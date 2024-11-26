import json
import sys
import cfg
import utils

def liveness(block, ll = []):
    gl = []
    kl = []
    for instr in block.instrs:
        if "op" not in instr:
            continue
        # go through each instruction and add the variables that
        # appear in args and subtract the variables that exist in dest
        if "args" in instr: # Gives me gen(b)
            gl += instr["args"]
        if "dest" in instr:
            kl.append(instr["dest"])

    kl = list(set(kl)) # remove dups
    gl = list(set(gl)) # remove dups
    ll = [var for var in ll if var not in kl]
    ll += gl
    return list(set(ll))

def get_defs(blocks: dict[str, cfg.bb], func_args: dict[str, list[str]]):
    block_list = [blocks[name] for name in blocks]
    block_list.sort()
    seen = {} # maps function names to seen variables
    for name in func_args:
        seen[name] = set()

    for block in block_list:
        defs = set()
        if "entry" in block.name:
            for arg in func_args[block.func_name]:
                defs.add(arg)
        for instr in block.instrs:
            if "dest" in instr and instr["dest"] not in seen[block.func_name]:
                defs.add(instr["dest"])
        block.defs = defs
        seen[block.func_name] |= defs

def instr_liveness(blocks):
    pass

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        out = block.gather_child_ll()
        inp = liveness(block, out)
        out.sort()
        inp.sort()
        if out != inp:
            for parent in block.parents:
                if parent not in stack:
                    stack.append(parent)
        block.live_list = inp

    for name in blocks:
        blocks[name] = mark_dead(blocks[name])

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
