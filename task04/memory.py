import json
import sys
import cfg
import utils

def dead_store():
    pass

def meet_parents(parent_maps: list[dict[str, list[int]]]):
    var_to_mem = {}
    for parent_map in parent_maps:
        for var in parent_map:
            if var in var_to_mem:
                var_to_mem[var] += parent_map[var]
            else:
                var_to_mem[var] = parent_map[var]
    for var in var_to_mem:
        var_to_mem[var] = list(set(var_to_mem[var])) # remove dups
    return var_to_mem

def analyze_block(block: cfg.bb, old_var_to_mem: dict[str, list[int]], parent_var_map: dict[str, list[int]], args):
    var_to_mem = {}
    if args:
        for arg in args:
            if "ptr" not in arg["type"]:
                continue
            if arg["name"] in old_var_to_mem:
                var_to_mem[arg["name"]] = old_var_to_mem[arg["name"]]
            else:
                var_to_mem[arg["name"]] = [cfg.bb.COUNTER]
                cfg.bb.COUNTER += 1
    var_to_mem |= parent_var_map

    for instr in block.instrs:
        if "op" not in instr:
            continue

        if "alloc" in instr["op"]:
            # name allocation and put it in the var map
            dest = instr["dest"]
            var_to_mem[dest] = [cfg.bb.COUNTER]
            cfg.bb.COUNTER += 1
        elif "id" in instr["op"]:
            dest = instr["dest"]
            arg = instr["args"][0]
            if arg not in var_to_mem:
                continue
            var_to_mem[dest] = var_to_mem[arg]
        elif "ptradd" in instr["op"]:
            dest = instr["dest"]
            ptr = instr["args"][0]
            if ptr not in var_to_mem:
                raise Exception("Pointer add on undefined pointer")
            var_to_mem[dest] = var_to_mem[ptr]
        elif "load" in instr["op"]:
            arg = instr["args"][0] # need another data structure to keep track of which variable are loaded and where
        elif "store" in instr["op"]: # check if what is being stored is a pointer
            ptr, val = instr["args"]
            if ptr not in var_to_mem:
                raise Exception("Storing to an invalid pointer")
            if val in var_to_mem: # storing pointer in a pointer
                var_to_mem[ptr] += val_to_mem[val]
    return var_to_mem

def alias(blocks: dict[str, cfg.bb], args: dict[str, list]):
    block_mem_info = {}
    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        meet = meet_parents([block_mem_info[parent.name] for parent in block.parents if parent.name in block_mem_info])
        var_map = analyze_block(block, block_mem_info[block.name] if block.name in block_mem_info else {}, meet, args[block.func_name] if "entry" in block.name else None)
        if block.name not in block_mem_info or var_map != block_mem_info[block.name]:
            block_mem_info[block.name] = var_map
            for kid in block.kids:
                if kid not in stack:
                    stack.append(kid)
    print(block_mem_info)


def opt(prog):
    blocks = {}
    args = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)
        if "args" in func:
            args[func["name"]] = func["args"]
        else:
            args[func["name"]] = []

    alias(blocks, args)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
