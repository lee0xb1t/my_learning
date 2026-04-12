#include "queue.h"
#include "device.h"


VOID
EvtIoCanceledOnQueue(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request
);

NTSTATUS MyQueueCreate(
	IN WDFDEVICE WdfDevice,
	OUT WDFQUEUE* WdfQueue,
	IN PFN_WDF_IO_QUEUE_IO_READ                    EvtIoRead,
	IN PFN_WDF_IO_QUEUE_IO_WRITE                   EvtIoWrite,
	IN PFN_WDF_IO_QUEUE_IO_DEVICE_CONTROL          EvtIoDeviceControl)
{
	NTSTATUS status = STATUS_SUCCESS;
	WDF_IO_QUEUE_CONFIG IoQueueConfig;
	PDEVICE_CONTEXT devContext = NULL;

	if (WdfQueue == NULL) {
		return STATUS_INVALID_PARAMETER;
	}

	WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&IoQueueConfig, WdfIoQueueDispatchManual);
	//IoQueueConfig.PowerManaged = WdfFalse;
	IoQueueConfig.EvtIoCanceledOnQueue = EvtIoCanceledOnQueue;

	if (IoQueueConfig.DispatchType != WdfIoQueueDispatchManual) {
		IoQueueConfig.EvtIoRead = EvtIoRead;
		IoQueueConfig.EvtIoWrite = EvtIoWrite;
		IoQueueConfig.EvtIoDeviceControl = EvtIoDeviceControl;
	}

	status = WdfIoQueueCreate(WdfDevice, &IoQueueConfig, WDF_NO_OBJECT_ATTRIBUTES, WdfQueue);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfIoQueueCreate failed\n"));
		return status;
	}

	devContext = DeviceGetContext(WdfDevice);

	if (devContext == NULL) {
		KdPrint(("DeviceGetContext failed!, devContextis null\n"));
		return STATUS_CONTEXT_MISMATCH;
	}

	if (IoQueueConfig.DispatchType == WdfIoQueueDispatchManual) {
		devContext->EvtIoRead = EvtIoRead;
		devContext->EvtIoWrite = EvtIoWrite;
		devContext->EvtIoDeviceControl = EvtIoDeviceControl;
	}

	return status;
}

VOID
EvtIoCanceledOnQueue(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request
) {
	PDEVICE_CONTEXT devContext = NULL;

	// Finish request
	WdfRequestComplete(Request, STATUS_CANCELLED);

	// Stop timer
	WDFDEVICE WdfDevice = WdfIoQueueGetDevice(Queue);
	devContext = DeviceGetContext(WdfDevice);
	WdfTimerStop(devContext->Timer, FALSE);
}