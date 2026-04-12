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
EvtDevicePrepareHardware(
	IN WDFDEVICE Device,
	IN WDFCMRESLIST ResourcesRaw,
	IN WDFCMRESLIST ResourcesTranslated
);

NTSTATUS
EvtDeviceReleaseHardware(
	IN WDFDEVICE Device,
	IN WDFCMRESLIST ResourcesTranslated
);


NTSTATUS
EvtDeviceD0Entry(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE PreviousState
);

NTSTATUS
EvtDeviceD0Exit(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE TargetState
);

NTSTATUS
EvtDeviceD0EntryPostInterruptsEnabled(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE PreviousState
); 

NTSTATUS
EvtDeviceD0ExitPreInterruptsDisabled(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE TargetState
);


NTSTATUS
EvtDeviceSelfManagedIoInit(
	IN WDFDEVICE Device
);

NTSTATUS
EvtDeviceSelfManagedIoSuspend(
	_In_
	WDFDEVICE Device
);

NTSTATUS
EvtDeviceSelfManagedIoRestart(
	_In_
	WDFDEVICE Device
);

VOID
EvtDeviceSelfManagedIoFlush(
	_In_
	WDFDEVICE Device
);

VOID
EvtDeviceSelfManagedIoCleanup(
	_In_
	WDFDEVICE Device
);

NTSTATUS ConfigurePowerPolicy(WDFDEVICE Device);


// Interrupt
BOOLEAN MyEvtInterruptIsr(
	WDFINTERRUPT Interrupt,
	ULONG MessageID
);

VOID MyEvtInterruptDpc(
	WDFINTERRUPT Interrupt,
	WDFOBJECT AssociatedObject
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
	WDF_PNPPOWER_EVENT_CALLBACKS PnpPowerCallbacks;


	WDF_OBJECT_ATTRIBUTES DevcieObjAttrs;
	WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&DevcieObjAttrs, DEVICE_CONTEXT);


	//
	// Pnp Power event
	WDF_PNPPOWER_EVENT_CALLBACKS_INIT(&PnpPowerCallbacks);

	PnpPowerCallbacks.EvtDevicePrepareHardware = EvtDevicePrepareHardware;
	PnpPowerCallbacks.EvtDeviceReleaseHardware = EvtDeviceReleaseHardware;

	PnpPowerCallbacks.EvtDeviceD0Entry = EvtDeviceD0Entry;
	PnpPowerCallbacks.EvtDeviceD0Exit = EvtDeviceD0Exit;
	PnpPowerCallbacks.EvtDeviceD0EntryPostInterruptsEnabled = EvtDeviceD0EntryPostInterruptsEnabled;
	PnpPowerCallbacks.EvtDeviceD0ExitPreInterruptsDisabled = EvtDeviceD0ExitPreInterruptsDisabled;


	//
	// 设备启动
	//	 ↓
	// EvtDeviceSelfManagedIoInit    ← 启动后台任务
	//	 ↓
	//   设备正常工作
	//	 ↓(后台任务持续运行)
	//	 ├─ 定时器回调
	//	 ├─ 工作项处理
	//	 ├─ DPC例程
	//	 └─ 系统线程
	//	 ↓
	// 设备暂停（系统休眠）
	//	 ↓
	// EvtDeviceSelfManagedIoSuspend  ← 暂停后台任务
	//	 ↓
	// 设备恢复
	//	 ↓
	// EvtDeviceSelfManagedIoRestart  ← 恢复后台任务
	//	 ↓
	// 设备移除
	//	 ↓
	// EvtDeviceSelfManagedIoFlush    ← 刷新待处理数据
	//	 ↓
	// EvtDeviceSelfManagedIoCleanup  ← 清理后台资源
	//
	PnpPowerCallbacks.EvtDeviceSelfManagedIoInit = EvtDeviceSelfManagedIoInit;
	PnpPowerCallbacks.EvtDeviceSelfManagedIoSuspend = EvtDeviceSelfManagedIoSuspend;
	PnpPowerCallbacks.EvtDeviceSelfManagedIoRestart = EvtDeviceSelfManagedIoRestart;
	PnpPowerCallbacks.EvtDeviceSelfManagedIoFlush = EvtDeviceSelfManagedIoFlush;
	PnpPowerCallbacks.EvtDeviceSelfManagedIoCleanup = EvtDeviceSelfManagedIoCleanup;

	WdfDeviceInitSetPnpPowerEventCallbacks(DeviceInit, &PnpPowerCallbacks);


	//
	// 设置Io回调之前的预处理函数
	// 对于大多数驱动，I/O请求在进入队列后，可能会在任意的线程上下文中被处理（比如系统的工作线程）。
	// EvtIoInCallerContext 给了驱动一个机会，在请求刚到达、还未被"转移"到其他线程前，就在发起者的原始环境中执行一些必要的预处理工作。
	// 一般用于<a href="https://learn.microsoft.com/zh-cn/windows-hardware/drivers/ddi/wdfdevice/nc-wdfdevice-evt_wdf_io_in_caller_context">METHOD_METHOD_NEITHER</a>
	WdfDeviceInitSetIoInCallerContextCallback(DeviceInit, EvtIoInCallerContext);


	status = WdfDeviceCreate(&DeviceInit, &DevcieObjAttrs, &WdfDevice);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfDeviceCreate failed\n"));
		return status;
	}

	//status = ConfigurePowerPolicy(WdfDevice);
	//if (!NT_SUCCESS(status)) {
	//	KdPrint(("电源策略配置失败,status:0x%x\n", status));
	//	return status;
	//}

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

