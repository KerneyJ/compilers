import json
import sys
import cfg

def liveness(block, ll= []):
    gl = []
    kl = []
    for instr in block.instrs:
        if "op" not in instr:
            continue
        if instr["op"] == "br":
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

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    for name in blocks:
        block = blocks[name]
        live = liveness(block)
        print(live)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
