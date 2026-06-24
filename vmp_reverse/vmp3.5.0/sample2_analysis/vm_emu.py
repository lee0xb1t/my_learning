# ============================================================
#  VM emulation
# ============================================================
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from trace_types import *
from triton import *
from vm_types import VM, VmHandlerBlock, VmDispatcher
from vm_features import VmDispatchFeature, VmStateTracker, VmStateTrace


@dataclass
class DispatchEvent:
    seq: int = -1
    block: VmHandlerBlock = None
    regid: int = -1
    vip: int = 0
    vbase: int = 0          # dispatch时的vBASE值 (=跳转目标)
    is_new: bool = False
    feature: str = ""
    state_trace: Optional["VmStateTrace"] = None


# ============================================================
#  triton helpers
# ============================================================
def make_ctx() -> TritonContext:
    ctx = TritonContext(ARCH.X86)
    ctx.setMode(MODE.CONSTANT_FOLDING, True)
    ctx.setMode(MODE.ALIGNED_MEMORY, True)
    ctx.setMode(MODE.AST_OPTIMIZATIONS, True)
    return ctx


def _sync_regs(ctx: TritonContext, inst: InstructionSnapshot):
    ctx_regs = ctx.registers  # type: ignore
    mapping = {
        ctx_regs.eax: 'eax', ctx_regs.ebx: 'ebx', ctx_regs.ecx: 'ecx',
        ctx_regs.edx: 'edx', ctx_regs.edi: 'edi', ctx_regs.esi: 'esi',
        ctx_regs.ebp: 'ebp', ctx_regs.esp: 'esp', ctx_regs.eflags: 'eflags',
    }
    for mk, mv in mapping.items():
        if ctx.getConcreteRegisterValue(mk) != inst.regs.get(mv):
            if ctx.isRegisterSymbolized(mk):
                continue
            ctx.setConcreteRegisterValue(mk, inst.regs.get(mv))
            if not ctx.isRegisterSymbolized(mk):
                ctx.symbolizeRegister(mk, mv)


def _sync_mem(ctx: TritonContext, inst: InstructionSnapshot):
    for m in inst.mems:
        mem = MemoryAccess(m.addr_int(), m.size)
        if ctx.isMemorySymbolized(mem):
            continue
        if ctx.getConcreteMemoryValue(mem) != m.val_int():
            ctx.setConcreteMemoryValue(mem, m.val_int())
        if not ctx.isMemorySymbolized(mem):
            ctx.symbolizeMemory(mem, m.addr)


def _read_bytecode(ctx: TritonContext, vip: int, size: int = 5) -> str:
    if not vip or size <= 0:
        return ""
    try:
        return " ".join(f"{b:02x}" for b in ctx.getConcreteMemoryAreaValue(vip, size))
    except Exception:
        return ""


# ============================================================
#  VmEmu
# ============================================================
@dataclass
class VmEvent:
    vm: VM = None
    ctx: TritonContext = None
    dispatches: list = None

    def __post_init__(self):
        if self.dispatches is None:
            self.dispatches = []

    def run_dispatch(self) -> Iterator[DispatchEvent]:
        yield from self.dispatches


class VmEmu:
    """VM模拟器 — 支持多VM, run() yield连续dispatch"""

    def __init__(self, vm: VM, trace: TraceIndex):
        self.vm = vm
        self.trace = trace
        self._seq = 0
        self._next_snap = None

    def run_vm(self) -> Iterator[VmEvent]:
        yield from self._run_vm_for(self.vm)

    def _run_vm_for(self, vm: VM) -> Iterator[VmEvent]:
        if vm.saved_context:
            ctx = vm.saved_context
        else:
            ctx = make_ctx()
            vm.saved_context = ctx

        _bound = _BoundCtx(ctx, vm, self.trace,
                           log_block=self._log_block,
                           create_block=self._create_block)
        if hasattr(self, '_skip_after') and self._skip_after:
            _bound._skip_until = self._skip_after
            self._skip_after = 0
        if hasattr(self, '_last_target') and self._last_target:
            _bound._first_handler_start = self._last_target
            self._last_target = 0
        # 传递上一个VM的粘合指令
        if hasattr(self, '_next_snap') and self._next_snap:
            _bound._first_snap = self._next_snap
            self._next_snap = None

        dispatches = []
        last_block = None
        for ev in _bound.run():
            ev.seq = self._seq; self._seq += 1
            dispatches.append(ev)
            last_block = ev.block
        ve = VmEvent(vm=vm, ctx=ctx, dispatches=dispatches)
        yield ve

        if last_block and last_block.next_handler > 0:
            self._last_target = last_block.next_handler

        if _bound._switch_info:
            addr, disasm = _bound._switch_info
            print(f'\n[+] [VM SWITCH] reg reassigned @ {hex(addr)}: {disasm}')
            _dump_vm_regs(_bound, ctx, vm)
            self._skip_after = addr

    def run(self, vms: List[VM]) -> Iterator[VmEvent]:
        for vm in vms:
            yield from self._run_vm_for(vm)

    def exec_counts(self) -> list:
        result = []
        for b in self.vm.dispatchers:
            if b.is_executed:
                result.append((b, b.exec_count + 1))
        return result

    def _log_block(self, ctx, block, vm):
        is_disp = VmDispatcher.is_dispatch(block, vm, ctx)
        tag = 'DISPATCH' if is_disp else 'HANDLER'
        # print(f'\n[+] [{tag}] {block.name} end @ {hex(block.end)}')
        state = block.exec_state
        for name, vr in [('vIP', vm.vIP), ('vSP', vm.vSP), ('vREG', vm.vREG), ('vBASE', vm.vBASE)]:
            reg = vr.to_triton_reg(ctx)
            if reg:
                val = ctx.getConcreteRegisterValue(reg)
                state[f'{name}_val'] = val
                # print(f'    {name:>6}({vr.value:>3}) = {hex(val)}')
        if is_disp:
            for rn in ['ebp', 'eax', 'ecx', 'edx', 'ebx', 'esi', 'edi']:
                r = getattr(ctx.registers, rn)
                state[rn] = ctx.getConcreteRegisterValue(r)
                # print(f'    {rn:>3} = {hex(state[rn])}')
            na = VmDispatcher.get_dispatch_target(ctx, block.end)
            if na > 0:
                block.next_handler = na
                # print(f'    next_handler -> {hex(na)}')
        block.is_executed = True
        # print()

    def _create_block(self, prev, vm):
        s = prev.next_handler
        if s <= 0 or any(d.start == s for d in vm.dispatchers):
            return
        b = VmHandlerBlock(name=f'vm_dispatch{len(vm.dispatchers)}', start=s, end=-1)
        vm.dispatchers.append(b)
        # print(f'[+] [DETECT] {b.name} @ {hex(s)}')


