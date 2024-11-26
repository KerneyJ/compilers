import cfg

def make_interference_graph(blocks):
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

def register_allocation(interference_graph, num_regs):
    reg_alloc = {}
    sorted_vars = sorted(interference_graph.keys(), key=lambda x: len(interference_graph[x]), reverse=True)
    unused = set(range(num_regs))
    for var in sorted_vars:
        used = [reg_alloc[adj] for adj in interference_graph[var] if adj in reg_alloc]
        available = unused - used
        if available:
            reg_alloc[var] = list(available)[0]
        else:
            reg_alloc[var] = None
    return reg_alloc
