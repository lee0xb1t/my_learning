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