class _BoundCtx:
    """绑定vm+ctx的单次运行"""

    def __init__(self, ctx, vm, trace, *, log_block=None, create_block=None):
        self.ctx = ctx
        self.vm = vm
        self.trace = trace
        self.tracker = VmStateTracker(vm)
        self._active = [None]
        self._last_regid = [0]
        self.log_block = log_block
        self.create_block = create_block
        self._switch_info = None
        self._first_snap = None
        self._skip_until = 0
        self._entry_start = None

    def run(self) -> Iterator[DispatchEvent]:
        started = self._skip_until == 0
        found_dispatch = not (self._skip_until > 0)
        for _, snap in self.trace.iter_items():
            if not started:
                if snap.addr_int() == self._skip_until:
                    started = True
                else:
                    continue
            if self._entry_start is None:
                self._entry_start = snap.addr_int()
            check_switch = found_dispatch
            for ev in self._do_snap(snap, check_switch=check_switch):
                found_dispatch = True
                yield ev
            if self._switch_info is not None:
                self._first_snap = snap
                break

    def _do_snap(self, snap, check_switch=True) -> Iterator[DispatchEvent]:
        _sync_regs(self.ctx, snap)
        _sync_mem(self.ctx, snap)
        self.ctx.setConcreteMemoryAreaValue(snap.addr_int(), snap.opcode_bytes())
        ctx_inst = Instruction(snap.addr_int(), snap.opcode_bytes())
        self.ctx.processing(ctx_inst)  # type: ignore

        self._track_regid(ctx_inst)
        self.tracker.track_inst(ctx_inst.getAddress(), ctx_inst.getDisassembly())

        if check_switch and VmDispatcher.is_vm_reg_switch(ctx_inst, self.vm):
            self._switch_info = (ctx_inst.getAddress(), ctx_inst.getDisassembly())
            return

        ev: Optional[DispatchEvent] = self._step(snap, ctx_inst)
        if ev is None:
            return
        if ev.is_new or not ev.block.feature:
            ev.block.feature = _detect_feature(ev.block, self.vm, self.trace)
        ev.feature = ev.block.feature
        yield ev

    def _step(self, snap, ctx_inst) -> Optional[DispatchEvent]:
        """处理单条指令: 匹配dispatch边界或handler block"""
        if VmDispatcher.op_is_dispatch(ctx_inst):
            ev = self._on_dispatch_boundary(snap)
            if ev is not None:
                return ev
        return self._match_handler_blocks(snap, ctx_inst)

    def _on_dispatch_boundary(self, snap) -> Optional[DispatchEvent]:
        """检测到dispatch指令, 设置活跃block的end或创建首个block"""
        active = self._active[0]
        if active is not None and active.end < 0:
            active.end = snap.addr_int()
            self.log_block(self.ctx, active, self.vm)
            self.create_block(active, self.vm)
            return self._emit(active)
        if not self.vm.dispatchers:
            return self._create_first_block(snap)
        return None

    def _create_first_block(self, snap) -> DispatchEvent:
        """为新VM自动创建第一个handler block"""
        start = getattr(self, '_first_handler_start', 0) or self._entry_start or snap.addr_int()
        b = VmHandlerBlock(name='vm_dispatch0', start=start, end=snap.addr_int())
        b.exec_state['_vip_in'] = _read_vip_inner(self.vm, self.ctx)
        self._entry_start = None
        self.vm.dispatchers.append(b)
        self._active[0] = b
        self._last_regid[0] = -1
        self.tracker.begin_block(self.ctx)
        b.is_executed = True
        b.next_handler = VmDispatcher.get_dispatch_target(self.ctx, b.end)
        self.create_block(b, self.vm)
        return self._emit(b, is_new=True)

    def _match_handler_blocks(self, snap, ctx_inst) -> Optional[DispatchEvent]:
        """匹配已知block的end/start"""
        return (self._match_block_end(snap, ctx_inst) or
                self._match_block_start(snap) or None)

    def _match_block_end(self, snap, ctx_inst) -> Optional[DispatchEvent]:
        for block in self.vm.dispatchers:
            if block.start >= 0 and block.end >= 0 and snap.addr_int() == block.end:
                is_new = not block.is_executed
                if is_new:
                    self.log_block(self.ctx, block, self.vm)
                    if not VmDispatcher.is_dispatch(block, self.vm, self.ctx, ctx_inst):
                        print(f'[+] Non-dispatch handler {block.name}, stopping')
                        return None
                    self.create_block(block, self.vm)
                else:
                    block.exec_count += 1
                    na = VmDispatcher.get_dispatch_target(self.ctx, block.end)
                    if na > 0:
                        block.next_handler = na
                return self._emit(block, is_new)
        return None

    def _match_block_start(self, snap) -> Optional[DispatchEvent]:
        for block in self.vm.dispatchers:
            if block.start >= 0 and snap.addr_int() == block.start:
                self._active[0] = block
                self._last_regid[0] = -1
                self.tracker.begin_block(self.ctx)
                block.exec_state['_vip_in'] = _read_vip_inner(self.vm, self.ctx)
                if not block.is_executed:
                    print(f'[+] [START] {block.name} @ {hex(block.start)}')
                break
        return None

    def _track_regid(self, ctx_inst):
        for mem, _ in (ctx_inst.getStoreAccess() or []) + (ctx_inst.getLoadAccess() or []):
            if mem.getBaseRegister().getName().lower() == 'esp':
                try:
                    val = self.ctx.getConcreteRegisterValue(self.ctx.registers.edx)  # type: ignore
                    self._last_regid[0] = val
                    if self._active[0]:
                        self._active[0].exec_state['_last_regid'] = val
                except Exception:
                    pass

    def _emit(self, block, is_new=False) -> DispatchEvent:
        regid = block.exec_state.get('_last_regid', -1)
        vip_in = block.exec_state.get('_vip_in', 0)
        vip_out = _read_vip_inner(self.vm, self.ctx)
        delta = vip_out - vip_in if vip_in else 0
        st = self.tracker.end_block(self.ctx, regid) if is_new else None
        if st is None:
            st = VmStateTrace(vip_in=vip_in, vip_out=vip_out)
        vbase = _read_vbase(self.vm, self.ctx)
        return DispatchEvent(block=block, regid=regid, vip=vip_in,
                             vbase=vbase, is_new=is_new, state_trace=st)

