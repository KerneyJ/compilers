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
        if set(block.live_list).symmetric_difference(set(inp)):
            for parent in block.parents:
                if parent not in stack:
                    stack.append(parent)
        block.live_list = inp

def instr_live(instr, ll):
    gl = []
    kl = []

    if "op" not in instr:
        return ll

    if "args" in instr:
        gl += instr["args"]
    if "f_args" in instr:
        gl += instr["f_args"]
    if "dest" in instr:
        kl.append(instr["dest"])

    kl = list(set(kl)) # remove dups
    gl = list(set(gl)) # remove dups
    ll = [var for var in ll if var not in kl]
    ll += gl
    return list(set(ll))

def instr_liveness(blocks): # TODO CURRENT PROBLEM IS NOT PLACING FUNCTION ARGS INTO LIVE LIST
    stack = [instr for name in blocks for instr in blocks[name].instrs]
    while stack:
        instr = stack.pop(0)
        out = instr["ii"].gather_child_ll()
        inp = instr_live(instr, out)
        if set(instr["ii"].live_list).symmetric_difference(set(inp)):
            for parent in instr["ii"].parents:
                stack.append(blocks[parent.bname].instrs[parent.idx])
        instr["ii"].live_list = inp
        instr["live_vars"] = inp

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
