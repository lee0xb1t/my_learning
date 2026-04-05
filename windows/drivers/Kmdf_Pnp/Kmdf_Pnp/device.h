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
} DEVICE_CONTEXT, * PDEVICE_CONTEXT;
WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, DeviceGetContext)


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