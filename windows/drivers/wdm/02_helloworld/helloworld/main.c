#include <wdm.h>


typedef struct _MY_DEVICE_DATA {
    ULONG SomeData;
} MY_DEVICE_DATA, * PMY_DEVICE_DATA;

#define DEVICE_NAME     L"\\Device\\TestDevice"
#define SYM_NAME        L"\\??\\TestDevice"

#define TestCtlCode CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define HelloCtlCode CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)


VOID DriverUnload(PDRIVER_OBJECT DrvObj) {
    UNREFERENCED_PARAMETER(DrvObj);

    // 删除符号链接和设备
    UNICODE_STRING usSymLinkName = RTL_CONSTANT_STRING(SYM_NAME);
    IoDeleteSymbolicLink(&usSymLinkName);

    // 删除设备对象
    if (DrvObj->DeviceObject) {
        IoDeleteDevice(DrvObj->DeviceObject);
    }

    KdPrint(("Driver Unload!\n"));
}

NTSTATUS
MyDeviceControl(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
) {
    NTSTATUS status = STATUS_SUCCESS;
    PIO_STACK_LOCATION irpStack = IoGetCurrentIrpStackLocation(Irp);
    ULONG ioControlCode = irpStack->Parameters.DeviceIoControl.IoControlCode;
    PVOID inputBuffer = Irp->AssociatedIrp.SystemBuffer;
    PVOID outputBuffer = Irp->AssociatedIrp.SystemBuffer;
    ULONG inputBufferLength = irpStack->Parameters.DeviceIoControl.InputBufferLength;
    ULONG outputBufferLength = irpStack->Parameters.DeviceIoControl.OutputBufferLength;
    ULONG bytesReturned = 0;

    // 获取设备扩展数据
    PMY_DEVICE_DATA deviceData = (PMY_DEVICE_DATA)DeviceObject->DeviceExtension;

    KdPrint(("MyDeviceControl called, IOCTL: 0x%X\n", ioControlCode));

    switch (ioControlCode) {
    case TestCtlCode:  // 自定义IOCTL示例
        if (inputBuffer != NULL && inputBufferLength >= sizeof(ULONG)) {
            // 读取输入数据
            deviceData->SomeData = *(PULONG)inputBuffer;
            KdPrint(("Received data: 0x%X\n", deviceData->SomeData));
            bytesReturned = 0;
            status = STATUS_SUCCESS;
        }
        else {
            status = STATUS_INVALID_PARAMETER;
        }
        break;

    case HelloCtlCode:  // 读取数据示例
        if (outputBuffer != NULL && outputBufferLength >= sizeof(ULONG)) {
            *(PULONG)outputBuffer = deviceData->SomeData;
            bytesReturned = sizeof(ULONG);
            status = STATUS_SUCCESS;
        }
        else {
            status = STATUS_BUFFER_TOO_SMALL;
        }
        break;

    default:
        status = STATUS_INVALID_DEVICE_REQUEST;
        break;
    }

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = bytesReturned;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

NTSTATUS
MyCreateClose(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
) {
    UNREFERENCED_PARAMETER(DeviceObject);

    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return STATUS_SUCCESS;
}

NTSTATUS DriverEntry(PDRIVER_OBJECT DrvObj, PUNICODE_STRING RegistryPath) {
    UNREFERENCED_PARAMETER(RegistryPath);

    NTSTATUS status = STATUS_SUCCESS;
    UNICODE_STRING usDeviceName = RTL_CONSTANT_STRING(DEVICE_NAME);
    UNICODE_STRING usSymLinkName = RTL_CONSTANT_STRING(SYM_NAME);
    PDEVICE_OBJECT DevObj = NULL;
    PMY_DEVICE_DATA deviceData = NULL;

    KdPrint(("DriverEntry: Starting driver initialization...\n"));

    // 设置卸载函数
    DrvObj->DriverUnload = DriverUnload;

    // 设置IRP处理函数
    DrvObj->MajorFunction[IRP_MJ_CREATE] = MyCreateClose;
    DrvObj->MajorFunction[IRP_MJ_CLOSE] = MyCreateClose;
    DrvObj->MajorFunction[IRP_MJ_DEVICE_CONTROL] = MyDeviceControl;

    // 创建设备对象
    status = IoCreateDevice(DrvObj,
        sizeof(MY_DEVICE_DATA),
        &usDeviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &DevObj);

    if (!NT_SUCCESS(status)) {
        KdPrint(("Device create failed! Status: 0x%X\n", status));
        return status;
    }

    KdPrint(("Device created successfully\n"));
    KdPrint(("Device flags before clearing: 0x%X\n", DevObj->Flags));

    // 初始化设备扩展数据
    deviceData = (PMY_DEVICE_DATA)DevObj->DeviceExtension;
    deviceData->SomeData = 0xabcd;

    // 设置设备缓冲区方式
    DevObj->Flags |= DO_BUFFERED_IO;

    // 重要：清除DO_DEVICE_INITIALIZING标志
    DevObj->Flags &= ~DO_DEVICE_INITIALIZING;

    KdPrint(("Device flags after clearing DO_DEVICE_INITIALIZING: 0x%X\n", DevObj->Flags));

    // 创建符号链接
    status = IoCreateSymbolicLink(&usSymLinkName, &usDeviceName);
    if (!NT_SUCCESS(status)) {
        KdPrint(("Symbolic link creation failed! Status: 0x%X\n", status));
        // 注意：这里不需要重新设置DO_DEVICE_INITIALIZING标志
        // 直接删除设备即可
        IoDeleteDevice(DevObj);
        return status;
    }

    KdPrint(("Symbolic link created successfully\n"));
    KdPrint(("DriverEntry: Driver loaded successfully!\n"));
    KdPrint(("Device Name: %wZ\n", &usDeviceName));
    KdPrint(("Symbolic Link: %wZ\n", &usSymLinkName));
    KdPrint(("Device Object: 0x%p\n", DevObj));

    return STATUS_SUCCESS;
}