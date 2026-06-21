// test_demo.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <windows.h>

__declspec(naked) void testCall() {
    __asm {
        push ebp
        mov ebp, esp
        push [ebp+8]
        push [ebp+0xc]
        push 0
        push 0
        call MessageBoxA
        add esp, 0x10
        pop ebp
        ret
    }
}

__declspec(naked) void testVMP() {
    __asm {
        push ebp
        mov ebp, esp
        push 0
        push 0
        call testCall
        add esp, 8
        pop ebp
        ret
    }
}

int main()
{
    testVMP();

    std::cout << "Hello World!\n";
}
