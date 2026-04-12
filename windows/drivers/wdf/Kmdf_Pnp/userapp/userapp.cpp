// userapp.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <windows.h>
#include <initguid.h>
#include <setupapi.h>
#include <fcntl.h>
#include <io.h>

#include <iostream>

#include <cstdio>
#include <cstdlib>

#pragma comment(lib, "Setupapi.lib")


// {3337A0D0-7993-450D-BA67-CE7B86FC9274}
DEFINE_GUID(DEVICE_INTERFACE,
    0x3337a0d0, 0x7993, 0x450d, 0xba, 0x67, 0xce, 0x7b, 0x86, 0xfc, 0x92, 0x74);



#define IOCTL_TEST CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)


int func()
{
    HDEVINFO hDevInfo = SetupDiGetClassDevs(&DEVICE_INTERFACE, NULL, NULL, DIGCF_DEVICEINTERFACE | DIGCF_PRESENT);
    if (hDevInfo == NULL) {
        printf("hDevInfo is NULL\n");
        // system("pause");
        return -1;
    }

    SP_DEVICE_INTERFACE_DATA data = { 0 };
    data.cbSize = sizeof(data);

    BOOL ok = SetupDiEnumDeviceInterfaces(hDevInfo, NULL, &DEVICE_INTERFACE, 0, &data);
    if (!ok) {
        printf("SetupDiEnumDeviceInterfaces failed: 0x%x\n", GetLastError());
        // system("pause");
        return -1;
    }

    PSP_DEVICE_INTERFACE_DETAIL_DATA detailData = (PSP_DEVICE_INTERFACE_DETAIL_DATA)malloc(2048);
    if (detailData == NULL) {
        printf("allocate failed\n");
        // system("pause");
        return -1;
    }
    ZeroMemory(detailData, 2048);
    DWORD dataSize = 0;

    detailData->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);
    ok = SetupDiGetDeviceInterfaceDetail(hDevInfo, &data, detailData, 2048, &dataSize, NULL);
    if (!ok) {
        printf("SetupDiGetDeviceInterfaceDetail failed: 0x%x\n", GetLastError());
        // system("pause");
        return -1;
    }

    printf("dev path: %ws\n", detailData->DevicePath);

    


    //------------------------------------------------------

    HANDLE hDevice = CreateFile(
        detailData->DevicePath,
        GENERIC_READ | GENERIC_WRITE | GENERIC_EXECUTE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL);

    if (hDevice == INVALID_HANDLE_VALUE) {
        std::cout << "GetLastError: " << std::hex << GetLastError() << std::endl;
        // system("pause");
        return -1;
    }

    std::cout << "文件打开正常!\n";


    COMMTIMEOUTS Timeouts;
    Timeouts.ReadIntervalTimeout = 0;
    Timeouts.ReadTotalTimeoutMultiplier = 0;
    Timeouts.ReadTotalTimeoutConstant = 3000; // 2秒
    SetCommTimeouts(hDevice, &Timeouts);

    DWORD value = 0;
    DWORD valueOfBytesToRead = 0;
    BOOL isRead = ReadFile(hDevice, &value, sizeof(DWORD), 0, NULL);
    if (isRead) {
        std::cout << "文件读取正常!\n";
    }
    else {
        std::cout << "文件读取失败: " << std::hex << GetLastError() << std::endl;
    }

    DWORD valueOfBytesToWritten = 0;
    BOOL isWrite = WriteFile(hDevice, &value, sizeof(DWORD), 0, NULL);
    if (isWrite) {
        std::cout << "文件写入正常!\n";
    }
    else {
        std::cout << "文件写入失败: " << std::hex << GetLastError() << std::endl;
    }

    DWORD dwRet = 0;

    CHAR c = '5';
    size_t cLength = sizeof(CHAR);

    WCHAR outWC = L'T';
    size_t outWCLength = sizeof(WCHAR);

    ok = DeviceIoControl(hDevice, IOCTL_TEST, &c, cLength, &outWC, outWCLength, &dwRet, 0);
    if (ok) {
        printf("dwRet: %d\n", dwRet);
        printf("outWC 的十六进制: 0x%04X\n", outWC);
        //printf("转换完成: [%lc]\n", outWC);
        int oldmode = _setmode(_fileno(stdout), _O_U16TEXT);
        wprintf(L"转换完成(wprintf): [%c]\n", outWC);
        _setmode(_fileno(stdout), oldmode);

        char utf8Buffer[8] = { 0 };
        WideCharToMultiByte(CP_ACP, 0, &outWC, 1, utf8Buffer, sizeof(utf8Buffer), NULL, NULL);
        printf("编码: %s\n", utf8Buffer);

    } else {
        printf("字符转换失败:0x%x, dwRet: %d\n", GetLastError(), dwRet);
    }

    CloseHandle(hDevice);
}

int main() {
    while (1) {
        func();
    }
}


