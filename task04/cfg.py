import copy

class bb:
    TERM = ["br", "jmp", "ret", "call"]
    COUNTER = 0

    def __init__(self, instrs, name, num, func_name):
        self.instrs = instrs
        self.func_name = func_name
        self.name = name
        self.num = num
        self.term = self.instrs[-1]

        self.parents = []
        self.kids = []
        self.call_parents = []
        self.call_kids = []
        self.ret_parents = []
        self.ret_kids = []

        self.reachable = []

        self.const_table = {}

        self.live_list = []

        self.dominates = []

        self.var_to_mem = {} # maping of variables to allocations
        self.live_alloc = [] # list of allocaitons made live by a load

    def __str__(self):
        s = "Name: " + self.name + " Parents: {" + ", ".join([p.name for p in self.parents]) + "} Children: {" + ", ".join([k.name for k in self.kids]) +\
            "} Call Parents: {" + ", ".join([p.name for p in self.call_parents]) + "} Call Children: {" + ", ".join([k.name for k in self.call_kids]) +\
             "} Return Parents: {" + ", ".join([p.name for p in self.call_parents]) + "} Return Children: {" + ", ".join([k.name for k in self.call_kids]) + "}\n"
        for instr in self.instrs:
            s += "\t" + str(instr) + "\n"
        return s

    def __lt__(self, other):
        return self.num < other.num

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def add_prnt(self, parent):
        self.parents.append(parent)

    def add_kid(self, kid):
        self.kids.append(kid)

    def gather_parent_ct(self):
        pct = {}
        for p in self.parents:
            if not pct:
                pct = p.const_table
                continue
            pct = dict(pct.items() & p.const_table.items())
        return pct

    def gather_child_ll(self):
        cll = []
        for k in self.kids:
            cll += k.live_list
        cll = list(set(cll)) # remove dups
        return cll

    def gather_desc_ll(self):
        # first get all descendants
        desc = self.kids
        visited = []
        while desc:
            node = desc.pop(0)
            if node in visited:
                continue
            visited.append(node)
            desc += [k for k in node.kids if k != self and k not in visited]

        dll = []
        for d in visited:
            dll += d.live_list
        dll = list(set(dll)) # remove dups
        return dll

    def gather_phi(self):
        # returns a list of indexes of the phi instructions
        phi_location = []
        for idx in range(len(self.instrs)):
            instr = self.instrs[idx]
            if "op" not in instr:
                continue
            if instr["op"] == "phi":
                phi_location.append(idx)

        return  phi_location

def make_bb(function):
    num = 0
    blocks = {}
    curr_instrs = []
    curr_name = "entry@" + function["name"]
    caller_name = None # switch that needs to be checked to see if the previous block ends with a call instruction, thus the this new block will be the block returned to
    for instr in function["instrs"]:
        if "op" in instr:
            curr_instrs.append(instr)
            if instr["op"] not in bb.TERM:
                continue
            if caller_name:
                blocks[caller_name].kids = [curr_name]
                caller_name = None # consume caller name
            if "call" in instr["op"]:
                funcs = "_".join([func for func in instr["funcs"]])
                caller_name = curr_name
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                curr_instrs = []
                curr_name = "ret-" + funcs + "@" + caller_name
                num += 1
                continue
            blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
            if instr["op"] == "jmp" or instr["op"] == "br":
                blocks[curr_name].kids += [label + "@" + function["name"] for label in instr["labels"]]
            curr_instrs = []
            curr_name = "temp" + str(len(blocks)) + "@" + function["name"]
            num += 1
        else: # we have a label
            if curr_instrs:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                if caller_name:
                    blocks[caller_name].kids = [curr_name]
                    caller_name = None # consume caller name
                blocks[curr_name].kids = [instr["label"] + "@" + function["name"]]
                num += 1

            curr_instrs = [instr]
            curr_name = instr["label"] + "@" + function["name"]
            if caller_name:
                blocks[caller_name].kids = [curr_name]
                caller_name = None # consume caller name
    if curr_instrs:
        blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
        num += 1
    if caller_name:
        if curr_name in blocks:
            blocks[caller_name].kids = [curr_name]
            caller_name = None
        else:
            curr_instrs = [{"op": "ret"}]
            blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
            blocks[caller_name].kids = [curr_name]


    # make cfg
    for name in blocks:
        block = blocks[name]
        for idx in range(len(block.kids)):
            kid_name = block.kids[idx]
            kid_block = blocks[kid_name]
            block.kids[idx] = kid_block
            kid_block.parents.append(block)

    return blocks

