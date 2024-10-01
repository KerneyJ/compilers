import json
import sys
import gdce
import cfg

def perform_op(instr):
    if instr["op"] == "add":
        return instr["args"][0] + instr["args"][1]
    elif instr["op"] == "mul":
        return instr["args"][0] * instr["args"][1]
    elif instr["op"] == "sub":
        return instr["args"][0] - instr["args"][1]
    elif instr["op"] == "div":
        return instr["args"][0] / instr["args"][1]
    else:
        raise Exception(f"Does not support instruction: {instr}")

def constprop(block, ct = {}):
    change = True
    while(change):
        change = False
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "op" not in instr:
                continue
            if instr["op"] == "const" and instr["dest"] not in ct:
                ct[instr["dest"]] = instr["value"]
                change = True
            if "args" not in instr:
                continue
            const = True
            for arg in instr["args"]:
                if arg in ct:
                    instr["args"][instr["args"].index(arg)] = ct[arg]
                if type(arg) != int:
                    const = False
            if const:
                value = perform_op(instr)
                block.instrs[idx] = {'dest': instr["dest"], 'op': 'const', 'type': 'int', 'value': value}
                ct[instr["dest"]] = value
                change = True
    return block, ct

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        inp = block.gather_parent_ct()
        block, out = constprop(block, inp)
        if out != inp:
            for kid in block.kids:
                if kid not in stack:
                    stack.append(kid)
        block.const_table = out

    prog["functions"] = cfg.reconstruct_prog(blocks)
    prog["functions"] = [gdce.gdce(f) for f in prog["functions"]]
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
