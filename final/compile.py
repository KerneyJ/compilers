import json
import sys
import cfg
import liveness
import regalloc
import codegen

GPR = ("r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15")

def compile(prog):
    blocks = {}
    funcs = {}
    func_args = {}
    for func in prog["functions"]:
        func_name = func["name"]
        func_blocks = cfg.make_bb(func)
        cfg.make_ii(func_blocks)
        funcs[func_name] = [func_blocks[block_name] for block_name in func_blocks]
        if "args" in func:
            func_args[func_name] = [arg["name"] for arg in func["args"]]
        else:
            func_args[func_name] = []
        blocks |= func_blocks
    for name in blocks: # place args in the instruction dictionary
        if "entry" not in name:
            continue
        block = blocks[name]
        func_name = block.func_name
        args = func_args[func_name]
        block.instrs[0]["f_args"] = args
    # liveness analysis
    liveness.instr_liveness(blocks)
    ig = regalloc.make_interference_graph(blocks)
    reg_alloc = regalloc.register_allocation(ig, len(GPR))
    for func_name in reg_alloc:
        regalloc.register_assignment(GPR, reg_alloc[func_name])
    for func_name in funcs:
        f_blocks = funcs[func_name]
        f_regs = reg_alloc[func_name]
        codegen.gen_func(f_blocks, f_regs)

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = compile(prog)

