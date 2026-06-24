# ============================================================
#  VMP Trace Analysis — entry point
# ============================================================
from trace_types import *
from vm_types import VM, VmHandlerBlock
from vm_emu import VmEmu, _read_bytecode, DispatchEvent


def load_trace(filepath: str) -> TraceIndex:
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = lines[2:]
    inst_addr, inst_seq, inst_dict = '', -1, {}
    state = 2
    for line in lines:
        if '^addr' in line:
            if state not in (1, 2): raise Exception('state error')
            parts = line.split(',')
            inst_addr, size = parts[0].split(':')[1], parts[1].split(':')[1]
            opcodes = parts[2].split(':')[1].split(' ')[0:-1]
            inst_seq += 1
            inst_dict[inst_seq] = {'addr': inst_addr, 'size': int(size, 10), 'opcodes': opcodes, 'mems': []}
            state = 0
        elif '*regs' in line:
            if state != 0: raise Exception('state error')
            regs = line.split(':')[1].split('|')[0:-1]
            inst_dict[inst_seq]['regs'] = {
                'eax': regs[0], 'ecx': regs[1], 'edx': regs[2], 'ebx': regs[3],
                'esp': regs[4], 'ebp': regs[5], 'esi': regs[6], 'edi': regs[7], 'eflags': regs[8],
            }
            state = 1
        elif '*mem_addr' in line:
            if state != 1: raise Exception('state error')
            parts = line.split(',')
            inst_dict[inst_seq]['mems'].append({
                'addr': parts[0].split(':')[1], 'val': parts[1].split(':')[1],
                'size': int(parts[2].split(':')[1], 10),
            })
            state = 2
    return TraceIndex.from_dict(inst_dict)


def main():
    trace = load_trace("sample2_all.trace")

    vm0 = VM.from_dict({'name': 'vm0', 'vIP': 'edi', 'vSP': 'esi', 'vREG': 'esp', 'vBASE': 'ebp'})
    vm0.dispatchers.append(VmHandlerBlock(name='vmEntry', start=0x944270, end=0x94e4fa))

    vm1 = VM.from_dict({'name': 'vm1', 'vIP': 'ebp-', 'vSP': 'edi', 'vREG': 'esp', 'vBASE': 'esi'})

    emu = VmEmu(vm0, trace)

    print(f'\n[+] Full VM Instruction Stream:')
    for ve in emu.run_vm():
        for dv in ve.run_dispatch():
            _print_event(dv, ve.vm, ve.ctx)
    print(f'\n[+] vm0 execution counts:')
    for block, count in emu.exec_counts():
        print(f'    [{block.name}] executed x{count}')

    vm1.saved_context = vm0.saved_context
    emu.vm = vm1
    print(f'\n  --- vm1 ---')
    for ve in emu.run_vm():
        for dv in ve.run_dispatch():
            _print_event(dv, ve.vm, ve.ctx)
    print(f'\n[+] vm1 execution counts:')
    for block, count in emu.exec_counts():
        print(f'    [{block.name}] executed x{count}')


def _print_event(ev: DispatchEvent, vm: VM, ctx):
    tag = ev.feature.split(' ')[0] if ev.feature else '?'
    addr = f"({hex(ev.block.start)} - {hex(ev.block.end)})"
    vip = ev.state_trace.vip_in if ev.state_trace else ev.vip
    show_detail = tag != '?' and vip > 0
    nbytes_raw = ev.state_trace.vip_delta() if ev.state_trace else 5
    nbytes = min(abs(nbytes_raw), 8) if nbytes_raw else 5
    direction = "↓" if vm.vip_dir < 0 else ("↑" if vm.vip_dir > 0 else "")
    vip_str = f" @0x{vip:x}" if show_detail else ""
    if 0 < abs(nbytes_raw) <= 8:
        bc = _read_bytecode(ctx, vip, abs(nbytes_raw)) if show_detail and ctx else ""
    else:
        bc = ""
    bc_str = f" | {bc}" if bc else ""
    delta_str = f" {direction}{abs(nbytes_raw)}" if show_detail and direction and nbytes_raw else ""
    operand = _get_operand(ev)
    print(f'    [{ev.seq:04d}] {ev.block.name:<16} {tag:<10} {operand:<12} {vip_str:>14}{bc_str:<24}{delta_str} {addr}')


def _get_operand(ev) -> str:
    parts = ev.feature.split() if ev.feature else []
    if len(parts) > 1 and parts[1].startswith('0x') and 'Jmp' not in parts[0]:
        return parts[1]
    if ev.regid >= 0:
        return f"0x{ev.regid:02x}"
    if ev.vbase > 0 and 'Jmp' in ev.feature:
        return f"0x{ev.vbase:x}"
    return ""


if __name__ == '__main__':
    main()
