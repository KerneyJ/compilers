import json
import sys
import cfg
import gdce
import ssa
import utils

def get_loops(entry: cfg.bb, blocks: dict[str, cfg.bb]):
    loops = [] # each loop is a pair of [loop_header, loop_tail]
    stack = [entry] # all functions should have a entry block
    visited = []
    while stack:
        block = stack.pop(0)
        visited.append(block)
        for kid in block.kids:
            if kid in visited and block in kid.dominates:
                loops.append((kid, block))
                continue
            stack.append(kid)
    # maybe duplicates could be a problem???
    return loops

# for these current uses head should always be the loop head
def collect_defs(inp: cfg.bb, head: cfg.bb): # collects defs from block up to some head(head most dominate b)
    defs = []
    stack = [b for b in inp.parents] # init stack to parents of b
    while stack:
        block = stack.pop(0)
        if block not in head.dominates or block == head: # if block is not dominated by the head then we do not consider it
            continue
        block_defs = ssa.get_def(block)
        defs += block_defs
        for parent in block.parents:
            stack.append(parent)
    return [d[0] for d in defs]


def move_invariant(block: cfg.bb, loop_head: cfg.bb):
    change = True
    while change:
        change = False
        defs_so_far = collect_defs(block, loop_head)
        print(defs_so_far)
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "dest" not in instr or "args" not in instr:
                continue
            if instr["op"] == "phi":
                continue
            args = instr["args"]
            dest = instr["dest"]
            # print(dest, args)

def licm(blocks: dict[str, cfg.bb], functions: dict[str, dict[str, cfg.bb]]):
    loops = [] # a list of pairs where the pair[0] = loop header, pair[1] = last block
    for name in functions:
        func = functions[name]
        args, blocks = func
        entry = blocks["entry" + "@" + name]
        floops = get_loops(entry, blocks)
        loops += floops

    for loop in loops:
        head, tail = loop
        print("processing this loop", head.name, tail.name)
        # if it dominates the tail it must execute
        considered_blocks = set()
        stack = [head]
        while stack:
            block = stack.pop(0)
            if tail in block.dominates:
                considered_blocks.add(block)
                if block == tail:
                    continue
                for kid in block.kids:
                    stack.append(kid)
            else:
                for kid in block.kids:
                    if kid not in block.dominates:
                        stack.append(kid)

        for block in considered_blocks:
            move_invariant(block, head)
        # if block does not dominate tail then I should consider all the children of block that it does not dominate
        print()

def opt(prog):
    blocks = {}
    functions = {}
    for func in prog["functions"]:
        func_blocks = cfg.make_bb(func)
        blocks |= func_blocks
        if "args" in func:
            functions[func["name"]] = (func["args"], func_blocks)
        else:
            functions[func["name"]] = ([], func_blocks)

    ssa.to_ssa(blocks, functions)
    licm(blocks, functions)

    cfg.reconstruct_prog(blocks, prog)
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
