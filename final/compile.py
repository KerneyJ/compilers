import json
import sys
import cfg
import liveness
import regalloc
import codegen

GPR = ("r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15") # general purpose registers
CACV = ("rdi", "rsi", "rdx", "rcx", "stack") # calling convention

def assemble_text(func: list[str]):
    out = ""
    for instr in func:
        out += instr + "\n"
    return out

def compile(prog):
    blocks = {}
    funcs = {}
    func_args = {}
    compiled_funcs = {}
    out = ".section .text\n.globl _start\n"
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

    # register allocation
    liveness.instr_liveness(blocks)
    ig = regalloc.make_interference_graph(blocks)
    reg_alloc = regalloc.register_allocation(ig, len(GPR)) # side effect is populating the type table block.var_type
    for func_name in reg_alloc:
        regalloc.register_assignment(GPR, reg_alloc[func_name])

    # code generation
    for func_name in funcs:
        f_blocks = funcs[func_name]
        f_regs = reg_alloc[func_name]
        # get typing info
        var_types = {}
        for b in f_blocks:
            var_types |= b.var_types
        func_x86 = codegen.gen_func(f_blocks, f_regs, {"var_types": var_types})
        compiled_funcs[func_name] = func_x86

    for func_name in compiled_funcs:
        out += assemble_text(compiled_funcs[func_name]) + "\n"

    out += "  movq $1, %rax\n  xorq %rbx, %rbx\n  int $0x80"

    return out

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    out = compile(prog)
    print(out)