NTSTATUS
EvtDevicePrepareHardware(
	IN WDFDEVICE Device,
	IN WDFCMRESLIST ResourcesRaw,
	IN WDFCMRESLIST ResourcesTranslated
) {
	UNREFERENCED_PARAMETER(Device);
	UNREFERENCED_PARAMETER(ResourcesRaw);
	UNREFERENCED_PARAMETER(ResourcesTranslated);
	
	PDEVICE_CONTEXT devContext = DeviceGetContext(Device);
	ULONG resourceCount;
	NTSTATUS status = STATUS_SUCCESS;

	KdPrint(("========================================\n"));
	KdPrint(("EvtDevicePrepareHardware 被调用！\n"));

	resourceCount = WdfCmResourceListGetCount(ResourcesTranslated);
	KdPrint(("系统分配的资源数量: %d\n", resourceCount));

	for (ULONG i = 0; i < resourceCount; i++) {
		PCM_PARTIAL_RESOURCE_DESCRIPTOR desc =
			WdfCmResourceListGetDescriptor(ResourcesTranslated, i);

		switch (desc->Type) {
		case CmResourceTypeMemory:
			KdPrint(("资源[%d]: 内存 - 物理地址: 0x%llX, 长度: 0x%X\n",
				i, desc->u.Memory.Start.QuadPart, desc->u.Memory.Length));

			// 保存物理地址
			devContext->MmioBase = desc->u.Memory.Start;
			devContext->MmioLength = desc->u.Memory.Length;

			// 映射到内核虚拟地址空间
			devContext->MmioVirtual = MmMapIoSpace(
				desc->u.Memory.Start,
				desc->u.Memory.Length,
				MmNonCached
			);

			if (devContext->MmioVirtual == NULL) {
				KdPrint(("错误：映射 MMIO 失败\n"));
				return STATUS_INSUFFICIENT_RESOURCES;
			}

			KdPrint(("MMIO 映射成功: 虚拟地址 0x%p\n", devContext->MmioVirtual));
			break;

		case CmResourceTypeInterrupt:
			KdPrint(("资源[%d]: 中断 - 向量: %lu, 级别: %lu, 极性: %d\n",
				i, desc->u.Interrupt.Vector, desc->u.Interrupt.Level, desc->Flags));

			devContext->InterruptVector = desc->u.Interrupt.Vector;
			devContext->InterruptLevel = desc->u.Interrupt.Level;

			// 注意：WDF 中断对象通常在 EvtDeviceAdd 中创建
			// 这里只需要保存信息
			break;

		case CmResourceTypeDeviceSpecific:
			KdPrint(("资源[%d]: 设备特定数据 (可忽略)\n", i));
			break;

		default:
			KdPrint(("资源[%d]: 未知类型 %d\n", i, desc->Type));
			break;
		}
	}

	// 可选：验证 HDAudio 控制器是否响应
	if (devContext->MmioVirtual) {
		// 读取 HDAudio 控制器的版本寄存器 (Offset 0x08)
		ULONG version = READ_REGISTER_ULONG((PULONG)((PUCHAR)devContext->MmioVirtual + 0x08));
		KdPrint(("HDAudio 控制器版本: 0x%08X (主要:%d, 次要:%d)\n",
			version, (version >> 8) & 0xFF, version & 0xFF));
	}

	KdPrint(("EvtDevicePrepareHardware 执行完成\n"));
	KdPrint(("========================================\n"));

	return status;
}

