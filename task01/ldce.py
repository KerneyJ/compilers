import json
import sys
from gdce import gdce

def ldce(function):
    con = True
    while con:
        con = False
        unused = {}
        for instr in function["instrs"]:
            if instr is None:
                continue
            if "args" in instr.keys():
                for arg in instr["args"]:
                    if arg in unused.keys():
                        del unused[arg]
            if "dest" in instr.keys():
                if instr["dest"] in unused.keys():
                    del unused[instr["dest"]]
                unused[instr["dest"]] = instr

        for var, instr in enumerate(unused):
           function["instrs"][function["instrs"].index(unused[instr])] = None

        if unused == {}:
            con = False

    function["instrs"] = [instr for instr in function["instrs"] if not instr is None]
    return function

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    count = sum([len(f["instrs"]) for f in prog["functions"]])
    # print(count)
    functions = prog["functions"]
    functions = [gdce(f) for f in functions]
    prog["functions"] = [ldce(f) for f in functions]
    json.dump(prog, sys.stdout, indent=2)
