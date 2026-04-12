#ifndef QUEUE_H
#define QUEUE_H

#include <ntddk.h>
#include <wdf.h>


NTSTATUS MyQueueCreate(
	IN WDFDEVICE WdfDevice, 
	OUT WDFQUEUE* WdfQueue,
	IN PFN_WDF_IO_QUEUE_IO_READ                    EvtIoRead,
	IN PFN_WDF_IO_QUEUE_IO_WRITE                   EvtIoWrite,
	IN PFN_WDF_IO_QUEUE_IO_DEVICE_CONTROL          EvtIoDeviceControl);


#endif