# ============================================================
#  dispatch 功能检测 — Triton符号表达式等价验证
# ============================================================
from dataclasses import dataclass
from typing import List, Optional, Tuple
from triton import *
from vm_types import VmRegType, VM, VmHandlerBlock, VmRegValue


@dataclass
class VmStateTrace:
    """单次dispatch的状态跟踪快照"""
    vip_in: int = 0
    vip_out: int = 0
    vsp_in: int = 0
    vsp_out: int = 0
    regid: int = -1
    instructions: list = None     # [(addr, disasm), ...]
    llvm_ir: str = ""              # Triton lift结果

    def __post_init__(self):
        if self.instructions is None:
            self.instructions = []

    def vip_delta(self) -> int:
        return self.vip_out - self.vip_in

    def vsp_delta(self) -> int:
        return self.vsp_out - self.vsp_in


class VmStateTracker:
    """VM状态跟踪器"""

    def __init__(self, vm: VM):
        self.vm = vm
        self._current_trace: Optional[VmStateTrace] = None
        self._inst_buf: list = []

    def begin_block(self, ctx: TritonContext):
        self._current_trace = VmStateTrace()
        self._current_trace.vip_in = self._read_vip(ctx)
        self._current_trace.vsp_in = self._read_reg(ctx, self.vm.vSP)
        self._inst_buf = []

    def track_inst(self, addr: int, disasm: str):
        if self._current_trace:
            self._inst_buf.append((addr, disasm))

    def end_block(self, ctx: TritonContext, regid: int) -> VmStateTrace:
        if self._current_trace is None:
            return VmStateTrace()
        t = self._current_trace
        t.vip_out = self._read_vip(ctx)
        t.vsp_out = self._read_reg(ctx, self.vm.vSP)
        t.regid = regid
        t.instructions = self._inst_buf.copy()
        try:
            t.llvm_ir = ctx.liftToLLVM(ctx.getRegisterAst(self._read_vip_reg(ctx)))  # type: ignore
        except Exception:
            pass
        self._current_trace = None
        self._inst_buf = []
        return t

    def delta_snapshot(self, ctx: TritonContext) -> Tuple[int, int]:
        """捕获vip增量(不清理current_trace, 用于每次dispatch)"""
        if self._current_trace is None:
            return (0, 0)
        vip_out = self._read_vip(ctx)
        delta = vip_out - self._current_trace.vip_in
        return (delta, self._current_trace.vip_in)

    def vip_in(self) -> int:
        return self._current_trace.vip_in if self._current_trace else 0

    def _read_vip(self, ctx: TritonContext) -> int:
        try:
            reg = self.vm.vIP.to_triton_reg(ctx)
            return ctx.getConcreteRegisterValue(reg) if reg else 0  # type: ignore
        except Exception:
            return 0

    def _read_vip_reg(self, ctx):
        return self.vm.vIP.to_triton_reg(ctx)

    def _read_reg(self, ctx: TritonContext, vr: VmRegValue) -> int:
        try:
            reg = vr.to_triton_reg(ctx)
            return ctx.getConcreteRegisterValue(reg) if reg else 0  # type: ignore
        except Exception:
            return 0


