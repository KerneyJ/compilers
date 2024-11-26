import json
import sys
import cfg
import liveness
import codegen

def compile(prog):
    blocks = {}
    func_args = {}
    for func in prog["functions"]:
        blocks |= cfg.make_bb(func)
        func_args[func["name"]] = [arg["name"] for arg in func["args"]]

    # liveness analysis
    liveness.instr_liveness(blocks)
    codegen.make_interference_graph(blocks)

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = compile(prog)

