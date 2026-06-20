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

-> 虚拟机程序地址: 0xF4B9B9

vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8

vmHandler: handler addr=0xF41012, handler index=0x7A  # 平衡栈

                                                      # vmmPushEBP（这里有一个隐含的映射关系，这个关系和上面vmEnter是恢复vmp环境的顺序有关，比如vreg1 -> ebp，但是不确定vreg1是否始终隐射到ebp）
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD vreg_1 (ebp)

                                                      # vmmMovVSPToReg reg
vmHandler: handler addr=0xF4BCCE, handler index=0xC9  # vmmPushHostStack
vmHandler: handler addr=0xF4BB25, handler index=0xE8  # vmmPopDWORD vreg_f

vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushBYTE imm (0)
vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushBYTE imm (0)

                                                      # vmmAdd 0xB40000, 0x40BEFA (calc call ptr)
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD vreg_1 (0xB40000 -> offset)
vmHandler: handler addr=0xF4B433, handler index=0x76  # vmmPushDWORD imm (0x40BEFA)
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax

vmHandler: handler addr=0xF4B433, handler index=0x66  # vmmPushDWORD imm (0x40BE15)

                                                      # vmmAdd 0xB40000, 0040B9B9 (calc call ptr)
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPopDWORD vreg_c (0xB40000)
vmHandler: handler addr=0xF4B433, handler index=0x66  # vmmPushDWORD imm (0040B9B9)
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax

vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushDWORD reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD reg

vmHandler: handler addr=0xF4BB7E, handler index=0x81  # vmmExit

                                                      # vmmExit之后会进入新的字节码，新字节码地址在上一个字节码执行时，已经push到栈中
                                                      # 调用虚拟机函数与调用非虚拟机函数类似，都会通过vmExit跳转
                                                      # TODO: 调转指令待验证


-> 虚拟机程序地址: 0xF4B9B9
   字节码地址:  0x40BE15

                                                      # vmmEnter
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8

vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushDWORD vreg_1 (ebp)

                                                      # vmmMoveVSPToReg
vmHandler: handler addr=0xF4BCCE, handler index=0xE4  # vmmPushHostStack
vmHandler: handler addr=0xF4BB25, handler index=0xE8  # vmmPopReg reg_a


--------------------------------------------------------------------------------------------
                                                      # vmmGetAndPush (vmmAdd(8, 0x8FFDF0))

                                                      # vmmAdd 8, 0x8FFDF0
vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushByte imm (8)
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg_a (0x8FFDF0)
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax

vmHandler: handler addr=0xF4BAD5, handler index=0x2A  # vmmGetAndPushVal
--------------------------------------------------------------------------------------------


--------------------------------------------------------------------------------------------
                                                      # vmmGetAndPush (vmmAdd(8, 0x8FFDF0))

                                                      # vmmAdd 0xF4B57F, 0xc
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg_A (0xF4B57F)
vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushByte imm (0xc)
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax

vmHandler: handler addr=0xF4BAD5, handler index=0x2A  # vmmGetAndPushVal
--------------------------------------------------------------------------------------------



vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushByte imm (0)
vmHandler: handler addr=0xF4B98B, handler index=0xEC  # vmmPushByte imm (0)

                                                      # vmmAdd 0x40BEEE, 0xB40000
vmHandler: handler addr=0xF4B433, handler index=0x66  # vmmPushDWORD imm
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg_8
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax


--------------------------------------------------------------------------------------------
                                                      # vmmGetAndPush (vmmAdd(0xB40000, 0x403058))

                                                      # vmmAdd 0xB40000, 0x403058
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg_8 (0xB40000)
vmHandler: handler addr=0xF4B433, handler index=0x76  # vmmPushDWORD imm (0x403058)
vmHandler: handler addr=0xF4BB5A, handler index=0x05  # vmmAddHostStackWithHostEax

vmHandler: handler addr=0xF460CF, handler index=0x12  # vmmGetAndPushVal
--------------------------------------------------------------------------------------------

上方代码执行完之后的栈
008FFDD8  75A07F60  user32.MessageBoxA
008FFDDC  00F4BEEE  test_demo.vmp.__dyn_tls_init_callback+7B22

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0xA8  # vmmPushReg reg
vmHandler: handler addr=0xF4B941, handler index=0x4D  # vmmPushReg reg

vmHandler: handler addr=0xF4BB7E, handler index=0x81  # vmmExit 这里应该调用MessageBox

vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4BB25, handler index=0xE8

vmHandler: handler addr=0xF4B98B, handler index=0xEC
vmHandler: handler addr=0xF4B98B, handler index=0xEC
vmHandler: handler addr=0xF4BCCE, handler index=0xE4
vmHandler: handler addr=0xF4BB5A, handler index=0x05
vmHandler: handler addr=0xF4BADE, handler index=0x8F
vmHandler: handler addr=0xF4B86F, handler index=0xBC
vmHandler: handler addr=0xF4BD86, handler index=0xFD
vmHandler: handler addr=0xF4BCCE, handler index=0xE4
vmHandler: handler addr=0xF4BC0B, handler index=0x1B
vmHandler: handler addr=0xF4BBF5, handler index=0x7C
vmHandler: handler addr=0xF4BBF5, handler index=0x7C
vmHandler: handler addr=0xF4BACA, handler index=0xF7
vmHandler: handler addr=0xF460FA, handler index=0xC3
vmHandler: handler addr=0xF4613F, handler index=0xC1
vmHandler: handler addr=0xF4BB25, handler index=0xE8
vmHandler: handler addr=0xF4B941, handler index=0x4D
vmHandler: handler addr=0xF4B941, handler index=0x4D
vmHandler: handler addr=0xF4B941, handler index=0x4D
vmHandler: handler addr=0xF4B941, handler index=0xA8
vmHandler: handler addr=0xF4B941, handler index=0x4D
vmHandler: handler addr=0xF4B941, handler index=0xA8
vmHandler: handler addr=0xF4B941, handler index=0xA8
vmHandler: handler addr=0xF4B941, handler index=0xA8
vmHandler: handler addr=0xF4B941, handler index=0xA8
vmHandler: handler addr=0xF4B941, handler index=0x4D
vmHandler: handler addr=0xF4BB7E, handler index=0x81
```