NTSTATUS
EvtDeviceReleaseHardware(
	IN WDFDEVICE Device,
	IN WDFCMRESLIST ResourcesTranslated
) {
	UNREFERENCED_PARAMETER(ResourcesTranslated);
	PDEVICE_CONTEXT devContext = DeviceGetContext(Device);

	KdPrint(("EvtDeviceReleaseHardware - 清理硬件资源\n"));

	// 取消映射 MMIO
	if (devContext->MmioVirtual) {
		MmUnmapIoSpace(devContext->MmioVirtual, devContext->MmioLength);
		devContext->MmioVirtual = NULL;
	}

	return STATUS_SUCCESS;
}






NTSTATUS
EvtDeviceD0Entry(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE PreviousState
) {
	UNREFERENCED_PARAMETER(PreviousState);
	PDEVICE_CONTEXT devContext = DeviceGetContext(Device);

	KdPrint(("EvtDeviceD0Entry - 设备上电\n"));

	if (devContext->MmioVirtual == NULL) {
		KdPrint(("错误: MMIO 未映射\n"));
		return STATUS_DEVICE_CONFIGURATION_ERROR;
	}

	return STATUS_SUCCESS;
}

NTSTATUS
EvtDeviceD0Exit(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE TargetState
) {
	UNREFERENCED_PARAMETER(TargetState);
	PDEVICE_CONTEXT devContext = DeviceGetContext(Device);

	KdPrint(("EvtDeviceD0Exit - 设备断电\n"));

	// 禁用 HDAudio 控制器
	if (devContext->MmioVirtual) {
		ULONG gctl = READ_REGISTER_ULONG((PULONG)((PUCHAR)devContext->MmioVirtual + 0x08));
		gctl &= ~(1 << 0);  // 清除 CRST 位
		WRITE_REGISTER_ULONG((PULONG)((PUCHAR)devContext->MmioVirtual + 0x08), gctl);
	}

	return STATUS_SUCCESS;
}

NTSTATUS
EvtDeviceD0EntryPostInterruptsEnabled(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE PreviousState
) {
	UNREFERENCED_PARAMETER(Device);
	UNREFERENCED_PARAMETER(PreviousState);
	KdPrint(("EvtDeviceD0EntryPostInterruptsEnabled\n"));
	return STATUS_SUCCESS;
}

NTSTATUS
EvtDeviceD0ExitPreInterruptsDisabled(
	IN WDFDEVICE Device,
	IN WDF_POWER_DEVICE_STATE TargetState
) {
	UNREFERENCED_PARAMETER(Device);
	UNREFERENCED_PARAMETER(TargetState);
	KdPrint(("EvtDeviceD0ExitPreInterruptsDisabled\n"));
	return STATUS_SUCCESS;
}


NTSTATUS
EvtDeviceSelfManagedIoInit(
	IN WDFDEVICE Device
) {
	UNREFERENCED_PARAMETER(Device);
	KdPrint(("EvtDeviceSelfManagedIoInit\n"));
	return STATUS_SUCCESS;
}

NTSTATUS
EvtDeviceSelfManagedIoSuspend(
	_In_
	WDFDEVICE Device
) {
	UNREFERENCED_PARAMETER(Device);
	KdPrint(("EvtDeviceSelfManagedIoSuspend\n"));
	return STATUS_SUCCESS;
}

NTSTATUS
EvtDeviceSelfManagedIoRestart(
	_In_
	WDFDEVICE Device
) {
	UNREFERENCED_PARAMETER(Device);
	KdPrint(("EvtDeviceSelfManagedIoRestart\n"));
	return STATUS_SUCCESS;
}

