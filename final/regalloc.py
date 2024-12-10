import cfg

def make_interference_graph(blocks: dict[str, cfg.bb]):
    # assumes liveness has been done at the instruciton level
    cfg.get_defs(blocks)
    interference_graph = {} # interference graph
    vars_by_func = {}
    for name in blocks:
        block = blocks[name]
        if block.func_name in vars_by_func:
            vars_by_func[block.func_name] |= block.defs
        else:
            vars_by_func[block.func_name] = block.defs

    for func_name in vars_by_func:
        vars = vars_by_func[func_name]
        interference_graph[func_name] = {}
        for var in vars:
            interference_graph[func_name][var] = set()

    for name in blocks:
        block = blocks[name]
        func_name = block.func_name
        for instr in block.instrs:
            if "live_vars" not in instr or "dest" not in instr:
                continue
            live_vars = instr["live_vars"]
            dest = instr["dest"]
            for var in live_vars:
                if dest != var:
                    interference_graph[func_name][dest].add(var)
                    interference_graph[func_name][var].add(dest)

    return interference_graph

def register_allocation(interference_graph: dict[str, dict[str, set[str]]], num_regs: int):
    reg_alloc = {}
    for func_name in interference_graph:
        func_ig = interference_graph[func_name]
        reg_alloc[func_name] = {}
        sorted_vars = sorted(func_ig.keys(), key=lambda x: len(func_ig[x]), reverse=True)
        unused = set(range(num_regs))
        for var in sorted_vars:
            used = set([reg_alloc[func_name][adj] for adj in func_ig[var] if adj in reg_alloc[func_name]])
            available = unused - used
            if available:
                reg_alloc[func_name][var] = list(available)[0]
            else:
                reg_alloc[func_name][var] = None
    return reg_alloc

def register_assignment(registers: tuple[str], reg_alloc: dict[str, set[str]]):
    stack_pos = 0
    for var in reg_alloc:
        if reg_alloc[var] != None:
            reg_alloc[var] = registers[reg_alloc[var]]
        else:
            reg_alloc[var] = "st" + str(stack_pos)
            stack_pos += 1