def make_crg(blocks: dict[str, bb]): # crg => call ret graph
    # first handle all of the calls
    for name in blocks:
        block = blocks[name]
        term = block.term
        if "op" not in term:
            continue
        if "call" not in term["op"]:
            continue
        funcs = term["funcs"]
        for func in funcs:
            block.call_kids.append(blocks["entry@" + func])
            blocks["entry@" + func].call_parents.append(block)

    # next handle all explicit returns
    for name in blocks:
        block = blocks[name]
        term = block.term
        if "op" not in term:
            continue
        if "ret" not in term["op"]:
            continue
        func_name = block.func_name
        func_entry = blocks["entry@" + func_name]
        callers = func_entry.call_parents
        for caller in callers:
            assert len(caller.kids) == 1 # the callers only child should be the return block
            kid = caller.kids[0]
            block.ret_kids.append(kid)
            kid.ret_parents.append(block)

    # finally, implicit returns
    flb = {} # maps function names to last block of function
    for name in blocks:
        block = blocks[name]
        if block.func_name not in flb:
            flb[block.func_name] = block
        else:
            curr = flb[block.func_name]
            if curr.num < block.num:
                flb[block.func_name] = block

    for name in flb:
        block = flb[name]
        term = block.term
        if "ret" in term["op"]:
            continue
        entry = blocks["entry@" + name]
        callers = entry.call_parents
        for caller in callers:
            assert len(caller.kids) == 1
            kid = caller.kids[0]
            block.ret_kids.append(kid)
            kid.ret_parents.append(block)

def insert_block(block: bb, child: bb, blocks):
    block.parents = copy.deepcopy(child.parents)
    child.parents = [block]
    block.kids = [child]
    for parent in block.parents:
        for idx in range(len(parent.kids)):
            if parent.kids[idx] == child:
                parent.kids[idx] = block
    for name in blocks:
        if blocks[name].num > child.num:
            blocks[name].num += 1
    block.num = child.num
    child.num += 1

def reconstruct_prog(blocks, prog):
    ofmap = {} # ordered functions map
    functions = []
    for name in blocks:
        block = blocks[name]
        if block.func_name in ofmap.keys():
            ofmap[block.func_name].append(block)
        else:
            ofmap[block.func_name] = [block]


    for idx in range(len(prog["functions"])):
        name = prog["functions"][idx]["name"]
        if name not in ofmap:
            raise Exception("looking for function not in ofmap")

        block_list = ofmap[name]
        block_list.sort()
        f = []
        for b in block_list:
            f += b.instrs
        prog["functions"][idx]["instrs"] = f

def dominate(block: bb):
    paths = []
    def dfs(b, p, paths):
        path = p + [b]
        if not b.parents:
            paths.append(path)
            return
        for parent in b.parents:
            if parent in path:
                path = path + [parent]
                for grandparent in parent.parents:
                    if grandparent in path:
                        continue
                    dfs(grandparent, path, paths)
                continue
            dfs(parent, path, paths)

    dfs(block, [], paths)

    spaths = [set(p) for p in paths]
    dom = spaths[0]
    for spath in spaths:
        dom &= spath

    for dominator in dom:
        dominator.dominates.append(block)

def df_b(b: bb, blocks: dict[str, bb]):
    df = []
    for name in blocks:
        block = blocks[name]
        if (block not in b.dominates) and len(set(block.parents) & set(b.dominates)) > 0:
            df.append(block)
    return df

def reachable(parent: bb, child: bb):
    stack = [parent]
    visited = []
    visited_funcs = set()
    while stack:
        block = stack.pop(0)
        visited_funcs.add(block.func_name)
        if child in (block.kids + block.ret_kids or block.call_kids):
            continue
        for kid in block.kids + block.call_kids:
            if kid in visited:
                continue
            visited.append(kid)
            stack.append(kid)
        for kid in block.ret_kids:
            if kid in visited:
                continue
            if kid.func_name not in visited_funcs:
                continue
            visited.append(kid)
            stack.append(kid)
    return visited

if __name__ == "__main__":
    import json
    import sys
    prog = json.load(sys.stdin)

    blocks = {}
    args = {}
    for func in prog["functions"]:
        blocks |= make_bb(func)
        if "args" in func:
            args[func["name"]] = func["args"]
        else:
            args[func["name"]] = []

    make_crg(blocks)
    reconstruct_prog(blocks, prog)

    json.dump(prog, sys.stdout, indent=2)
