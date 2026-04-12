#ifndef TIMER_H
#define TIMER_H

#include <ntddk.h>
#include <wdf.h>

NTSTATUS MyTimerCreate(IN WDFDEVICE WdfDevice, OUT WDFTIMER *WdfTimer);


#endif