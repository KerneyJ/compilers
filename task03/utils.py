def count(prog):
    return sum([len(f["instrs"]) for f in prog["functions"]])

def print_instrs(prog):
    for f in prog["functions"]:
        for instr in f["instrs"]:
            print(instr)
