#include "timer.h"
#include "device.h"
#include "queue.h"


VOID
WdfTimerFunc(
	IN WDFTIMER Timer
);

NTSTATUS MyTimerCreate(IN WDFDEVICE WdfDevice, OUT WDFTIMER* WdfTimer) {
	NTSTATUS status = STATUS_SUCCESS;
	WDF_TIMER_CONFIG TimerConfig;
	WDF_OBJECT_ATTRIBUTES TimerObjAttr;

	if (WdfTimer == NULL) {
		return STATUS_INVALID_PARAMETER;
	}

	WDF_OBJECT_ATTRIBUTES_INIT(&TimerObjAttr);
	TimerObjAttr.ParentObject = WdfDevice;

	WDF_TIMER_CONFIG_INIT_PERIODIC(&TimerConfig, WdfTimerFunc, 100);

	status = WdfTimerCreate(&TimerConfig, &TimerObjAttr, WdfTimer);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfTimerCreate failed!, status:0x%x\n", status));
		return status;
	}

	BOOLEAN ok = WdfTimerStart(*WdfTimer, 100);
	if (ok) {
		KdPrint(("WdfTimer is already exists (ignored)\n"));
	}

	return status;
}

VOID
WdfTimerFunc(
	IN WDFTIMER Timer
) {
	NTSTATUS status = STATUS_SUCCESS;
	WDFDEVICE WdfDevice;
	PDEVICE_CONTEXT devContext = NULL;

	WDFREQUEST WdfRequest;
	WDF_REQUEST_PARAMETERS RequestParams;

	WdfDevice = (WDFDEVICE)WdfTimerGetParentObject(Timer);
	devContext = DeviceGetContext(WdfDevice);

	if (devContext == NULL) {
		KdPrint(("DeviceGetContext failed!, devContextis null\n"));
		return;
	}

	status = WdfIoQueueRetrieveNextRequest(devContext->Queue, &WdfRequest);
	if (!NT_SUCCESS(status)) {
		//KdPrint(("Get next request failed (ignored), status:0x%x\n", status));
		return;
	}

	WDF_REQUEST_PARAMETERS_INIT(&RequestParams);
	WdfRequestGetParameters(WdfRequest, &RequestParams);


	switch (RequestParams.Type) {
	case WdfRequestTypeRead:
		devContext->EvtIoRead(devContext->Queue, WdfRequest, RequestParams.Parameters.Read.Length);
		break;
	case WdfRequestTypeWrite:
		devContext->EvtIoWrite(devContext->Queue, WdfRequest, RequestParams.Parameters.Write.Length);
		break;
	case WdfRequestTypeDeviceControl:
		devContext->EvtIoDeviceControl(devContext->Queue, WdfRequest, 
			RequestParams.Parameters.DeviceIoControl.OutputBufferLength, 
			RequestParams.Parameters.DeviceIoControl.InputBufferLength,
			RequestParams.Parameters.DeviceIoControl.IoControlCode
			);
		break;
	default:
		WdfRequestComplete(WdfRequest, STATUS_INVALID_DEVICE_REQUEST);
		break;
	}
}
