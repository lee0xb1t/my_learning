// test_demo.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <windows.h>

int add(int a, int b) {
    return a + b;
}

int main()
{
    int ret = add(4, 6);
    MessageBoxA(0, 0, 0, 0);

    std::cout << "Hello World!\n";
    return ret;
}
