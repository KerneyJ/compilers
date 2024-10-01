import json
import sys

def is_pure(instr):
    if instr["op"] in ["add", "mul", "sub", "eq", "lt", "gt", "le", "ge", "not", "and", "or", "const"]:
        return True
    return False

def gdce(function):
    con = True
    while con:
        used = []
        con = False
        for instr in function["instrs"]:
            if instr is None:
                continue
            if "args" in instr.keys():
                used += instr["args"]

        for idx in range(len(function["instrs"])):
            instr = function["instrs"][idx]
            if instr is None:
                continue
            if not "dest" in instr.keys():
                continue
            if (not instr["dest"] in used) and is_pure(instr):
                function["instrs"][idx] = None
                con = True

    function["instrs"] = [instr for instr in function["instrs"] if not instr is None]
    return function

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    prog["functions"] = [gdce(f) for f in functions]
    json.dump(prog, sys.stdout, indent=2)
