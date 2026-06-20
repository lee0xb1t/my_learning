// test_demo.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <windows.h>

__declspec(naked) void testVMP() {
    __asm {
        push 0
        push 0
        push 0
        push 0
        call MessageBoxA
        ret
    }
}

int main()
{
    //__asm int 3;

    testVMP();

    std::cout << "Hello World!\n";
}
