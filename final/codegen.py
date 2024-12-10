import cfg
import briltox86

def handle_call():
    pass

def handle_return():
    pass

def gen(blocks: list[cfg.bb], reg_alloc: dict[str, str]):
    x86func = []
    for block in blocks:
        print(block.name, reg_alloc)
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            # print(instr)
