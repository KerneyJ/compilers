import cfg
import briltox86

def handle_call():
    pass

def handle_return():
    pass

def block_to_instrs(block: cfg.bb, reg_alloc: dict[str, str]) -> list[str]:
    ret = []
    for instr in block.instrs:
        if "op" in instr:
            ret += briltox86.map[instr["op"]](instr, reg_alloc)
        else:
            ret += briltox86.label(instr, reg_alloc)
    return ret

def gen_func(blocks: list[cfg.bb], reg_alloc: dict[str, str]):
    x86func = []
    instrs_by_block = {}
    for block in blocks:
        instrs_by_block[block.name] = block_to_instrs(block, reg_alloc)
        print(instrs_by_block[block.name])


def gen_prog():
    pass
