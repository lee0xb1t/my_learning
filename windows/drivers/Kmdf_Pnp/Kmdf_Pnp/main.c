#include "device.h"

#include <ntddk.h>
#include <wdf.h>


_IRQL_requires_(DISPATCH_LEVEL)
NTSTATUS LoadParameters(IN WDFDRIVER WdfDriver);

NTSTATUS DriverEntry(IN PDRIVER_OBJECT DriverObject, IN PUNICODE_STRING RegistryPath) {
	NTSTATUS status = STATUS_SUCCESS;
	WDF_DRIVER_CONFIG Config;
	WDFDRIVER WdfDriver;

	WDF_DRIVER_CONFIG_INIT(&Config, EvtDriverDeviceAdd);

	status = WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, &Config, &WdfDriver);
	if (!NT_SUCCESS(status)) {
		KdPrint(("WdfDrvierCreate failed\n"));
		return status;
	}

	KdPrint(("驱动创建成功\n"));

	status = LoadParameters(WdfDriver);
	if (!NT_SUCCESS(status)) {
		KdPrint(("RegKey Parameters load failed (ignored)\n"));
	}

	return status;
}


_IRQL_requires_(DISPATCH_LEVEL)
NTSTATUS LoadParameters(IN WDFDRIVER WdfDriver) {
	NTSTATUS status;
	WDFKEY WdfKey;
	UNICODE_STRING ValueName;

	status = WdfDriverOpenParametersRegistryKey(WdfDriver, STANDARD_RIGHTS_ALL, WDF_NO_OBJECT_ATTRIBUTES, &WdfKey);
	if (!NT_SUCCESS(status)) {
		return status;
	}

	ULONG Number = 0;
	RtlInitUnicodeString(&ValueName, L"数字");

	status = WdfRegistryQueryULong(WdfKey, &ValueName, &Number);
	if (!NT_SUCCESS(status)) {
		return status;
	}
	KdPrint(("查询到数字：%d\n", Number));


	WDFSTRING StringValue;
	status = WdfStringCreate(NULL, WDF_NO_OBJECT_ATTRIBUTES, &StringValue);
	if (!NT_SUCCESS(status)) {
		KdPrint(("wdf string创建失败\n"));
		return status;
	}

	RtlInitUnicodeString(&ValueName, L"字符");

	status = WdfRegistryQueryString(WdfKey, &ValueName, StringValue);
	if (!NT_SUCCESS(status)) {
		KdPrint(("字符串查询失败\n"));
		return status;
	}
	UNICODE_STRING UniStringValue;
	WdfStringGetUnicodeString(StringValue, &UniStringValue);
	KdPrint(("查询到字符：%wZ\n", &UniStringValue));

	
	ULONG BoolValue = 0;
	RtlInitUnicodeString(&ValueName, L"布尔");

	status = WdfRegistryQueryULong(WdfKey, &ValueName, &BoolValue);
	if (!NT_SUCCESS(status)) {
		return status;
	}
	KdPrint(("查询到布尔：%d\n", BoolValue));


	WdfRegistryClose(WdfKey);

	return status;
}
