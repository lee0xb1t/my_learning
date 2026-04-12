#include <windows.h>
#include <stdio.h>

#define TestCtlCode     CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define HelloCtlCode    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define DEVICE_PATH     L"\\\\.\\TestDevice"

int main()
{
    HANDLE hDevice;
    DWORD bytesReturned;
    ULONG writeData = 0x12345678;
    ULONG readData = 0;

    printf("Opening device...\n");
    hDevice = CreateFileW(DEVICE_PATH, GENERIC_READ | GENERIC_WRITE,
        0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hDevice == INVALID_HANDLE_VALUE) {
        printf("Failed to open device! Error: %d\n", GetLastError());
        return 1;
    }
    printf("Device opened successfully!\n");

    // 读取初始值
    printf("\nReading initial value...\n");
    if (DeviceIoControl(hDevice, HelloCtlCode, NULL, 0,
        &readData, sizeof(readData), &bytesReturned, NULL)) {
        printf("Initial value: 0x%X (%d)\n", readData, readData);
    }

    // 写入新值
    printf("\nWriting new value: 0x%X\n", writeData);
    if (DeviceIoControl(hDevice, TestCtlCode, &writeData, sizeof(writeData),
        NULL, 0, &bytesReturned, NULL)) {
        printf("Write successful!\n");
    }

    // 读取新值
    printf("\nReading back value...\n");
    if (DeviceIoControl(hDevice, HelloCtlCode, NULL, 0,
        &readData, sizeof(readData), &bytesReturned, NULL)) {
        printf("New value: 0x%X (%d)\n", readData, readData);
    }

    CloseHandle(hDevice);
    printf("\nTest completed. Press any key to exit...\n");
    getchar();
    return 0;
}