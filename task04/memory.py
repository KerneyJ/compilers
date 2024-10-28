import json
import sys
import cfg
import utils

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

def meet_parents(parent_maps: list[dict[str, list[int]]]):
    var_to_mem = {}
    for parent in parent_maps:
        parent_map = parent_maps[parent]
        for var in parent_map:
            if var in var_to_mem:
                var_to_mem[var] += parent_map[var]
            else:
                var_to_mem[var] = parent_map[var]

    for var in var_to_mem:
        var_to_mem[var] = list(set(var_to_mem[var])) # remove dups
    return var_to_mem

def analyze_block(block: cfg.bb, parent_var_map: dict[str, list[int]], args):
    if args:
        for arg in args:
            if "ptr" not in arg["type"]:
                continue
            if arg["name"] not in block.var_to_mem:
                block.var_to_mem[arg["name"]] = [cfg.bb.COUNTER]
                cfg.bb.COUNTER += 1

    for var in parent_var_map:
        if var in block.var_to_mem:
            block.var_to_mem[var] += parent_var_map[var]
        else:
            block.var_to_mem[var] = parent_var_map[var]

    changed = False
    for idx in range(len(block.instrs)):
        instr = block.instrs[idx]
        if "op" not in instr:
            continue
        if "alloc" in instr["op"] or ("call" in instr["op"] and "ptr" in instr["type"]):
            # name allocation and put it in the var map
            dest = instr["dest"]
            if dest in block.var_to_mem:
                continue
            block.var_to_mem[dest] = [cfg.bb.COUNTER]
            cfg.bb.COUNTER += 1
            changed = True
        elif "id" in instr["op"]:
            dest = instr["dest"]
            arg = instr["args"][0]
            if arg not in block.var_to_mem:
                continue
            if dest in block.var_to_mem:
                block.var_to_mem[dest] += block.var_to_mem[arg]
            else:
                block.var_to_mem[dest] = block.var_to_mem[arg]
            changed = True
        elif "ptradd" in instr["op"]:
            dest = instr["dest"]
            ptr = instr["args"][0]
            if ptr not in block.var_to_mem:
                raise Exception(f"Pointer add on undefined pointer {ptr} in {block.name}")
            if dest in block.var_to_mem:
                block.var_to_mem[dest] += block.var_to_mem[ptr]
            else:
                block.var_to_mem[dest] = block.var_to_mem[ptr]
            changed = True
        elif "load" in instr["op"]:
            arg = instr["args"][0] # need another data structure to keep track of which variable are loaded and where
            if arg not in block.var_to_mem:
                raise Exception(f"Load from undefined pointer {arg}, {block.var_to_mem}, {block.name}")
            block.live_alloc += block.var_to_mem[arg]
        elif "store" in instr["op"]: # check if what is being stored is a pointer
            ptr, val = instr["args"]
            if ptr not in block.var_to_mem:
                raise Exception("Storing to an invalid pointer")
            if val in block.var_to_mem: # storing pointer in a pointer
                block.var_to_mem[ptr] += block.var_to_mem[val]
                changed = True
                continue

    return changed

def alias(blocks: dict[str, cfg.bb], args: dict[str, list]):
    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        meet = meet_parents({parent.name: parent.var_to_mem for parent in block.parents})
        changed = analyze_block(block, meet, args[block.func_name] if "entry" in block.name else None)
        if changed:
            for kid in block.kids:
                if kid not in stack:
                    stack.append(kid)

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

    # remove dead stores
    for name in blocks:
        block = blocks[name]
        dead_store(block)
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "dead" not in instr:
                continue
            if instr["dead"]:
                block.instrs[idx] = None
        block.instrs = [instr for instr in block.instrs if instr] # clean the nones

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
