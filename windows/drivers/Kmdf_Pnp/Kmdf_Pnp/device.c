#include "device.h"
#include "timer.h"
#include "queue.h"

#include <initguid.h>


// {3337A0D0-7993-450D-BA67-CE7B86FC9274}
DEFINE_GUID(DEVICE_INTERFACE ,
	0x3337a0d0, 0x7993, 0x450d, 0xba, 0x67, 0xce, 0x7b, 0x86, 0xfc, 0x92, 0x74);

#define IOCTL_TEST CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)


VOID
EvtIoInCallerContext(
	IN WDFDEVICE Device,
	IN WDFREQUEST Request
);


NTSTATUS
EvtDriverDeviceAdd(
	IN WDFDRIVER Driver,
	IN OUT PWDFDEVICE_INIT DeviceInit
) {
	UNREFERENCED_PARAMETER(Driver);

	NTSTATUS status = STATUS_SUCCESS;
	WDFDEVICE WdfDevice;
	PDEVICE_CONTEXT devContext = NULL;

	WDF_OBJECT_ATTRIBUTES DevcieObjAttr;
	WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&DevcieObjAttr, DEVICE_CONTEXT);

	status = WdfDeviceCreate(&DeviceInit, &DevcieObjAttr, &WdfDevice);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfDeviceCreate failed\n"));
		return status;
	}

	//
	// 设置Io回调之前的预处理函数
	// 对于大多数驱动，I/O请求在进入队列后，可能会在任意的线程上下文中被处理（比如系统的工作线程）。
	// EvtIoInCallerContext 给了驱动一个机会，在请求刚到达、还未被"转移"到其他线程前，就在发起者的原始环境中执行一些必要的预处理工作。
	// 一般用于<a href="https://learn.microsoft.com/zh-cn/windows-hardware/drivers/ddi/wdfdevice/nc-wdfdevice-evt_wdf_io_in_caller_context">METHOD_METHOD_NEITHER</a>
	WdfDeviceInitSetIoInCallerContextCallback(DeviceInit, EvtIoInCallerContext);


	devContext = DeviceGetContext(WdfDevice);

	// Wdf timer
	status = MyTimerCreate(WdfDevice, &devContext->Timer);
	if (!NT_SUCCESS(status)) {
		KdPrint(("MyTimerCreate failed, status: 0x%x\n", status));
		return status;
	}


	// Wdf queue
	status = MyQueueCreate(WdfDevice, &devContext->Queue, EvtIoRead, EvtIoWrite, EvtIoDeviceControl);
	if (!NT_SUCCESS(status)) {
		KdPrint(("MyQueueCreate failed, status: 0x%x\n", status));
		return status;
	}


	status = WdfDeviceCreateDeviceInterface(WdfDevice, &DEVICE_INTERFACE, NULL);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfDeviceCreateDeviceInterface failed\n"));
		return status;
	}

	KdPrint(("设备创建成功\n"));

	return status;
}


VOID
EvtIodEFAULT(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request
) {
	UNREFERENCED_PARAMETER(Queue);
	UNREFERENCED_PARAMETER(Request);

	WdfRequestComplete(Request, STATUS_SUCCESS);
	KdPrint(("EvtIodEFAULT called!\n"));
}

VOID
EvtIoRead(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t Length
) {
	UNREFERENCED_PARAMETER(Queue);
	UNREFERENCED_PARAMETER(Request);
	UNREFERENCED_PARAMETER(Length);

	WdfRequestComplete(Request, STATUS_SUCCESS);
	KdPrint(("EvtIoRead called!\n"));
}

VOID
EvtIoWrite(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t Length
) {
	UNREFERENCED_PARAMETER(Queue);
	UNREFERENCED_PARAMETER(Request);
	UNREFERENCED_PARAMETER(Length);

	WdfRequestComplete(Request, STATUS_SUCCESS);
	KdPrint(("EvtIoWrite called!\n"));
}

VOID
EvtIoDeviceControl(
	IN WDFQUEUE Queue,
	IN WDFREQUEST Request,
	IN size_t OutputBufferLength,
	IN size_t InputBufferLength,
	IN ULONG IoControlCode
) {
	UNREFERENCED_PARAMETER(Queue);
	UNREFERENCED_PARAMETER(OutputBufferLength);
	UNREFERENCED_PARAMETER(InputBufferLength);
	UNREFERENCED_PARAMETER(IoControlCode);

	NTSTATUS status = STATUS_SUCCESS;

	PVOID Buffer = NULL;
	size_t Length = 0;
	CHAR n = 0;

	WCHAR cNumbers[] = L"零一二三四五六七八九";

	switch (IoControlCode) {
	case IOCTL_TEST:
		status = WdfRequestRetrieveInputBuffer(Request, sizeof(CHAR), &Buffer, &Length);
		if (!NT_SUCCESS(status)) {
			WdfRequestComplete(Request, status);
			break;
		}

		if (Length < sizeof(CHAR)) {
			status = STATUS_INVALID_PARAMETER;
			WdfRequestComplete(Request, status);
			break;
		}

		n = *(PCHAR)Buffer;
		if ((n >= '0' && n <= '9')) {
			n = n - '0';
		} else {
			status = STATUS_INVALID_PARAMETER;
			WdfRequestComplete(Request, status);
			break;
		}

		status = WdfRequestRetrieveOutputBuffer(Request, sizeof(WCHAR), &Buffer, &Length);
		if (!NT_SUCCESS(status)) {
			WdfRequestComplete(Request, status);
			break;
		}

		if (Length < sizeof(WCHAR)) {
			status = STATUS_INVALID_PARAMETER;
			WdfRequestComplete(Request, status);
			break;
		}

		*(PWCHAR)Buffer = cNumbers[n];

		WdfRequestCompleteWithInformation(Request, status, sizeof(WCHAR));
		break;

	default:
		status = STATUS_INVALID_PARAMETER;
		WdfRequestComplete(Request, status);
		break;
	};
}

VOID
EvtIoInCallerContext(
	IN WDFDEVICE Device,
	IN WDFREQUEST Request
) {
	//WDF_REQUEST_PARAMETERS params;
	//WDF_REQUEST_PARAMETERS_INIT(&params);
	//WdfRequestGetParameters(Request, &params);

	//if (params.Type == WdfRequestTypeDeviceControl &&
	//	params.Parameters.DeviceIoControl.IoControlCode == IOCTL_NEITHER_CODE_XXX) {

	//	// 在调用者上下文中执行必要的Probe和Lock操作
	//	PVOID userBuffer = WdfRequestWdmGetIrp(Request)->UserBuffer;
	//	// ... 执行 ProbeForRead, MmProbeAndLockPages 等操作
	//}

	// 最终，将请求排入队列或直接完成
	WdfDeviceEnqueueRequest(Device, Request);
	// WdfRequestComplete(Request, STATUS_INVALID_PARAMETER);
}
