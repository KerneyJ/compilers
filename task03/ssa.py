import json
import sys
import cfg
import gdce
import utils

def insert_phi(dest: str, typ: str, block: cfg.bb, def_blocks: list[cfg.bb]):
    def_preds = list(set(block.parents) & set(def_blocks)) # all predecessors of block that define dest
    if len(def_preds) < 2:
        return False
    labels = [block.name.split("@")[0] for block in def_preds]
    instr = {
             "args": [dest for i in range(len(labels))],
             "dest": dest,
             "labels": labels,
             "op": "phi",
             "type": typ,
             }

    if "label" in block.instrs[0]:
        block.instrs.insert(1, instr)
    else:
        block.instrs.insert(0, instr)
    return True

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

def find_var(var: str, vs: dict[str: (int, list[str])]):
    potentials = [base for base in vs if base in var]
    for p in potentials:
        stack = vs[p][1]
        for i in range(len(stack)):
            if stack[i] == var:
                return (p, i)
    return ()

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
                map[dest][1].append(block)
            else:
                map[dest] = (typ, [block])

    return map

def rename(entry: cfg.bb, params: dict[str, dict[str, str]], blocks: dict[str, cfg.bb]):

    def fresh_name(var: str, vs: dict[str: (int, list[str])]):
        if var not in vs:
            vs[var] = [1, [var + ".1"]]
            return vs[var][1][0]

        vs[var][0] += 1
        nn = var + "." + str(vs[var][0])
        vs[var][1].insert(0, nn)
        return nn # new_name

    var_stack = {}
    for param in params:
        var_name = param["name"]
        var_stack[var_name] = (0, [var_name])

    def rename_helper(block, var_stack):
        label = block.name.split("@")[0]

        for phi_idx in block.gather_phi():
            instr = block.instrs[phi_idx]
            dest = instr["dest"]
            new_name = fresh_name(dest, var_stack)
            instr["dest"] = new_name
            block.instrs[phi_idx] = instr

        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "op" in instr and instr["op"] == "phi":
                continue

            if "args" in instr:
                new_args = [var_stack[arg][1][0] for arg in instr["args"]]
                instr["args"] = new_args

            if "dest" in instr:
                new_name = fresh_name(instr["dest"], var_stack)
                instr["dest"] = new_name

            block.instrs[idx] = instr

        for kid in block.kids:
            kid_phis = kid.gather_phi()
            for phi_idx in kid_phis:
                phi = kid.instrs[phi_idx]
                dest = phi["dest"] if phi["dest"] in var_stack else find_var(phi["dest"], var_stack)
                if dest:
                    stack_pos = 0 # init to top of stack
                    if isinstance(dest, tuple):
                        stack_pos = dest[1]
                        dest = dest[0]
                    args = phi["args"]
                    arg_idx = phi["labels"].index(label)
                    args[arg_idx] = var_stack[dest][1][stack_pos]
                    phi["args"] = args
                    kid.instrs[phi_idx] = phi
                else:
                    args = phi["args"]
                    print(label, phi["labels"], phi)
                    arg_idx = phi["labels"].index(label)
                    args[arg_idx] = "__undefined"
                    phi["args"] = args
                    kid.instrs[phi_idx] = phi

        for kid in block.kids:
            if kid in block.dominates:
                rename_helper(kid, var_stack)

    rename_helper(entry, var_stack)

    # if len(rename) < len(blocks): raise Exception("Some block was not renamed")

def to_ssa(blocks: dict[str, cfg.bb], functions: dict[str, dict[str, cfg.bb]]):
    for name in blocks:
        block = blocks[name]
        cfg.dominate(block)

    dfs = {}
    for name in blocks:
        df = cfg.df_b(blocks[name], blocks)
        dfs[name] = df

    defs = get_defs(blocks)
    for var in defs:
        for def_block in defs[var][1]:
            for df_block in dfs[def_block.name]:
                if find_phi(var, df_block) < 0:
                    if insert_phi(var, defs[var][0], df_block, defs[var][1]):
                        defs[var][1].append(df_block)

    for name in functions:
        args, func = functions[name]
        entry = func["entry@" + name]
        rename(entry, args, func)


def test_ssa(prog):
    blocks = {}
    functions = {}
    for func in prog["functions"]:
        func_blocks = cfg.make_bb(func)
        blocks |= func_blocks
        if "args" in func:
            functions[func["name"]] = (func["args"], func_blocks)
        else:
            functions[func["name"]] = ({}, func_blocks)

    to_ssa(blocks, functions)

    cfg.reconstruct_prog(blocks, prog)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = test_ssa(prog)
    json.dump(prog, sys.stdout, indent=2)
