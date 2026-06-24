VMP3.5可能将取指令解析并执行分布到了不同的BBL中，有几个BBL的功能是相同的

比如BBL99、BBL63、BBL103、BBL87的功能都是：
1. esi-=1
2. edx = byte[esi]
3. esi-=4
4. eax = dword[esi]

仅观察graph很难提取出真正的vm_handler

--------------------------------------------------------------
不同虚拟机跳转：
.vmp0:0002DD79                 mov     esi, edi        ; edi交换到esi，实现不同虚拟机使用不同寄存器
.vmp0:000337D2                 lea     edi, loc_337D2  ; 切换edi指向的私有寄存器

不同虚拟机之间调用会切换寄存器作用，包括但不限于 esi edi ebp

