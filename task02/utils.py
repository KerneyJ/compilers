def count(prog):
    return sum([len(f["instrs"]) for f in prog["functions"]])
