from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar, List, Optional

from triton import *


class VmRegType(Enum):
    UNKNOWN = auto()
    REGISTER = auto()
    ADDRESS = auto()


@dataclass
class VmRegValue:
    """VMP虚拟寄存器引用值"""
    type: VmRegType
    value: str = ""

    UNKNOWN: ClassVar["VmRegValue"]

    @classmethod
    def of_register(cls, reg_name: str) -> "VmRegValue":
        return cls(type=VmRegType.REGISTER, value=reg_name)

    @classmethod
    def of_address(cls, addr: str) -> "VmRegValue":
        return cls(type=VmRegType.ADDRESS, value=addr)

    def __bool__(self) -> bool:
        return self.type != VmRegType.UNKNOWN

    def __str__(self) -> str:
        if self.type == VmRegType.UNKNOWN:
            return "<unknown>"
        return self.value

    def to_triton_reg(self, ctx: TritonContext) -> Optional[Any]:
        if self.type != VmRegType.REGISTER:
            return None
        return getattr(ctx.registers, self.value, None)

    def addr_int(self) -> Optional[int]:
        if self.type != VmRegType.ADDRESS:
            return None
        return int(self.value, 16)


VmRegValue.UNKNOWN = VmRegValue(type=VmRegType.UNKNOWN, value="")


@dataclass
class VM:
    """VMP虚拟机, 包含寄存器映射和dispatcher列表"""
    name: str
    vIP: VmRegValue = field(default_factory=lambda: VmRegValue(type=VmRegType.UNKNOWN, value=""))
    vSP: VmRegValue = field(default_factory=lambda: VmRegValue(type=VmRegType.UNKNOWN, value=""))
    vREG: VmRegValue = field(default_factory=lambda: VmRegValue(type=VmRegType.UNKNOWN, value=""))
    vBASE: VmRegValue = field(default_factory=lambda: VmRegValue(type=VmRegType.UNKNOWN, value=""))

    dispatchers: List["VmHandlerBlock"] = field(default_factory=list)
    saved_context: Any = None
    vip_dir: int = 1        # vIP方向: 1=低→高, -1=高→低

    @classmethod
    def from_dict(cls, data: dict) -> "VM":
        vip_dir = 0
        def _parse_reg(val) -> VmRegValue:
            nonlocal vip_dir
            if not val or val == '':
                return VmRegValue.UNKNOWN
            s = str(val)
            if s.endswith('-'):
                vip_dir = -1; s = s[:-1]
            elif s.endswith('+'):
                vip_dir = 1; s = s[:-1]
            if s.startswith('0x') or s.startswith('0X'):
                return VmRegValue.of_address(s)
            return VmRegValue.of_register(s)

        return cls(
            name=data.get('name', ''),
            vIP=_parse_reg(data.get('vIP', '')),
            vSP=_parse_reg(data.get('vSP', '')),
            vREG=_parse_reg(data.get('vREG', '')),
            vBASE=_parse_reg(data.get('vBASE', '')),
            vip_dir=vip_dir,
        )


@dataclass
class VmHandlerBlock:
    """VM dispatch代码块 (start/end + 执行状态)"""
    name: str
    start: int
    end: int

    exec_state: dict = field(default_factory=dict)
    next_handler: int = -1
    is_executed: bool = False
    exec_count: int = 0            # 重复执行次数
    feature: str = ""           # 人工分析的dispatch功能 (如 'vPush', 'vPop', 'vAdd')


