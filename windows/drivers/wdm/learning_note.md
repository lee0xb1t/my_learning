# Learning Note

1. OS基础：中断与Irql level
2. hello world，驱动
   DriverObject和DeviceObject的机构成员作用
3. 驱动框架分类
   WDM和WDF区别
4. 基础数据类型
5. 驱动中字符串处理
   DbgPrint输出字符串的坑
6. 内存管理
   池内存分配函数
   分页内存和非分页内存
   Lookaside：固定大小的内存频繁申请和释放
7. 驱动布局与设备栈
8. Irp和派遣函数
   IO_STACK_LOCATION
   IoCallDriver
9. 用户通信
10. 注册表操作api
11. 内核同步机制
   对象等待
   自旋锁
   互斥锁
   信号量
   事件
   WORKITEM
   不同irql下的同步
12. 内核中的数据结构
   链表
   二叉树
13. irp的同步和异步
   同步完成
   异步完成
   irp的取消
14. StartIO
   StartIO例程
   自定义StartIO（多队列）
15. 内核定时器
   Timer
   Dpc
   内核中的等待操作
   时间api
16. 驱动间调用
   同步调用
   异步调用
   直接创建irp包调用驱动
17. Pnp驱动
   Pnp设备添加
   电源状态与转换
   电源管理
   pci总线获取