class HandlerSpec:
    name: str = ""
    @staticmethod
    def verify(insts: List[Instruction], vsp: str, vip: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def extract_info(insts: List[Instruction], vsp: str, vip: str,
                     ctx: TritonContext, tracker=None, vbase: str = '') -> str:
        return ""


class VmDispatchFeature:
    @staticmethod
    def detect(block, vm, processed: List[Instruction], ctx: TritonContext,
               tracker=None) -> str:
        if not processed:
            return ""
        vsp = _name(vm.vSP)
        vip = _name(vm.vIP)
        vbase = _name(vm.vBASE)
        for spec in SPECS:
            if spec.verify(processed, vsp, vip):
                info = spec.extract_info(processed, vsp, vip, ctx, tracker, vbase)
                return f"{spec.name} {info}" if info else spec.name
        return ""


# ============================================================
#  vPop: [vSP]→val, vSP+=4, [vIP]→regid, vIP+=1, [vREG+regid]=val
# ============================================================
class VPop(HandlerSpec):
    name = "vPop"

    @staticmethod
    def verify(insts, vsp, vip):
        l_from_vsp = _mem_load(insts, vsp)
        l_from_vip = _mem_load(insts, vip, size=1)
        wm = _mem_write(insts)
        ws = _reg_write(insts, vsp)
        wi = _reg_write(insts, vip)

        if not all([l_from_vsp, l_from_vip, wm, ws, wi]):
            return False
        return _equiv(l_from_vsp[1], wm[1])

    @staticmethod
    def extract_info(insts, vsp, vip, ctx, tracker=None, vbase=''):
        return _store_regid_info(insts, vip, ctx)


# ============================================================
#  vPush: [vIP]→regid, vIP+=1, [vREG+regid]→val, [vSP]=val
# ============================================================
class VPush(HandlerSpec):
    name = "vPush"

    @staticmethod
    def verify(insts, vsp, vip):
        l_from_vreg = _mem_load(insts, 'esp')
        l_from_vip = _mem_load(insts, vip, size=1)
        wm = _mem_write(insts)
        wi = _reg_write(insts, vip)

        if not all([l_from_vreg, l_from_vip, wm, wi]):
            return False
        return _equiv(l_from_vreg[1], wm[1])

    @staticmethod
    def extract_info(insts, vsp, vip, ctx, tracker=None, vbase=''):
        return _store_regid_info(insts, vip, ctx)


# ============================================================
#  vPushImm / vPop (同 VmRegType)
# ============================================================
class VPushImm(HandlerSpec):
    name = "vPushImm"

    @staticmethod
    def verify(insts, vsp, vip):
        loads = _mem_loads(insts, vip)
        wm = _mem_write(insts)
        wi = _reg_write(insts, vip)
        if len(loads) < 2 or not wm or not wi:
            return False
        for _, lv in loads:
            if _equiv(lv, wm[1]):
                return True
        return False

    @staticmethod
    def extract_info(insts, vsp, vip, ctx, tracker=None, vbase=''):
        return _store_regid_info(insts, vip, ctx)


class VPushVSP(HandlerSpec):
    name = "vPushVSP"

    @staticmethod
    def verify(insts, vsp, vip):
        wm = _mem_write(insts)
        ws = _reg_write(insts, vsp)
        lv = _mem_load(insts, 'esp')   # vPushVSP不读vREG
        if not wm or not ws or lv:
            return False
        mem, _ = wm
        return mem.getBaseRegister().getName().lower() == vsp

    @staticmethod
    def extract_info(insts, vsp, vip, ctx, tracker=None, vbase=''):
        return ""


class VJmp(HandlerSpec):
    """vJmp: 取偏移量(dword), 无[esp]读, 无vREG写"""
    name = "vJmp"

    @staticmethod
    def verify(insts, vsp, vip):
        l_from = _mem_load(insts, vsp, size=4) or _mem_load(insts, vip, size=4)
        w_to_vsp_or_vip = _reg_write(insts, vsp) or _reg_write(insts, vip)
        l_from_esp = _mem_load(insts, 'esp')
        if not l_from or not w_to_vsp_or_vip or l_from_esp:
            return False
        return True

    @staticmethod
    def extract_info(insts, vsp, vip, ctx, tracker=None, vbase=''):
        """跳转目标 = vBASE的最终值"""
        w = _reg_write(insts, vbase) if vbase else (_reg_write(insts, vip) or _reg_write(insts, vsp))
        if w:
            try:
                val = w[1].evaluate()  # type: ignore
                return f"0x{val:x}"
            except Exception:
                pass
        return ""


SPECS: List[HandlerSpec] = [VPop, VPush, VPushImm, VPushVSP, VJmp]


# ============================================================
#  Triton 符号分析工具
# ============================================================

def _store_regid_info(insts, vip, ctx) -> str:
    """从[vREG+regid]或[esp+regid]访问指令提取解码后regid"""
    computed = _find_regid_in_insts(insts, vip, ctx)
    raw_byte = _find_raw_byte(insts, vip)

    vip_addr = _find_vip_addr(insts, vip)
    info = f"0x{computed:x}"
    if computed != raw_byte:
        info += f" (raw:0x{raw_byte:x})"
    if vip_addr > 0:
        raw = ctx.getConcreteMemoryAreaValue(vip_addr, 16)
        bytes_str = " ".join(f"{b:02x}" for b in raw)
        while bytes_str.endswith(" 00"):
            bytes_str = bytes_str[:-3]
        return f"{info} @{hex(vip_addr)} | {bytes_str}"
    return info


def _find_regid_in_insts(insts, vip, ctx) -> int:
    """找到vIP加载的目标寄存器, 在同寄存器参与[esp+reg]运算时取其值作为regid"""
    # 1. 从vIP加载的指令中找到目标寄存器
    target_reg_name = None
    vip_inst = _find_load_inst(insts, vip, size=1)
    if vip_inst is not None:
        for wr, _ in vip_inst.getWrittenRegisters():
            name = wr.getName().lower()
            if name not in ('eip', 'af', 'cf', 'of', 'pf', 'sf', 'zf', 'tf', 'if', 'df'):
                target_reg_name = name
                break

    # 2. 在[esp+reg]访问指令中找同寄存器, 读取其值
    if target_reg_name is None:
        return 0
    tgt_id = getattr(ctx.registers, target_reg_name).getId()

    for inst in insts:
        for mem, _ in inst.getLoadAccess():
            if mem.getBaseRegister().getName().lower() == 'esp':
                for rr, ast in inst.getReadRegisters():
                    if rr.getId() == tgt_id:
                        try:
                            return ast.evaluate()  # type: ignore
                        except Exception:
                            pass
        for mem, _ in inst.getStoreAccess():
            if mem.getBaseRegister().getName().lower() == 'esp':
                for rr, ast in inst.getReadRegisters():
                    if rr.getId() == tgt_id:
                        try:
                            return ast.evaluate()  # type: ignore
                        except Exception:
                            pass
    return 0


def _find_raw_byte(insts, vip) -> int:
    vip_inst = _find_load_inst(insts, vip, size=1)
    if vip_inst is None:
        return 0
    for wr, ast in vip_inst.getWrittenRegisters():
        if wr.getName().lower() not in ('eip', 'af', 'cf', 'of', 'pf', 'sf', 'zf', 'tf', 'if', 'df'):
            try:
                return ast.evaluate()  # type: ignore
            except Exception:
                pass
    return 0


def _find_store_inst(insts) -> Optional[Instruction]:
    for inst in insts:
        if inst.getStoreAccess():
            return inst
    return None


def _find_vip_addr(insts, vip) -> int:
    for inst in insts:
        for mem, _ in inst.getLoadAccess():
            if mem.getBaseRegister().getName().lower() == vip:
                return mem.getAddress()
    return 0


def _find_load_inst(insts, reg, size=None) -> Optional[Instruction]:
    for inst in insts:
        for mem, _ in inst.getLoadAccess():
            if mem.getBaseRegister().getName().lower() == reg:
                if size is None or mem.getSize() == size:
                    return inst
    return None


def _mem_load(insts, reg, size=None) -> Optional[tuple]:
    inst = _find_load_inst(insts, reg, size)
    if inst is None:
        return None
    for wr, ast in inst.getWrittenRegisters():
        if wr.getName().lower() not in ('eip', 'af', 'cf', 'of', 'pf', 'sf', 'zf', 'tf', 'if', 'df'):
            return (inst, ast)
    return None


def _mem_loads(insts, reg) -> List[tuple]:
    result = []
    for inst in insts:
        if not any(mem.getBaseRegister().getName().lower() == reg
                   for mem, _ in inst.getLoadAccess()):
            continue
        for wr, ast in inst.getWrittenRegisters():
            if wr.getName().lower() not in ('eip', 'af', 'cf', 'of', 'pf', 'sf', 'zf', 'tf', 'if', 'df'):
                result.append((inst, ast))
                break
    return result


def _mem_write(insts) -> Optional[tuple]:
    for inst in insts:
        for mem, ast in inst.getStoreAccess():
            return (mem, ast)
    return None


def _reg_write(insts, reg) -> Optional[tuple]:
    for inst in insts:
        for r, ast in inst.getWrittenRegisters():
            if r.getName().lower() == reg:
                return (r, ast)
    return None


def _equiv(a, b) -> bool:
    try:
        return a.evaluate() == b.evaluate()  # type: ignore
    except Exception:
        return False


def _name(vr) -> str:
    return vr.value if vr and vr.type == VmRegType.REGISTER else ""
