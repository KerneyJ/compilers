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

def _rename_labels(blocks: list[cfg.bb]): # label names such as loop and done are very common so need to rename them for
    oname_nname = {} # maps old label names to new label names
   # change the names of the labels first
    for b in blocks:
        for instr in b.instrs:
            if "label" not in instr:
                continue
            label = instr["label"]
            oname_nname[label] = f"{b.func_name}_{label}"
    return oname_nname

# convert a basic block into a list of x86 instructions
def block_to_instrs(block: cfg.bb, reg_alloc: dict[str, str], rename_map: dict[str, str], clobber: set[str], vars_on_stack: int) -> list[str]:
    # list of instructions to be returned
    ret = []

    # special processing for the first block in a function
    if "entry" in block.name:
        # handle arguments passed down
        f_args = block.instrs[0]["f_args"]
        if len(f_args) > 0:
            if block.func_name == "main":
                for arg in f_args:
                    block.instrs.insert(0, {"op": "handle_scan_arg", "arg": arg})
            else:
                block.instrs.insert(0, {"op": "handle_args", "args": f_args})

        if len(clobber) > 0 and block.func_name != "main": # this(first condition, but good sanity check) should almost always be true
            block.instrs.insert(0, {"op": "handle_clobber_push", "clobber": clobber})

        # check for arguments that exist on the stack, if so allocate stack space
        if vars_on_stack > 0:
            block.instrs.insert(0, {"op": "handle_stack_vars_alloc", "num_vars": vars_on_stack})

        # change the name of the main function to _start for the linker
        if block.func_name == "main":
            ret += [f"_start:"]
        else:
            ret += [f"{block.func_name}:"]

    # if the block has a ret statement then we need to pop all of the clobbered variables off the stack
    if "op" in block.term and block.term["op"] == "ret" and block.func_name != "main" and len(clobber) > 0:
        block.instrs.insert(len(block.instrs), {"op": "handle_clobber_pop", "clobber": clobber})

    # fix the stack if there are stack vars
    if "op" in block.term and block.term["op"] == "ret" and block.func_name != "main" and vars_on_stack > 0:
        block.instrs.insert(len(block.instrs), {"op": "handle_stack_vars_free", "num_vars": vars_on_stack})

    # convert every instruction see briltox86
    for instr in block.instrs:
        instr["rename_map"] = rename_map
        if "op" in instr:
            ret += briltox86.map[instr["op"]](instr, reg_alloc)
        else:
            ret += briltox86.label(instr, reg_alloc)

    # return list of instructions
    return ret

def gen_func(blocks: list[cfg.bb], reg_alloc: dict[str, str], metadata): # metadata is a dictionary of bullshit
    # preprocessing using meta data
    func_name = blocks[0].func_name
    if func_name == "main":
        func_name = "_start"

    if "var_types" in metadata:
        var_types = metadata["var_types"]
        _instrument_prints(blocks, var_types)

    rename_map = _rename_labels(blocks)

    x86func = []
    instrs_by_block = []
    for block in blocks:
        instrs_by_block.append((block.num, block_to_instrs(block, reg_alloc, rename_map, metadata["clobber"], metadata["vars_on_stack"])))

    # put together all the basic blocks
    sorted_blocks = sorted(instrs_by_block, key=lambda x: x[0])
    for num, block_instrs in sorted_blocks:
        x86func += block_instrs

    if func_name == "_start":
        x86func.append("__stub__exit")

    decl = [
        f".globl {func_name}",
        f".type {func_name}, @function"
    ]

    return {"func": x86func, "decl": decl}