VOID
EvtDeviceSelfManagedIoFlush(
	_In_
	WDFDEVICE Device
) {
	UNREFERENCED_PARAMETER(Device);
	KdPrint(("EvtDeviceSelfManagedIoFlush\n"));
}

VOID
EvtDeviceSelfManagedIoCleanup(
	_In_
	WDFDEVICE Device
) {
	UNREFERENCED_PARAMETER(Device);
	KdPrint(("EvtDeviceSelfManagedIoCleanup\n"));
}


NTSTATUS ConfigurePowerPolicy(WDFDEVICE Device) {
	//PDEVICE_CONTEXT devContext = DeviceGetContext(Device);
	NTSTATUS status;

	// 配置空闲策略
	WDF_DEVICE_POWER_POLICY_IDLE_SETTINGS idleSettings;
	WDF_DEVICE_POWER_POLICY_IDLE_SETTINGS_INIT(&idleSettings, IdleCanWakeFromS0);

	// 3秒空闲后休眠
	idleSettings.IdleTimeout = 3000;

	status = WdfDeviceAssignS0IdleSettings(Device, &idleSettings);
	if (!NT_SUCCESS(status)) {
		KdPrint(("设置空闲策略失败: 0x%08X (ignored)\n", status));
		return STATUS_SUCCESS;
	}

	//// 配置唤醒策略
	//WDF_DEVICE_POWER_POLICY_WAKE_SETTINGS wakeSettings;
	//WDF_DEVICE_POWER_POLICY_WAKE_SETTINGS_INIT(&wakeSettings);

	//wakeSettings.Enabled = WdfTrue;
	//wakeSettings.UserControlOfWakeSettings = WakeAllowUserControl;
	//wakeSettings.DxState = PowerDeviceD3;

	//status = WdfDeviceAssignSxWakeSettings(Device, &wakeSettings);
	//if (!NT_SUCCESS(status)) {
	//	KdPrint(("设置唤醒策略失败: 0x%08X\n", status));
	//	return status;
	//}

	return STATUS_SUCCESS;
}


// Interrupt
NTSTATUS CreateInterrupt(WDFDEVICE Device) {
	PDEVICE_CONTEXT devContext = DeviceGetContext(Device);
	WDF_INTERRUPT_CONFIG interruptConfig;
	WDF_OBJECT_ATTRIBUTES interruptAttributes;

	WDF_INTERRUPT_CONFIG_INIT(&interruptConfig,
		MyEvtInterruptIsr,      // ISR 回调
		MyEvtInterruptDpc);      // DPC 回调

	interruptConfig.PassiveHandling = FALSE;  // HDAudio 使用传统中断

	WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&interruptAttributes, INTERRUPT_CONTEXT);

	return WdfInterruptCreate(Device, &interruptConfig, &interruptAttributes,
		&devContext->Interrupt);
}

// ISR (运行在 DIRQL)
BOOLEAN MyEvtInterruptIsr(
	WDFINTERRUPT Interrupt,
	ULONG MessageID
) {
	UNREFERENCED_PARAMETER(MessageID);
	PDEVICE_CONTEXT devContext = DeviceGetContext(Interrupt);

	// 读取中断状态寄存器
	ULONG intStatus = READ_REGISTER_ULONG((PULONG)((PUCHAR)devContext->MmioVirtual + 0x20));

	if (intStatus == 0) {
		return FALSE;  // 不是我们的中断
	}

	// 保存状态供 DPC 使用
	// 清除中断位
	WRITE_REGISTER_ULONG((PULONG)((PUCHAR)devContext->MmioVirtual + 0x20), intStatus);

	// 请求 DPC
	return TRUE;
}

// DPC (运行在 DISPATCH_LEVEL)
VOID MyEvtInterruptDpc(
	WDFINTERRUPT Interrupt,
	WDFOBJECT AssociatedObject
) {
	UNREFERENCED_PARAMETER(Interrupt);
	UNREFERENCED_PARAMETER(AssociatedObject);
	//PDEVICE_CONTEXT devContext = DeviceGetContext(Interrupt);

	// 处理中断
	KdPrint(("DPC: 处理中断\n"));
}
