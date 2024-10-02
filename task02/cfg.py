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

    def __str__(self):
        s = "Name: " + self.name + " Parents: " + ", ".join([p.name for p in self.parents]) + " Children: " + ", ".join([k.name for k in self.kids]) + "\n"
        for instr in self.instrs:
            s += "\t" + str(instr) + "\n"
        return s

    def __lt__(self, other):
        self.num < other.num

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

def make_bb(function):
    num = 0
    blocks = {}
    curr_instrs = []
    curr_name = "head@" + function["name"]
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
        else:
            if curr_instrs:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                num += 1
            curr_instrs = [instr]
            curr_name = instr["label"] + "@" + function["name"]
    if curr_instrs:
        blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
        num += 1


    # make cfg
    for name in blocks:
        parents = blocks[name].kids
        for i in range(len(blocks[name].kids)):
            parent = blocks[name].kids[i]
            blocks[name].kids[i] = blocks[parent]
            blocks[parent].add_prnt(blocks[name])

    return blocks

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