class VmDispatcher:
    """VM Dispatch 检测器"""

    _NON_DISPATCH_REGS = frozenset({'esp', 'sp', 'spl'})

    @staticmethod
    def is_dispatch(block: VmHandlerBlock, vm: VM, ctx: TritonContext,
                    last_inst: Optional[Instruction] = None) -> bool:
        if block.start < 0 or block.end < 0:
            return False

        if last_inst is not None:
            return VmDispatcher._check_dispatch(ctx, last_inst, block.end, vm)

        insts: List[Instruction] = ctx.disassembly(block.end, 1)
        if not insts:
            return False
        return VmDispatcher._check_dispatch(ctx, insts[0], block.end, vm)

    @staticmethod
    def get_dispatch_target(ctx: TritonContext, handler_end: int) -> int:
        insts = ctx.disassembly(handler_end, 1)
        if not insts:
            return -1
        last = insts[0]
        if last.getType() in (OPCODE.X86.RET, OPCODE.X86.RETF, OPCODE.X86.RETFQ):
            esp_val = ctx.getConcreteRegisterValue(ctx.registers.esp)
            return ctx.getConcreteMemoryValue(MemoryAccess(esp_val - 4, 4))
        if last.getType() == OPCODE.X86.JMP:
            for op in last.getOperands():
                if op.getType() == OPERAND.REG:
                    reg = getattr(ctx.registers, op.getName(), None)
                    if reg:
                        return ctx.getConcreteRegisterValue(reg)
        return -1

    @staticmethod
    def op_is_dispatch(inst: Instruction) -> bool:
        t = inst.getType()
        if t == OPCODE.X86.JMP:
            for op in inst.getOperands():
                if op.getType() == OPERAND.REG:
                    return True
        if t in (OPCODE.X86.RET, OPCODE.X86.RETF, OPCODE.X86.RETFQ):
            return True
        return False

    @staticmethod
    def is_vm_reg_switch(inst: Instruction, vm: VM) -> bool:
        """用Triton语义检测VM寄存器切换。
        
        只检测MOV/LEA/MOVZX/XCHG等赋值类指令,
        排除BTS/BTC/ADD/SUB等仅在运算中使用VM寄存器的指令.
        """
        t = inst.getType()
        if t not in (OPCODE.X86.MOV, OPCODE.X86.MOVZX, OPCODE.X86.MOVSX,
                     OPCODE.X86.LEA, OPCODE.X86.XCHG, OPCODE.X86.MOVSXD):
            return False

        vm_reg_names = set()
        for vr in [vm.vIP, vm.vSP, vm.vBASE]:
            if vr.type == VmRegType.REGISTER:
                vm_reg_names.add(vr.value.lower())

        if len(vm_reg_names) < 2:
            return False

        written_names = set(rr[0].getName().lower() for rr in inst.getWrittenRegisters())
        expl_dst = set()
        for op in inst.getOperands():
            if op.getType() == OPERAND.REG and op.getName().lower() in written_names:
                if op.getName().lower() in vm_reg_names:
                    expl_dst.add(op.getName().lower())

        read_regs = [rr[0].getName().lower() for rr in inst.getReadRegisters()]

        for w in expl_dst:
            for r in read_regs:
                if r in vm_reg_names and r != w:
                    return True
        return False

    @staticmethod
    def _check_dispatch(ctx: TritonContext, last: Instruction,
                        end: int, vm: VM) -> bool:
        if VmDispatcher._is_indirect_jmp(last, vm):
            return True
        if VmDispatcher._is_push_ret(ctx, last, end, vm):
            return True
        return False

    @staticmethod
    def _is_indirect_jmp(inst: Instruction, vm: VM) -> bool:
        if inst.getType() != OPCODE.X86.JMP:
            return False
        vbase_name = vm.vBASE.value if vm.vBASE.type == VmRegType.REGISTER else ''
        for op in inst.getOperands():
            if op.getType() == OPERAND.REG:
                if not vbase_name or op.getName().lower() == vbase_name.lower():
                    return True
        return False

    @staticmethod
    def _is_push_ret(ctx: TritonContext, last: Instruction,
                     end: int, vm: VM) -> bool:
        if last.getType() not in (OPCODE.X86.RET, OPCODE.X86.RETF, OPCODE.X86.RETFQ):
            return False

        vbase_name = vm.vBASE.value if vm.vBASE.type == VmRegType.REGISTER else ''

        for offset in range(1, 16):
            prev_addr = end - offset
            try:
                prev_insts = ctx.disassembly(prev_addr, 1)
            except Exception:
                continue
            if not prev_insts:
                continue
            prev = prev_insts[0]
            if prev.getAddress() + prev.getSize() == end:
                if prev.getType() != OPCODE.X86.PUSH:
                    return False
                if VmDispatcher._is_fp_push(prev):
                    return False
                if not vbase_name:
                    return True
                return VmDispatcher._push_matches_vbase(prev, vbase_name)

        return False

    @staticmethod
    def _push_matches_vbase(inst: Instruction, vbase_name: str) -> bool:
        ops = inst.getOperands()
        if not ops:
            return False
        op = ops[0]
        if op.getType() == OPERAND.REG:
            return op.getName().lower() == vbase_name.lower()
        return False

    @staticmethod
    def _is_fp_push(inst: Instruction) -> bool:
        ops = inst.getOperands()
        if not ops:
            return False
        op = ops[0]
        if op.getType() == OPERAND.REG:
            return op.getName().lower() in VmDispatcher._NON_DISPATCH_REGS
        return False
