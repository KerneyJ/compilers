import cfg
import briltox86

# misc helpers
def _instrument_prints(blocks: list[cfg.bb], var_types):
    for b in blocks:
        for idx in range(len(b.instrs)):
            instr = b.instrs[idx]
            if "op" not in instr:
                continue
            if "print" not in instr["op"]:
                continue
            vars = instr["args"]
            types = [var_types[var] for var in vars]
            b.instrs[idx]["var_types"] = types

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
            if instr["op"] == "print":
                pass
            ret += briltox86.map[instr["op"]](instr, reg_alloc)
        else:
            ret += briltox86.label(instr, reg_alloc)
    return ret

def gen_func(blocks: list[cfg.bb], reg_alloc: dict[str, str], metadata): # metadata is a dictionary of bullshit
    # preprocessing usin meta data
    if "var_types" in metadata:
        var_types = metadata["var_types"]
        _instrument_prints(blocks, var_types)

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
