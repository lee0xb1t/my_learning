#

* VMP 指令流程：

0x40BB20: vmpPop n

0x40BA4E: vmpPopToEcx 调用这个指令可能只是为了平衡host栈

0x406104: vmpDefine

0x40BB20: vmpPop 0

0x40BAD2: vmpPush n
