import json
import sys
import cfg
import liveness
import regalloc
import codegen
import stubs
import constants

def stub_scan(func: list[str]):
    stub_funcs = {}
    for idx in range(len(func)):
        instr = func[idx]
        if "__stub__" in instr:
            stub_func = instr[8:]
            if "reorder" in stub_func:
                pos = int(stub_func[7:])
                ret = func.pop(len(func) - pos - 2)
                func.append(ret)
                continue
            res = stubs.map[stub_func]()
            stub_funcs[instr] = res
    func = [instr for instr in func if "__stub__" not in instr]

    return func, stub_funcs

def _instr_lst_to_txt(instr_lst: list[str]):
    out = ""
    for instr in instr_lst:
        out += instr + "\n"
    return out

def assemble_functions(funcs: list[dict[str, str]]):
    # here we need to compose the text and data sections
    # decl and funcs go to the text section
    # data goes to the data section
    text = ".text\n"
    func_strs = ""
    decl_strs = ""
    data = ".data\n"
    out = ""
    stub_funcs = {}
    
    # put together compiled functions
    for func_name in funcs:
        func_map = funcs[func_name]
        if "decl" in func_map:
            decl = func_map["decl"]
            decl_strs += _instr_lst_to_txt(decl)
        if "func" in func_map:
            func = func_map["func"]
            func, sf = stub_scan(func)
            if "__stub__exit" in sf:
                func += sf["__stub__exit"]["stub"]
                del sf["__stub__exit"]
            stub_funcs |= sf
            func_strs += _instr_lst_to_txt(func) + "\n"
        if "data" in func_map:
            d = func_map["data"]
            data += _instr_lst_to_txt(d)

    # put together stub functions
    for func_name in stub_funcs:
        func_map = stub_funcs[func_name]
        if "decl" in func_map:
            decl = func_map["decl"]
            decl_strs += _instr_lst_to_txt(decl)
        if "func" in func_map:
            func = func_map["func"]
            func_strs += _instr_lst_to_txt(func) + "\n"
        if "data" in func_map:
            d = func_map["data"]
            data += _instr_lst_to_txt(d)

    text += decl_strs + "\n"
    text += func_strs + "\n"
    out += data + "\n" + text
    return out

def compile(prog):
    blocks = {}
    funcs = {}
    func_args = {}
    compiled_funcs = {}
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
    reg_alloc = regalloc.register_allocation(ig, len(constants.GPR)) # side effect is populating the type table block.var_type
    for func_name in reg_alloc:
        regalloc.register_assignment(constants.GPR, reg_alloc[func_name])

    # code generation
    for func_name in funcs:
        f_blocks = funcs[func_name]
        f_regs = reg_alloc[func_name]
        # get typing info
        var_types = {}
        for b in f_blocks:
            var_types |= b.var_types
        func_x86 = codegen.gen_func(f_blocks, f_regs, {"var_types": var_types, "clobber": set([f_regs[var] for var in f_regs])})
        compiled_funcs[func_name] = func_x86

    # put them all together
    out = assemble_functions(compiled_funcs)

    return out

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    out = compile(prog)
    print(out)