def _dump_vm_regs(_bound, ctx, vm):
    print(f'    VM Register Values:')
    for name, vr in [('vIP', vm.vIP), ('vSP', vm.vSP),
                      ('vREG', vm.vREG), ('vBASE', vm.vBASE)]:
        reg = vr.to_triton_reg(ctx)
        if reg:
            val = ctx.getConcreteRegisterValue(reg)
            print(f'    {name:>6}({vr.value:>3}) = {hex(val)}')

def _read_vip_inner(vm: VM, ctx: TritonContext) -> int:
    try:
        reg = vm.vIP.to_triton_reg(ctx)
        return ctx.getConcreteRegisterValue(reg) if reg else 0  # type: ignore
    except Exception:
        return 0


def _read_vbase(vm: VM, ctx: TritonContext) -> int:
    try:
        reg = vm.vBASE.to_triton_reg(ctx)
        return ctx.getConcreteRegisterValue(reg) if reg else 0  # type: ignore
    except Exception:
        return 0
    try:
        reg = vm.vBASE.to_triton_reg(ctx)
        return ctx.getConcreteRegisterValue(reg) if reg else 0  # type: ignore
    except Exception:
        return 0


def _detect_feature(block: VmHandlerBlock, vm: VM, trace: TraceIndex) -> str:
    ctx = make_ctx()
    result: List[Instruction] = []
    started = False
    for _, snap in trace.iter_items():
        a = snap.addr_int()
        if not started:
            if a == block.start:
                started = True
            else:
                continue
        if a == block.end:
            break
        _sync_regs(ctx, snap)
        _sync_mem(ctx, snap)
        ctx.setConcreteMemoryAreaValue(a, snap.opcode_bytes())
        inst = Instruction(a, snap.opcode_bytes())
        ctx.processing(inst)  # type: ignore
        result.append(inst)
    return VmDispatchFeature.detect(block, vm, result, ctx) or "?"
