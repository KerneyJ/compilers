import cfg
import briltox86

def insert_funcs(): # TODO add header functions for
    pass

def handle_call():
    pass

def handle_return():
    pass

def block_to_instrs(block: cfg.bb, reg_alloc: dict[str, str]) -> list[str]:
    ret = []
    if "entry" in block.name:
        if block.func_name == "main":
            ret += [f"_start:"]
        else:
            ret += [f"{block.func_name}:"]
    for instr in block.instrs:
        if "op" in instr:
            ret += briltox86.map[instr["op"]](instr, reg_alloc)
        else:
            ret += briltox86.label(instr, reg_alloc)
    return ret

def gen_func(blocks: list[cfg.bb], reg_alloc: dict[str, str]):
    x86func = []
    instrs_by_block = []
    for block in blocks:
        instrs_by_block.append((block.num, block_to_instrs(block, reg_alloc)))

    sorted_blocks = sorted(instrs_by_block, key=lambda x: x[0])
    for num, block_instrs in sorted_blocks:
        x86func += block_instrs
    return x86func

def gen_prog():
    pass
