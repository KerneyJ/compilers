import json
import sys
import cfg
import utils

def filter_vtm(block: cfg.bb, blocks: list[cfg.bb]):
    pass

def dead_store(block: cfg.bb):
    live_alloc = block.live_alloc
    for idx in range(len(block.instrs)):
        instr = block.instrs[idx]
        if "op" not in instr:
            continue
        if "store" not in instr["op"]:
            continue
        ptr = instr["args"][0]
        points_to = block.var_to_mem[ptr]
        if not (set(live_alloc) & set(points_to)):
            block.instrs[idx]["dead"] = True
        else:
            block.instrs[idx]["dead"] = False

def meet_parents(block: cfg.bb):
    var_to_mem = {}
    for parent in block.parents:
        parent_map = parent.var_to_mem
        for var in parent_map:
            if var in var_to_mem:
                var_to_mem[var] |= parent_map[var]
            else:
                var_to_mem[var] = parent_map[var]

    for parent in block.ret_parents:
        parent_map = parent.var_to_mem
        term = parent.term
        if "args" not in term:
            continue
        ret_vars = term["args"]
        for var in parent_map:
            if var not in ret_vars:
                continue
            if var in var_to_mem:
                var_to_mem[var] |= parent_map[var]
            else:
                var_to_mem[var] = parent_map[var]

    return var_to_mem

def analyze_block(block: cfg.bb, parent_var_map: dict[str, list[int]], args):
    # Return Codes:
    # 0 => Nothing has changed
    # 1 => Something has Changed
    # 2 => not enough information
    ret = 0
    if args:
        for idx in range(len(args)):
            arg = args[idx]
            if "ptr" not in arg["type"]:
                continue
            for parent in block.call_parents:
                if parent.func_name == block.func_name:
                    continue
                term = parent.term
                arg_in_parent = term["args"][idx]
                if arg_in_parent not in parent.var_to_mem:
                    return 2
                block.var_to_mem[arg["name"]] = parent.var_to_mem[arg_in_parent]
                ret = 1

    for var in parent_var_map:
        if var in block.var_to_mem:
            block.var_to_mem[var] |= parent_var_map[var]
        else:
            block.var_to_mem[var] = parent_var_map[var]

    for idx in range(len(block.instrs)):
        instr = block.instrs[idx]
        if "op" not in instr:
            continue
        if "alloc" in instr["op"] or ("call" in instr["op"] and ("type" in instr and "ptr" in instr["type"])):
            # name allocation and put it in the var map
            dest = instr["dest"]
            if dest in block.var_to_mem:
                continue
            block.var_to_mem[dest] = set([(block.name, cfg.bb.COUNTER)])
            cfg.bb.COUNTER += 1
            ret = 1
        elif "id" in instr["op"]:
            dest = instr["dest"]
            arg = instr["args"][0]
            if arg not in block.var_to_mem:
                continue
            if dest in block.var_to_mem:
                block.var_to_mem[dest] |= block.var_to_mem[arg]
            else:
                block.var_to_mem[dest] = block.var_to_mem[arg]
            ret = 1
        elif "ptradd" in instr["op"]:
            dest = instr["dest"]
            ptr = instr["args"][0]
            if ptr not in block.var_to_mem:
                return 0 # raise Exception(f"Pointer add on undefined pointer {ptr} in {block.name}")
            if dest in block.var_to_mem:
                block.var_to_mem[dest] |= block.var_to_mem[ptr]
            else:
                block.var_to_mem[dest] = block.var_to_mem[ptr]
            ret = 1
        elif "load" in instr["op"]:
            arg = instr["args"][0] # need another data structure to keep track of which variable are loaded and where
            if arg not in block.var_to_mem:
                return 0 # raise Exception(f"Load from undefined pointer {arg}, {block.var_to_mem}, {block.name}")
            block.live_alloc |= block.var_to_mem[arg]
            for b in block.reachable:
                b.live_alloc |= block.var_to_mem[arg]
        elif "store" in instr["op"]: # check if what is being stored is a pointer
            ptr, val = instr["args"]
            if ptr not in block.var_to_mem:
                return 0 # raise Exception("Storing to an invalid pointer")
            if val in block.var_to_mem: # storing pointer in a pointer
                block.var_to_mem[ptr] |= block.var_to_mem[val]
                ret = 1
                continue
    return ret

def alias(blocks: dict[str, cfg.bb], args: dict[str, list]):
    # initial stack condition
    block_list = [blocks[name] for name in blocks]
    # find functions that are never called
    entry_blocks = [block for block in block_list if "entry" in block.name]
    uncalled_funcs = [block.func_name for block in entry_blocks if not block.call_parents and block.func_name != "main"]
    # delete call parents(prevents infinite loops) that are never invoked
    for block in block_list:
        block.call_parents = [parent for parent in block.call_parents if parent.func_name not in uncalled_funcs]
    # remove functions that are never called
    stack = [block for block in block_list if block.func_name not in uncalled_funcs]
    while stack:
        block = stack.pop(0)
        meet = meet_parents(block)
        ret = analyze_block(block, meet, args[block.func_name] if "entry" in block.name else None)
        if ret == 1:
            for kid in (block.kids + block.ret_kids + block.call_kids):
                if kid not in stack:
                    stack.append(kid)
        elif ret == 2:
            stack += [b for b in block_list if b.func_name == block.func_name]

def opt(prog):
    blocks = {}
    args = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)
        if "args" in func:
            args[func["name"]] = func["args"]
        else:
            args[func["name"]] = []
    cfg.make_crg(blocks)
    entry_main = blocks["entry@main"]
    for name in blocks:
        if name == "entry@main":
            continue
        block = blocks[name]
        block.reachable = set(cfg.reachable(entry_main, block))

    alias(blocks, args)
    #for name in blocks:
    #    print(name, blocks[name].live_alloc)

    # remove dead stores
#    for name in blocks:
#        block = blocks[name]
#        dead_store(block)
#        for idx in range(len(block.instrs)):
#            instr = block.instrs[idx]
#            if "dead" not in instr:
#                continue
#            if instr["dead"]:
#                block.instrs[idx] = None
#        block.instrs = [instr for instr in block.instrs if instr] # clean the nones

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
