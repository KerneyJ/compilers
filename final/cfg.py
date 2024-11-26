import copy

class bb:
    TERM = ['br', 'jmp', 'ret']

    def __init__(self, instrs, name, num, func_name):
        self.instrs = instrs
        self.name = name
        self.parents = []
        self.kids = []
        self.const_table = {}
        self.live_list = []
        self.term = self.instrs[-1]
        self.num = num
        self.func_name = func_name
        self.dominates = []
        self.defs = set()

    def __str__(self):
        s = "Name: " + self.name + " Parents: " + ", ".join([p.name for p in self.parents]) + " Children: " + ", ".join([k.name for k in self.kids]) + "\n"
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
    for instr in function["instrs"]:
        if "op" in instr:
            curr_instrs.append(instr)
            if instr["op"] in bb.TERM:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                if instr["op"] == "jmp" or instr["op"] == "br":
                    blocks[curr_name].kids += [label + "@" + function["name"] for label in instr["labels"]]
                curr_instrs = []
                curr_name = "temp" + str(len(blocks)) + "@" + function["name"]
                num += 1
        else: # we have a label
            if curr_instrs:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                blocks[curr_name].kids = [instr["label"] + "@" + function["name"]]
                num += 1
            curr_instrs = [instr]
            curr_name = instr["label"] + "@" + function["name"]
    if curr_instrs:
        blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
        num += 1


    # make cfg
    for name in blocks:
        parents = blocks[name].kids
        for i in range(len(parents)):
            parent = blocks[name].kids[i]
            blocks[name].kids[i] = blocks[parent]
            blocks[parent].add_prnt(blocks[name])

    return blocks

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

def get_defs(blocks: dict[str, cfg.bb], func_args: dict[str, list[str]]):
    block_list = [blocks[name] for name in blocks]
    block_list.sort()
    seen = {} # maps function names to seen variables
    for name in func_args:
        seen[name] = set()

    for block in block_list:
        defs = set()
        if "entry" in block.name:
            for arg in func_args[block.func_name]:
                defs.add(arg)
        for instr in block.instrs:
            if "dest" in instr and instr["dest"] not in seen[block.func_name]:
                defs.add(instr["dest"])
        block.defs = defs
        seen[block.func_name] |= defs
