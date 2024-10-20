import json
import sys
import cfg
import gdce
import utils

def insert_phi(dest: str, typ: str, labels: list[str], args: list[str], block: cfg.bb):
    instr = {"op": "phi",
             "dest": dest,
             "type": typ,
             "labels": labels,
             "args": args}
    bb.instrs.insert(0, instr)

def modify_phi(block: cfg.bb):
    pass

def find_phi(var: str, block: cfg.bb):
    for idx in range(len(block.instrs)):
        instr = block.instrs[idx]
        if "op" not in instr:
            continue
        if instr["op"] != "phi":
            continue
        if instr["dest"] == var:
            return idx
    return -1


def get_defs(blocks: dict[str, cfg.bb]):
    map = {}
    for name in blocks:
        block = blocks[name]
        for instr in block.instrs:
            if "dest" not in instr:
                continue
            dest = instr["dest"]
            typ = instr["type"]
            if dest in map:
                map[dest][1].add(block)
            else:
                map[dest] = (typ, set([block]))

    return map

def to_ssa(blocks):
    for name in blocks:
        block = blocks[name]
        cfg.dominate(block)

    dfs = {}
    for name in blocks:
        df = cfg.df_b(blocks[name], blocks)
        dfs[name] = df

    print(dfs)
    defs = get_defs(blocks)
    for var in defs:
        print(var, end=": ")
        for def_block in defs[var][1]:
            print(def_block.name, end=" => ")
            for df_block in dfs[def_block.name]:
                print(df_block.name, end=", ")
            print()
        print()

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)

    to_ssa(blocks)

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
#    json.dump(prog, sys.stdout, indent=2)
