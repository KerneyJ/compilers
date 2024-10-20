def count(prog):
    return sum([len(f["instrs"]) for f in prog["functions"]])

def print_instrs(prog):
    for f in prog["functions"]:
        for instr in f["instrs"]:
            print(instr)

if __name__ == "__main__":
    import json
    import sys
    prog = json.load(sys.stdin)
    # json.dump(prog, sys.stdout, indent=2)
    print_instrs(prog)
