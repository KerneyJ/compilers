class bb:
    TERM = ['br', 'jmp', 'ret']

    def __init__(self, instrs, name, num, func_name):
        self.instrs = instrs
        self.name = name
        self.parents = []
        self.kids = []
        self.const_table = {}
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

    def gather_parent_state(self):
        pst = {}
        for p in self.parents:
            if not pst:
                pst = p.const_table
                continue
            pst = dict(pst.items() & p.const_table.items())
        return pst

def make_bb(function):
    num = 0
    blocks = {}
    curr_instrs = []
    curr_name = function["name"]
    for instr in function["instrs"]:
        if "op" in instr:
            curr_instrs.append(instr)
            if instr["op"] in bb.TERM:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                if instr["op"] == "jmp" or instr["op"] == "br":
                    blocks[curr_name].kids += instr["labels"]
                curr_instrs = []
                curr_name = "temp" + str(len(blocks))
                num += 1
        else:
            if curr_instrs:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
                num += 1
            curr_instrs = [instr]
            curr_name = instr["label"]
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

def reconstruct_prog(blocks):
    ofmap = {} # ordered functions map
    functions = []
    for name in blocks:
        block = blocks[name]
        if block.func_name in ofmap.keys():
            ofmap[block.func_name].append(block)
        else:
            ofmap[block.func_name] = [block]

    for name in ofmap:
        block_list = ofmap[name]
        block_list.sort()
        f = []
        for b in block_list:
            f += b.instrs
        functions.append({"instrs": f, "name": name})

    return functions
