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

def defs(blocks):
    map = {}
    for name in blocks:
        block = blocks[name]
        for instr in block.instrs:
            if "dest" not in instr:
                continue
            dest = instr["dest"]
            if dest in map:
                map[dest].add(block)
            else:
                map[dest] = set([block])

    print(map)
    return map

def to_ssa(blocks):
    for name in blocks:
        block = blocks[name]
        cfg.dominate(block)

    for name in blocks:
        df = cfg.df_b(blocks[name], blocks)
        # print(name, [block.name for block in blocks[name].dominates])

    defs(blocks)

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
