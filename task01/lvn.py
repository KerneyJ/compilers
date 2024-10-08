import json
import sys

class bb: 
    TERM = ['br', 'jmp', 'ret']
    def __init__(self, instrs, name, num, func_name):
        self.instrs = instrs
        self.name = name
        self.parents = []
        self.term = self.instrs[-1]
        self.num = num
        self.func_name = func_name

    def __str__(self):
        return str(self.instrs)

    def __lt__(self, other):
        self.num < other.num

    def add_prnt(self, parent):
        self.parents.append(parent)

def make_bb(function):
    num = 0
    blocks = {}
    curr_instrs = []
    curr_name = function["name"]
    for instr in function["instrs"]:
        if "op" in instr:
            curr_instrs.append(instr)
            if instr in bb.TERM:
                blocks[curr_name] = bb(curr_instrs, curr_name, num, function["name"])
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

    return blocks

def make_cfg(blocks):
    for name in blocks:
        block = blocks[name]
        if not (block.term["op"] in bb.TERM):
            continue

        labels = block.term["labels"]
        for label in labels:
            if label not in blocks:
                raise Exception("Somehow have a label that is not associated with a block")
            child = blocks[label]
            child.add_prnt(blocks[label])

def lvn(block):
    number = 0
    val2num = {}
    num2val = {}
    var2num = {}
    num2var = {}

    for instr in block.instrs:
        if not "op" in instr.keys():
            continue
        if instr["op"] == "const":
            continue
        if not "dest" in instr.keys():
            continue

        dest = instr["dest"]
        args = []
        if "args" in instr.keys():
            for arg in instr["args"]:
                args.append(arg)
        val = "".join([instr["op"]] + args)
        num = val2num.get(val)

        if num is None:
            num = number
            val2num[val] = num
            num2val[num] = val
            var2num[dest] = num
            num2var[num] = dest
            number += 1
        else:
            instr["op"] = "id"
            instr["args"] = [num2var[num]]

    return block, [val2num, num2val, var2num, num2var]

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

def opt(prog):
    blocks = {}
    for func in prog["functions"]:
        blocks |= make_bb(func)
    make_cfg(blocks)

    for name in blocks:
        block = blocks[name]
        opt_block, state = lvn(block)

    prog["functions"] = reconstruct_prog(blocks)
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    prog = opt(prog)
    json.dump(prog, sys.stdout, indent=2)


