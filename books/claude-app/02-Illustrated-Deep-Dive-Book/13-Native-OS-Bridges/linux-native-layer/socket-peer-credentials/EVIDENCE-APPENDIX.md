# 原创定位附录

样本：Claude Desktop Linux amd64 2.37337.1；文件大小10,026,272字节；SHA-256为 `c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`。源文件前后摘要一致；17个FDE范围与24项样本绑定静态检查通过，未加载或执行目标。

所有地址是样本 ELF linked VA，不是受 ASLR 影响的运行时地址。普通符号已剥离，本文的“工厂”“工作函数”“完成回调”是按实参、调用和表关联分配的分析标签，不冒充恢复的Rust源符号。反汇编从 `.eh_frame` FDE 起点解码，所选17段均未出现 `(bad)` 或 `.byte` 尾部截断。REA 6.5.0 的只读 file_headers Evidence 再次记录同一 digest 与 x86-64 ELF 格式。GNU readelf 提供 relocation/FDE，GNU objdump 提供逐段解码。REA 的 file_headers provider 同样是 GNU objdump，不是第二套独立解码引擎。

## NPB-01：名字与 callback

- 名字串起点：0x45367；仅用必要锚点 `connectUnixSocketSameUid`。
- 0x5b0dd1 取名字地址，0x5b0dd8 取 callback=0x5b0c80，0x5b0ded 间接调用 GOT 0x98d640；该 GOT 的 GLOB_DAT symbol 为 napi_create_function。
- 0x5b0d59 直接调用0x58fd60；0x58fd77指定完成回调0x6216e0。

## NPB-02：异步任务关联（结构证据）

以下是已解码的直接边或明确的表安装/relocation 边；两处“表 → 入口”是供调度器使用的静态关联，不是声称某次执行已通过间接调用。

- 0x58fed7 → 0x4cb7a0；0x4cb7d0 → 0x460360。
- 0x4603d3 取表0x974500；RELATIVE relocation的addend为0x4a7fb8。
- 0x4a7fb8跳转0x39a4c0；0x39a57b → 0x472150；0x4721a4 → 0x4047b0。
- 0x4048a9 → 0x4be6d0；0x4be75c → 0x452e20。
- 0x452e64 取表0x971300；RELATIVE relocation的addend为0x4a7ab8。
- 0x4a7ab8跳转0x33bdf0；0x33beaa → 0x4665e0；0x46663b → 0x52d890；0x52d8df → 0x4f0ff0。

不是用“所有调用都可达”的未经验证假设压平所有条件分支。异步运行时完整的投递/取消/异常派发仍为未闭合点。

## NPB-03：fd与凭据分支

- 工作函数FDE：0x4f0ff0..0x4f26df。
- 0x4f1036：socket，经GOT 0x98d290；实参1、0x80801、0。
- 0x4f1095：保存fd至栈+0xc；0x4f13ad载入r13d。
- 0x4f1400与0x4f1463：connect，经GOT 0x98d298；返回0分支到0x4f1ea3。
- 0x4f1ebf/0x4f1ede：fcntl，经GOT 0x98cb00；命令3与4；flags按0x7ffff7ff掩码处理；后一次非负才到0x4f21a8。
- 0x4f21b0..0x4f21e6：零初始化12字节buffer；optlen=12；getsockopt(fd,1,17,buffer,&optlen)，GOT 0x98d2b0。
- 0x4f21ec..0x4f21ee：返回0跳0x4f22c8；失败路径错误锚点地址0x3f626，对应必要前缀EPEERCRED。
- 0x4f22c8：geteuid，经GOT 0x98d2b8；0x4f22d2比较buffer+4的32位UID。
- 0x4f22d6：不相等跳0x4f22e8；错误格式锚点0x3b145，必要前缀EPERM。
- 0x4f22d8..0x4f22e3：结果+8写fd，结果+0写-1，跳0x4f237f，绕过close。
- 0x4f2376..0x4f2379：r13d作为close实参，经GOT 0x98c928；两种凭据拒绝汇入这里。下一指令进入返回段，未测试close的返回值。
- 另有0x4f118f的普通错误清理和0x4f26cb的unwind清理close。仅记录其存在，不把未穷尽异常路由等同于全生命周期证明。

## NPB-04：交付与JS错误分类

- 完成回调FDE：0x6216e0..0x621855。
- 0x6216fc比较结果首字段是否-1；成功分支在0x621724调用napi_create_int32（GOT 0x98d488），输入数字来自结果+8。
- 0x62179b调用napi_resolve_deferred（GOT 0x98d808）；错误汇合段0x62181b调用napi_reject_deferred（GOT 0x98d800）。转换或resolve失败也可进入错误段；fd清理没有在该回调里闭合。
- 已验证Linux JS wrapper SHA-256：d241a58d6a392b2074afb85713b9a7210cac511d068c30cb182552775e4ee512。
- UTF-8字节偏移2937955：调用native、等待fd、构造net.Socket的wrapper入口。
- UTF-8字节偏移2934799：错误规范化函数；相邻模式匹配消息首部的全大写错误码加冒号，写入code；标记名isNativeConnectError。

## ABI核验边界

Linux v6.12的公开内核socket定义提供ucred的三个32位字段；asm-generic socket选项提供1/17。分析机的x86-64 glibc头另以编译期assert交叉核对size=12与uid offset=4。该测试只做语法检查，无链接、无执行、更无目标加载。它验证解释采用的ABI布局，不证明产品构建用的头文件版本或其他架构布局。
