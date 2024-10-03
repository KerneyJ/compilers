import json
import sys
import gdce
import cfg

def perform_op(instr):
    if instr["op"] == "add":
        return instr["args"][0][1] + instr["args"][1][1]
    elif instr["op"] == "mul":
        return instr["args"][0][1] * instr["args"][1][1]
    elif instr["op"] == "sub":
        return instr["args"][0][1] - instr["args"][1][1]
    elif instr["op"] == "div":
        return instr["args"][0][1] / instr["args"][1][1]
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
            if instr["op"] == "id" or instr["op"] == "print":
                continue
            if instr["op"] == "const" and instr["dest"] not in ct:
                if type(instr["value"]) == bool:
                    ct[instr["dest"]] = "true" if instr["value"] else "false"
                else: # is an int
                    ct[instr["dest"]] = instr["value"]
                change = True
            if "args" not in instr:
                continue
            perform = True
            for arg in instr["args"]:
                if arg in ct:
                    instr["args"][instr["args"].index(arg)] = (arg, ct[arg])
                if type(arg) != tuple or type(arg[1]) != int:
                    perform = False
            if perform:
                value = perform_op(instr)
                block.instrs[idx] = {'dest': instr["dest"], 'op': 'const', 'type': 'int', 'value': value}
                ct[instr["dest"]] = value
                change = True

    # add a pass to fix all the mangled instructions(fix args)
    for idx in range(len(block.instrs)):
        if "args" not in block.instrs[idx]:
            continue
        for jdx in range (len(block.instrs[idx]["args"])):
            arg = block.instrs[idx]["args"][jdx]
            if type(arg) != tuple:
                continue
            if type(arg[1]) == str:
                block.instrs[idx]["args"][jdx] = arg[0]
            elif type(arg[1]) == int:
                block.instrs[idx]["args"][jdx] = arg[0]
            else:
                raise Exception(f"Unexpected type: {type(args[1])} in args for instruction {block.instrs[idx]}")

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

    cfg.reconstruct_prog(blocks, prog)
    prog["functions"] = [gdce.gdce(f) for f in prog["functions"]]
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)
