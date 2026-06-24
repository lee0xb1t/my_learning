from trace_types import *
from triton import *

def load_trace(filepath: str) -> TraceIndex:
    """从trace文件解析指令快照, 返回TraceIndex"""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = lines[2:]  # skip first 2 header lines

    inst_addr = ''
    inst_seq = -1
    state = 2
    inst_dict = {}
    for line in lines:
        if '^addr' in line:
            if not (state == 1 or state == 2):
                raise Exception('state error')
            inst_line_split = line.split(',')
            inst_addr = inst_line_split[0].split(':')[1]
            size = inst_line_split[1].split(':')[1]
            opcodes = inst_line_split[2].split(':')[1]
            opcodes = opcodes.split(' ')[0:-1]
            inst_seq += 1
            inst_dict[inst_seq] = {
                'addr': inst_addr,
                'size': int(size, 10),
                'opcodes': opcodes,
                'mems': []
            }
            state = 0

        elif '*regs' in line:
            if not state == 0:
                raise Exception('state error')
            regs_split = line.split(':')
            regs_split = regs_split[1].split('|')
            regs_split = regs_split[0:-1]
            inst_dict[inst_seq]['regs'] = {
                'eax': regs_split[0],
                'ecx': regs_split[1],
                'edx': regs_split[2],
                'ebx': regs_split[3],
                'esp': regs_split[4],
                'ebp': regs_split[5],
                'esi': regs_split[6],
                'edi': regs_split[7],
                'eflags': regs_split[8],
            }
            state = 1

        elif '*mem_addr' in line:
            if not state == 1:
                raise Exception('state error')
            mem_split = line.split(',')
            mem_addr = mem_split[0].split(':')[1]
            mem_val = mem_split[1].split(':')[1]
            mem_size = mem_split[2].split(':')[1]
            inst_dict[inst_seq]['mems'].append(
                {
                    'addr': mem_addr,
                    'val': mem_val,
                    'size': int(mem_size, 10),
                }
            )
            state = 2

    return TraceIndex.from_dict(inst_dict)


def update_args_sym(ctx:TritonContext):
    """
    符号化参数
    """

    esp_val = ctx.getConcreteRegisterValue(ctx.registers.esp) # type: ignore

    param1_addr = esp_val+4
    memory1 = MemoryAccess(param1_addr, 4)
    ctx.setConcreteMemoryValue(memory1, 1)

    param2_addr = esp_val+8
    memory2 = MemoryAccess(param2_addr, 4)
    ctx.setConcreteMemoryValue(memory2, 1)

    ctx.symbolizeMemory(memory1, 'param1')
    ctx.symbolizeMemory(memory2, 'param2')
    return


def sync_mem(ctx: TritonContext, inst: InstructionSnapshot):
    """
    检查Triton中的内存值是否正确
    如果不正确就更新
    跳过符号化内存, 避免setConcreteMemoryValue破坏符号表达式
    """
    for m in inst.mems:
        memory = MemoryAccess(m.addr_int(), m.size)
        if ctx.isMemorySymbolized(memory):
            continue
        sync_val = ctx.getConcreteMemoryValue(memory)
        if sync_val != m.val_int():
            ctx.setConcreteMemoryValue(memory, m.val_int())
    return

def sync_regs(ctx: TritonContext, inst: InstructionSnapshot):
    ctx_regs = ctx.registers  # type: ignore
    mapping = {
        ctx_regs.eax: 'eax',
        ctx_regs.ebx: 'ebx',
        ctx_regs.ecx: 'ecx',
        ctx_regs.edx: 'edx',
        ctx_regs.edi: 'edi',
        ctx_regs.esi: 'esi',
        ctx_regs.ebp: 'ebp',
        ctx_regs.esp: 'esp',
        ctx_regs.eflags: 'eflags',
    }
    for mapping_key, mapping_val in mapping.items():
        reg_val = ctx.getConcreteRegisterValue(mapping_key)
        if reg_val != inst.regs.get(mapping_val):
            if ctx.isRegisterSymbolized(mapping_key):
                continue
            ctx.setConcreteRegisterValue(mapping_key, inst.regs.get(mapping_val))
    return


def main():
    traces = load_trace("sample1.trace")
    with open('trace.json', 'w') as f:
        f.write(traces.to_json())

    ctx = TritonContext(ARCH.X86)

    ctx.setMode(MODE.CONSTANT_FOLDING, True)
    ctx.setMode(MODE.ALIGNED_MEMORY, True)
    ctx.setMode(MODE.AST_OPTIMIZATIONS, True)

    first_exec = True
    for _, inst in traces.iter_items():
        sync_regs(ctx, inst)
        sync_mem(ctx, inst)

        if first_exec:
            update_args_sym(ctx)
            first_exec = False

        ctx_inst: Instruction = Instruction(inst.addr_int(), inst.opcode_bytes())
        ctx.processing(ctx_inst) # type: ignore

    eax_expr = ctx.getRegisterAst(ctx.registers.eax) # type: ignore

    ast    = ctx.getAstContext()
    unro   = ast.unroll(eax_expr)
    synth  = ctx.synthesize(eax_expr)
    ppast1 = (str(unro) if len(str(unro)) < 100 else 'In: %s ...' %(str(unro)[0:100]))
    ppast2 = (str(synth) if len(str(synth)) < 100 else 'In: %s ...' %(str(unro)[0:100]))

    print(f'[+] Return value: {hex(eax_expr.evaluate())}')
    print(f'[+] Devirt expr: {ppast1}')
    print(f'[+] Synth expr: {ppast2}\n')
    print(f'[+] LLVM IR ==============================\n')
    print(ctx.liftToLLVM(synth if synth else eax_expr)) # type: ignore
    print(f'[+] EOF LLVM IR ============================== ')
    return

if __name__ == '__main__':
    main()