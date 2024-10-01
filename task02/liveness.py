import json
import sys
import cfg
import gdce

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
    return ll

def mark_dead(block):
    ll = block.gather_child_ll()
    ll += block.live_list
    for idx in range(len(block.instrs)):
        instr = block.instrs[idx]
        if "dest" not in instr:
            continue
        if instr["dest"] not in ll:
            block.instrs[idx]["dest"] = ""
    return block

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        out = block.gather_child_ll()
        inp = liveness(block, out)
        if out != inp:
            for parent in block.parents:
                if parent not in stack:
                    stack.append(parent)
        block.live_list = inp

    for name in blocks:
        blocks[name] = mark_dead(blocks[name])

    prog["functions"] = cfg.reconstruct(blocks)
    prog["functions"] = [gdce.gdce(f) for f in prog["functions"]]

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
