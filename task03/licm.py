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

def pre_loop_defs(loop_head: cfg.bb):
    pld = []
    stack = [parent for parent in loop_head.parents if parent not in loop_head.dominates]
    while stack:
        block = stack.pop(0)
        for instr in block.instrs:
            if "dest" not in instr:
                continue
            pld.append(instr["dest"])
    return pld

def move_invariant(block: cfg.bb, loop_head: cfg.bb, preloop_instrs, preloop_vars):
    change = True
    while change:
        change = False
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "dest" not in instr or "args" not in instr:
                continue
            if instr["op"] == "phi":
                continue
            args = instr["args"]
            dest = instr["dest"]
            raised = True
            for arg in args:
                if arg not in preloop_vars:
                    raised = False
            if raised:
                preloop_instrs.append(instr)
                block.instrs[idx] = None
                preloop_vars.append(dest)
    block.instrs = [instr for instr in block.instrs if instr] # clear nones

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
        func_name = head.func_name
        preloop_instrs = [{"label": "_preheader"}]
        # pre_header = cfg.bb([], "_looppreheader@" + func_name, -1, func_name) # TODO need to figure out how to insert blocks
        # if it dominates the tail it must execute
        considered_blocks = set()
        preloop_vars = pre_loop_defs(head)
        stack = [head]
        while stack:
            block = stack.pop(0)
            if tail in block.dominates: # probably call considered blocks here because this is already because this has a notion of order
                move_invariant(block, head, preloop_instrs, preloop_vars)
                # considered_blocks.add(block)
                if block == tail:
                    continue
                for kid in block.kids:
                    stack.append(kid)
            else:
                for kid in block.kids:
                    if kid not in block.dominates:
                        stack.append(kid)
        # if block does not dominate tail then I should consider all the children of block that it does not dominate
        # construct new preaheader with these instructions
        name = "_preheader@" + func_name
        preheader = cfg.bb(preloop_instrs, name, -1, func_name)
        cfg.insert_block(preheader, head, blocks)
        blocks[name] = preheader
    return blocks

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
    blocks = licm(blocks, functions)

    cfg.reconstruct_prog(blocks, prog)
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
