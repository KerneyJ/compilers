import json
import sys

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
        print(self.parents)
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
        if block.fuc_name in ofmap.keys():
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

def perform_op(instr):
    if instr["op"] == "add":
        return instr["args"][0] + instr["args"][1]
    elif instr["op"] == "mul":
        return instr["args"][0] * instr["args"][1]
    elif instr["op"] == "sub":
        return instr["args"][0] - instr["args"][1]
    elif instr["op"] == "div":
        return instr["args"][0] / instr["args"][1]
    else:
        raise Exception(f"Does not support instruction: {instr}")

def constprop(block, ct = {}):
    change = True
    while(change):
        change = False
        for idx in range(len(block.instrs)):
            instr = block.instrs[idx]
            if "op" not in instr:
                continue
            if instr["op"] == "const" and instr["dest"] not in ct:
                ct[instr["dest"]] = instr["value"]
                change = True
            if "args" not in instr:
                continue
            const = True
            for arg in instr["args"]:
                if arg in ct:
                    instr["args"][instr["args"].index(arg)] = ct[arg]
                if type(arg) != int:
                    const = False
            if const:
                value = perform_op(instr)
                block.instrs[idx] = {'dest': instr["dest"], 'op': 'const', 'type': 'int', 'value': value}
                ct[instr["dest"]] = value
                change = True
    return block, ct

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= make_bb(func)

    stack = [blocks[name] for name in blocks]
    while stack:
        block = stack.pop(0)
        inp = block.gather_parent_state()
        block, out = constprop(block, inp)
        if out != inp:
            for kid in block.kids:
                if kid not in stack:
                    stack.append(kid)
        block.const_table = out

    for name in blocks:
        block = blocks[name]
        print(block)

    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    # json.dump(prog, sys.stdout, indent=2)
