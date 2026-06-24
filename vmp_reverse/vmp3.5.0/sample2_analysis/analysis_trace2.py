from typing import Iterator
from trace_types import *
from triton import *

split_addr = 0xa18567

def load_trace(filepath: str) -> List[TraceIndex]:
    """从trace文件解析指令快照, 返回TraceIndex"""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = lines[2:]  # skip first 2 header lines

    inst_addr = ''
    inst_seq = -1
    state = 2
    insts = []
    inst_dict = {}
    for line in lines:
        if inst_seq != -1 and f'^addr:{hex(split_addr)}' in line:
            # skip first
            insts.append(TraceIndex.from_dict(inst_dict))
            inst_dict = {}

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

    return insts


def update_args_sym(ctx:TritonContext):
    """
    符号化参数
    """

    # esp_val = ctx.getConcreteRegisterValue(ctx.registers.esp) # type: ignore

    # param1_addr = esp_val+4
    # memory1 = MemoryAccess(param1_addr, 4)
    # ctx.setConcreteMemoryValue(memory1, 1)

    # param2_addr = esp_val+8
    # memory2 = MemoryAccess(param2_addr, 4)
    # ctx.setConcreteMemoryValue(memory2, 1)

    # ctx.symbolizeMemory(memory1, 'param1')
    # ctx.symbolizeMemory(memory2, 'param2')
    return

def update_regs_sym(ctx:TritonContext):
    """
    符号化参数
    """

    if not ctx.isRegisterSymbolized(ctx.registers.eax):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.eax)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.ebx):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.ebx)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.ecx):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.ecx)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.edx):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.edx)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.edi):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.edi)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.esi):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.esi)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.ebp):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.ebp)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.esp):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.esp)    # type: ignore

    if not ctx.isRegisterSymbolized(ctx.registers.eflags):      # type: ignore
        ctx.symbolizeRegister(ctx.registers.eflags)    # type: ignore

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
        if not ctx.isMemorySymbolized(memory):
            ctx.symbolizeMemory(memory, m.addr)
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

            if not ctx.isRegisterSymbolized(mapping_key):
                ctx.symbolizeRegister(mapping_key, mapping_val)
    return

def emu(ctx: TritonContext, trace: TraceIndex) -> Iterator[Tuple[InstructionSnapshot, Instruction]]:
    first_exec = True
    for _, inst in trace.iter_items():
        sync_regs(ctx, inst)
        sync_mem(ctx, inst)

        # update_regs_sym(ctx)

        if first_exec:
            update_args_sym(ctx)
            first_exec = False

        ctx_inst: Instruction = Instruction(inst.addr_int(), inst.opcode_bytes())
        ctx.processing(ctx_inst) # type: ignore

        yield (inst, ctx_inst)

def walk(node):
    yield node
    for c in node.getChildren():
        yield from walk(c)

def calc_expr(ctx: TritonContext, reg, syth=True):
    expr = ctx.getRegisterAst(reg)

    ast    = ctx.getAstContext()
    unro   = ast.unroll(expr)
    synth  = ctx.synthesize(expr)
    ppast1 = (str(unro) if len(str(unro)) < 100 else 'In: %s ...' %(str(unro)[0:100]))
    ppast2 = (str(synth) if len(str(synth)) < 100 else 'In: %s ...' %(str(unro)[0:100]))

    print(f'[+] Return value: {hex(expr.evaluate())}')
    print(f'[+] Devirt expr: {ppast1}')
    print(f'[+] Synth expr: {ppast2}\n')
    print(f'[+] LLVM IR ==============================\n')
    if syth:
        print(ctx.liftToLLVM(synth if synth else expr)) # type: ignore
    else:
        print(ctx.liftToLLVM(expr)) # type: ignore
    print(f'[+] EOF LLVM IR ============================== ')
    return

def main():
    traces = load_trace("sample2_0x68567.trace")

    # i=0
    # for trace in traces:
    #     with open(f'sample2_0x68567_split/trace{i}.json', 'w') as f:
    #         f.write(trace.to_json())
    #     i+=1

    ctx = TritonContext(ARCH.X86)

    ctx.setMode(MODE.CONSTANT_FOLDING, True)
    ctx.setMode(MODE.ALIGNED_MEMORY, True)
    ctx.setMode(MODE.AST_OPTIMIZATIONS, True)

    # f = open(f'sample2_0x68567_result/test.txt', 'w')

    ctx.taintRegister(ctx.registers.esi)

    i=0
    for trace in traces:
        for (inst, ctx_inst) in emu(ctx, trace):
            # if inst.addr_int() == 0xa11687:
            #     ctx.taintRegister(ctx.registers.esi)

            print('%s' %(str(ctx_inst)))
            # f.write(f'{str(ctx_inst)}\n')

            # if ctx_inst.isTainted():
                # print('[  tainted] %s' %(str(ctx_inst)))
                # f.write(f'[  tainted] {str(ctx_inst)}\n')
            # else:
                # print('[untainted] %s' %(str(ctx_inst)))
        # f.write(f'------------------\n')
        print('------------------')
        
        i+=1
        if i == 5:
            break

    esi_expr = ctx.getRegisterAst(ctx.registers.esi) # type: ignore
    calc_expr(ctx, esi_expr)
    
    return


def main_ir():
    traces = load_trace("sample2_0x68567.trace")

    i=0
    for trace in traces:
        ctx = TritonContext(ARCH.X86)

        ctx.setMode(MODE.CONSTANT_FOLDING, True)
        ctx.setMode(MODE.ALIGNED_MEMORY, True)
        ctx.setMode(MODE.AST_OPTIMIZATIONS, True)
        
        for (inst, ctx_inst) in emu(ctx, trace):
            # print('%s' %(str(ctx_inst)))
            pass

        
        print('\n==================== ESI ====================')
        calc_expr(ctx, ctx.registers.esi, False) # type: ignore

        print('\n==================== EDI ====================')
        calc_expr(ctx, ctx.registers.edi, False) # type: ignore
        
        print('\n\n')
        
        i+=1
        if i == 5:
            break
    
    return

if __name__ == '__main__':
    main_ir()