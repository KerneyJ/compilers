import json
import sys
import cfg
import utils

def live(block, ll = []):
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

def live_analysis(blocks):
    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        out = block.gather_child_ll()
        inp = live(block, out)
        out.sort()
        inp.sort()
        if out != inp:
            for parent in block.parents:
                if parent not in stack:
                    stack.append(parent)
        block.live_list = inp

def instr_liveness(blocks):
    live_analysis(blocks) # performs block level liveness analysis
    block_list = [blocks[name] for name in blocks]
    block_list.sort()
    seen = {} # maps function names to seen variables
    for name in blocks:
        if "entry" not in name:
            continue
        seen[blocks[name].func_name] = set()

    for block in block_list:
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "dest" in instr and instr["dest"] not in seen[block.func_name]:
                seen[block.func_name].add(instr["dest"])
            block.instrs[idx]["live_vars"] = seen[block.func_name] & set(block.live_list)

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    live_analysis(blocks)

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
