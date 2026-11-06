#!/usr/bin/env python3
"""Compile unchanged upstream jailer.go with local Go stub dependencies.

Tests only constructor selection, UID/GID rejection, and config forwarding.
No runc, KVM, Firecracker, network, mount, namespaces or permission changes.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

EXPECTED = "19af4ad2dce6eb62f9cf64be06a475de09be5502"
FILES = {
    "go.mod": '''module github.com/firecracker-microvm/firecracker-containerd
go 1.19
require (
 github.com/sirupsen/logrus v0.0.0
 github.com/firecracker-microvm/firecracker-go-sdk v0.0.0
)
replace github.com/sirupsen/logrus => ./stub-logrus
replace github.com/firecracker-microvm/firecracker-go-sdk => ./stub-sdk
''',
    "stub-logrus/go.mod": "module github.com/sirupsen/logrus\ngo 1.19\n",
    "stub-logrus/logrus.go": '''package logrus
type Entry struct{}
func (e *Entry) WithField(string, interface{}) *Entry { return e }
''',
    "stub-sdk/go.mod": "module github.com/firecracker-microvm/firecracker-go-sdk\ngo 1.19\n",
    "stub-sdk/sdk.go": '''package firecracker
type Config struct{}
type Opt struct{}
''',
    "config/config.go": '''package config
type Config struct { JailerConfig JailerConfig }
type JailerConfig struct { RuncBinaryPath, RuncConfigPath string }
''',
    "internal/vm/vm.go": "package vm\ntype Dir string\n",
    "proto/proto.go": '''package proto
type DriveExposePolicy int
type FirecrackerDriveMount struct{}
type JailerConfig struct {
 UID, GID uint32
 CPUs, Mems, CgroupPath string
 DriveExposePolicy DriveExposePolicy
}
type CreateVMRequest struct {
 JailerConfig *JailerConfig
 DriveMounts []*FirecrackerDriveMount
}
''',
    "runtime/jailer_test.go": '''package main
import (
 "context"
 "os"
 "path/filepath"
 "testing"
 "github.com/sirupsen/logrus"
 "github.com/firecracker-microvm/firecracker-containerd/config"
 "github.com/firecracker-microvm/firecracker-containerd/internal/vm"
 "github.com/firecracker-microvm/firecracker-containerd/proto"
 firecracker "github.com/firecracker-microvm/firecracker-go-sdk"
)
type service struct { shimDir vm.Dir; config *config.Config; vmID string }
type runcJailerConfig struct {
 OCIBundlePath, RuncBinPath, RuncConfigPath string
 UID, GID uint32
 CPUs, Mems, CgroupPath string
 DriveExposePolicy proto.DriveExposePolicy
}
type mockJailer struct { kind string; cfg runcJailerConfig }
func (*mockJailer) BuildJailedMachine(*config.Config,*firecracker.Config,string)([]firecracker.Opt,error){return nil,nil}
func (*mockJailer) ExposeFileToJail(string)error{return nil}
func (*mockJailer) JailPath()vm.Dir{return vm.Dir("synthetic")}
func (*mockJailer) StubDrivesOptions()[]FileOpt{return nil}
func (*mockJailer) Stop(bool)error{return nil}
func (*mockJailer) Close()error{return nil}
func newNoopJailer(context.Context,*logrus.Entry,vm.Dir) jailer {return &mockJailer{kind:"noop"}}
func newRuncJailer(_ context.Context,_ *logrus.Entry,_ string,c runcJailerConfig,_ []*proto.FirecrackerDriveMount)(jailer,error){return &mockJailer{kind:"runc",cfg:c},nil}
func fixture()*service{
 return &service{config:&config.Config{JailerConfig:config.JailerConfig{RuncBinaryPath:"synthetic-runc",RuncConfigPath:"synthetic.json"}},vmID:"synthetic-vm"}
}
func TestAbsentJailerConfigSelectsNoop(t *testing.T){
 for _,req:=range []*proto.CreateVMRequest{nil,{}}{
  p:=filepath.Join(t.TempDir(),"not-created")
  j,err:=newJailer(context.Background(),&logrus.Entry{},p,fixture(),req)
  if err!=nil || j.(*mockJailer).kind!="noop" { t.Fatalf("unexpected selection: %v %v",j,err) }
  if _,err:=os.Stat(p);!os.IsNotExist(err){t.Fatal("noop should not create bundle")}
 }
}
func TestZeroUIDOrGIDRejectedBeforeFilesystemSetup(t *testing.T){
 for _,ids:=range [][2]uint32{{0,1},{1,0},{0,0}}{
  p:=filepath.Join(t.TempDir(),"not-created")
  j,err:=newJailer(context.Background(),&logrus.Entry{},p,fixture(),&proto.CreateVMRequest{JailerConfig:&proto.JailerConfig{UID:ids[0],GID:ids[1]}})
  if err==nil || j!=nil {t.Fatalf("expected rejection for %v",ids)}
  if _,err:=os.Stat(p);!os.IsNotExist(err){t.Fatal("reject should precede bundle creation")}
 }
}
func TestExplicitConfigSelectsRuncAndForwardsPolicy(t *testing.T){
 p:=filepath.Join(t.TempDir(),"bundle")
 req:=&proto.CreateVMRequest{JailerConfig:&proto.JailerConfig{UID:1001,GID:1002,CPUs:"2-3",Mems:"0",CgroupPath:"/synthetic",DriveExposePolicy:1}}
 j,err:=newJailer(context.Background(),&logrus.Entry{},p,fixture(),req)
 if err!=nil{t.Fatal(err)}
 m:=j.(*mockJailer)
 if m.kind!="runc" || m.cfg.UID!=1001 || m.cfg.GID!=1002 || m.cfg.CPUs!="2-3" || m.cfg.Mems!="0" || m.cfg.DriveExposePolicy!=1 || m.cfg.RuncBinPath!="synthetic-runc" {t.Fatalf("bad forwarding: %+v",m)}
 if info,err:=os.Stat(p);err!=nil || !info.IsDir(){t.Fatalf("missing owned temporary bundle: %v",err)}
}
''',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("upstream_jailer", type=Path)
    args = parser.parse_args()
    source = args.upstream_jailer.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    if blob != EXPECTED:
        raise SystemExit(f"Refusing mismatched upstream file: {blob}")
    go = shutil.which("go")
    if not go:
        raise SystemExit("Preinstalled Go required; this script never installs it.")
    print(json.dumps({"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "source_git_blob": blob, "source_bytes": len(source),
                      "source_sha256": hashlib.sha256(source).hexdigest(),
                      "scope": "unchanged Go selector with local stub factories; no VMM"}, indent=2), flush=True)
    with tempfile.TemporaryDirectory(prefix="jailer-selector-mock-") as tmp:
        root = Path(tmp)
        for name, content in FILES.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        (root / "runtime/jailer.go").write_bytes(source)
        env = {"PATH": os.environ.get("PATH", ""), "HOME": tmp,
               "GOPROXY": "off", "GOSUMDB": "off", "GOTOOLCHAIN": "local",
               "GOCACHE": str(root / "go-cache"), "GOMODCACHE": str(root / "go-mod-cache"),
               "GOPATH": str(root / "go-path"), "CGO_ENABLED": "0", "TMPDIR": tmp}
        probe = subprocess.run([go, "version"], env=env, text=True, capture_output=True, timeout=10)
        if probe.returncode or not probe.stdout.startswith("go version go"):
            raise SystemExit("BLOCKED: PATH go is not a validated Go toolchain. "
                             + (probe.stderr or probe.stdout).strip())
        print(probe.stdout.strip(), flush=True)
        result = subprocess.run([go, "test", "-mod=mod", "-count=1", "-v", "./runtime"],
                                cwd=root, env=env, timeout=180)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
