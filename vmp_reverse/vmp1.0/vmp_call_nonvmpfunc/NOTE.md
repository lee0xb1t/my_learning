# VMP Call分析

* VMP 指令流程：

0x40BB20: vmpPop n

0x40BA4E: vmpPopToEcx 调用这个指令可能只是为了平衡host栈

0x406104: vmpDefine

0x40BB20: vmpPop 0

0x40BAD2: vmpPush n

## VMP Stack

**VMP栈是基于Host栈实现的**，以下代码是vmpPush指令的实现：

```asm
.vmp0:00406015 sub_406015      proc near               ; DATA XREF: .vmp1:0040B87D↓o
.vmp0:00406015                                         ; .vmp1:0040B9A5↓o
.vmp0:00406015                 lodsb
.vmp0:00406016                 cbw
.vmp0:00406018                 cwde
.vmp0:00406019                 push    eax
.vmp0:0040601A                 jmp     loc_40BC33
.vmp0:0040601A sub_406015      endp
```

## VMP Call

```text
                                                       # vmpEnvSave
vmHanlder: handler addr=0x9860F8,  handler index=0xA9  # vmpPopReg reg
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9

vmHanlder: handler addr=0x98BAE8,  handler index=0xBE  # 平衡栈
                                                       # 压入MessageBox的参数
vmHanlder: handler addr=0x986015,  handler index=0xD4  # vmpPush
vmHanlder: handler addr=0x986015,  handler index=0xD4
vmHanlder: handler addr=0x986015,  handler index=0xD4
vmHanlder: handler addr=0x986015,  handler index=0xD4

                                                       # vmpPrepareCall
                                                       # 1. 压入Call之后的返回值，因为外部Call调用完成后还要返回VMP继续执行，所以压入的也是`vmpEnter`地址
                                                       # 2. 压入调用地址
                                                       # 3. 退出VMP

                                                       # vmpPushRet
vmHanlder: handler addr=0x9860E5,  handler index=0x83  # vmpPushDWORD imm
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE  # vmpPushDWORD reg
vmHanlder: handler addr=0x98B44F,  handler index=0x72  # vmpAdd ^-> imm=imm+reg

                                                       # vmpPushCallPtr
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE  # vmpPushDWORD reg
vmHanlder: handler addr=0x9860E5,  handler index=0x83  # vmpPushDWORD imm
vmHanlder: handler addr=0x98B44F,  handler index=0x72  # vmpAdd ^-> reg=reg+imm
vmHanlder: handler addr=0x98B50C,  handler index=0x96  # vmpGetCallPtr

                                                       # vmpEnvRestore
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE  # vmpPushReg reg
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE

                                                      # VMP通过vmExit的方式调用Call，Call地址在之前已经压入栈，
                                                      # 而函数调用后的返回地址是vmEnter，也就是Call调用之后再次进入VMP
vmHanlder: handler addr=0x98BABE,  handler index=0xA2 # vmpExit

vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9
vmHanlder: handler addr=0x9860F8,  handler index=0xA9

                                                      # 全部完成后执行vmExit
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BC5D,  handler index=0xFE
vmHanlder: handler addr=0x98BABE,  handler index=0xA2
```
