import test from 'node:test';
import assert from 'node:assert/strict';
import {canonical,Rejected,createApprovalBoundary,VirtualFS,buildPlan,prepareSensitiveSave} from './guardrails.mjs';

test('stress: a non-enumerable array method cannot forge approved-content fingerprints',()=>{
  const args=['original'];let called=0;
  Object.defineProperty(args,'map',{value:()=>{called++;return ['"fixed"'];}});
  assert.throws(()=>canonical({args}),Rejected);assert.equal(called,0);
});
test('stress: array subclass hooks are rejected without running inherited code',()=>{
  let called=0;class Hooked extends Array {map(){called++;return ['"fixed"'];}}
  assert.throws(()=>canonical(new Hooked('original')),Rejected);assert.equal(called,0);
});
test('stress: hidden non-JSON array properties are rejected rather than left unbound',()=>{
  const array=['a'];Object.defineProperty(array,'authority',{value:'ignored',writable:true});
  assert.throws(()=>canonical(array),Rejected);
});
test('stress: NaN confirmation clock fails closed instead of issuing nonexpiring approval',()=>{
  const boundary=createApprovalBoundary({now:()=>NaN});
  assert.throws(()=>boundary.trustedUiConfirm({data:'synthetic'}),Rejected);
});
test('stress: NaN consumption clock rejects and consumes its one-use token',()=>{
  let now=0;const boundary=createApprovalBoundary({now:()=>now}),plan={data:'synthetic'};
  const token=boundary.trustedUiConfirm(plan);now=NaN;assert.throws(()=>boundary.consume(token,plan),Rejected);
  now=1;assert.throws(()=>boundary.consume(token,plan),Rejected);
});
test('stress: cloned token, cancelled token, failed attempt, and context replay stay rejected',()=>{
  const boundary=createApprovalBoundary({now:()=>0}),plan={destination:'/virtual'};
  const token=boundary.trustedUiConfirm(plan);assert.throws(()=>boundary.consume({...token},plan),Rejected);
  assert.equal(boundary.consume(token,plan).kind,'authorized-plan');
  const cancelled=boundary.trustedUiConfirm(plan);boundary.cancel(cancelled);assert.throws(()=>boundary.consume(cancelled,plan),Rejected);
  const changed=boundary.trustedUiConfirm(plan);assert.throws(()=>boundary.consume(changed,{destination:'/different'}),Rejected);assert.throws(()=>boundary.consume(changed,plan),Rejected);
  const old=boundary.trustedUiConfirm(plan);boundary.setContext({session:'new',generation:1,policyRevision:1});assert.throws(()=>boundary.consume(old,plan),Rejected);
});
test('stress: context input alias mutation cannot change the trusted stored scope',()=>{
  const boundary=createApprovalBoundary({now:()=>0}),context={session:'one',generation:1,policyRevision:1},plan={a:1};
  boundary.setContext(context);const token=boundary.trustedUiConfirm(plan);context.session='two';
  assert.equal(boundary.consume(token,plan).kind,'authorized-plan');
});
test('stress: consuming approval before a stale resource check does not restore approval',()=>{
  const fs=new VirtualFS(),boundary=createApprovalBoundary({now:()=>0});
  const plan=buildPlan(fs,'doccopy -- /input/a /output/a',[fs.grant('/input'),fs.grant('/output','write')]);
  const token=boundary.trustedUiConfirm(plan);fs.link('/output/a','/elsewhere');boundary.consume(token,plan);
  assert.throws(()=>fs.validateTicket(plan.resources[1]),Rejected);assert.throws(()=>boundary.consume(token,plan),Rejected);
});
test('stress: a missing secure adapter blocks the save plan without throwing',()=>{
  assert.deepEqual(prepareSensitiveSave('synthetic',undefined),{status:'blocked',reason:'secure backend unavailable'});
  assert.deepEqual(prepareSensitiveSave('synthetic',null),{status:'blocked',reason:'secure backend unavailable'});
});
test('stress: accepted virtual plans deeply detach path operands and resource identities',()=>{
  const fs=new VirtualFS(),grants=[fs.grant('/work','write')];const plan=buildPlan(fs,'doccopy -- /work/a /work/b',grants);
  assert.ok(Object.isFrozen(plan)&&Object.isFrozen(plan.command)&&Object.isFrozen(plan.command.paths)&&Object.isFrozen(plan.resources));
  assert.ok(plan.resources.every(Object.isFrozen));grants.length=0;
  assert.deepEqual(plan.resources.map(x=>x.canonicalPath),['/work/a','/work/b']);
});
test('stress: changing array arguments cannot reuse approval through a forged canonical map',()=>{
  const boundary=createApprovalBoundary({now:()=>0}),args=['original'],plan={args};
  Object.defineProperty(args,'map',{value:()=>['"constant"']});
  let token;try{token=boundary.trustedUiConfirm(plan);}catch(error){assert.ok(error instanceof Rejected);return;}
  args[0]='changed';assert.throws(()=>boundary.consume(token,plan),Rejected);
});
