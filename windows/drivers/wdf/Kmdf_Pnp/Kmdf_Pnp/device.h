#ifndef DEVICE_H
#define DEVICE_H

#include <ntddk.h>
#include <wdf.h>


typedef struct _DEVICE_CONTEXT {
	WDFTIMER Timer;
	WDFQUEUE Queue;

	PFN_WDF_IO_QUEUE_IO_READ                    EvtIoRead;
	PFN_WDF_IO_QUEUE_IO_WRITE                   EvtIoWrite;
	PFN_WDF_IO_QUEUE_IO_DEVICE_CONTROL          EvtIoDeviceControl;

    // 基础设备信息
    WDFDEVICE Device;

    // 硬件资源
    PHYSICAL_ADDRESS MmioBase;      // MMIO 物理地址
    ULONG MmioLength;               // MMIO 长度
    PVOID MmioVirtual;              // MMIO 虚拟地址（映射后）

    // 中断资源
    ULONG InterruptVector;          // 中断向量
    ULONG InterruptLevel;           // 中断级别
    WDFINTERRUPT Interrupt;         // WDF 中断对象
} DEVICE_CONTEXT, * PDEVICE_CONTEXT;
WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, DeviceGetContext)


//----------------------------------
typedef struct _INTERRUPT_CONTEXT {
    ULONG v;
}INTERRUPT_CONTEXT, *PINTERRUPT_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(INTERRUPT_CONTEXT, InterruptGetContext)


//----------------------------------
VOID
EvtIoRead(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t Length
);

VOID
EvtIoWrite(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t Length
);

VOID
EvtIoDeviceControl(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t OutputBufferLength,
	IN size_t InputBufferLength,
	IN ULONG IoControlCode
);


//----------------------------------
NTSTATUS
EvtDriverDeviceAdd(
	IN WDFDRIVER Driver,
	IN OUT PWDFDEVICE_INIT DeviceInit
);


#endif