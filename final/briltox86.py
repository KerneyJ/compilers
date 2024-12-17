import constants

def convert_stack_if_needed(arg):
    if "st" not in arg:
        return arg
    return f"{int(arg[2]) * 8}(%rsp)"


# TODO need to check if the args/dest are stack positions or registers
# arithmetic
def add(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  addq {arg2}, %rax",
        f"  movq %rax, {dest}"
    ]

def sub(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  subq {arg2}, %rax",
        f"  movq %rax, {dest}"
    ]

def mul(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  imul {arg2}, %rax",
        f"  movq %rax, {dest}"
    ]

def div(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  cltd",
        f"  divq {arg2}",
        f"  movq %rax, {dest}"
    ]

# comparrison
def eq(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  cmpq {arg1}, {arg2}",
        f"  sete %al",
        f"  movq %rax, {dest}",
    ]

def lt(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  cmpq {arg2}, {arg1}",
        f"  setl %al",
        f"  movq %rax, {dest}",
    ]

def lte(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  cmpq {arg2}, {arg1}",
        f"  setle %al",
        f"  movq %rax, {dest}",
    ]

def gt(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  cmpq {arg2}, {arg1}",
        f"  setg %al",
        f"  movq %rax, {dest}",
    ]

def gte(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  cmpq {arg2}, {arg1}",
        f"  setge %al",
        f"  movq %rax, {dest}",
    ]

def noti(instr, reg_alloc):
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  xor %rax, %rax",
        f"  test {dest}, {dest}",
        f"  sete %al",
        f"  movq %rax, {dest}",
    ]

def andi(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  andq {arg2}, %rax",
        f"  movq %rax, {dest}"
    ]

def ori(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    arg2 = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  movq {arg1}, %rax",
        f"  orq {arg2}, %rax",
        f"  movq %rax, {dest}"
    ]

def jmp(instr, reg_alloc):
    assert len(instr["labels"]) == 1
    label = instr["labels"][0]
    return [
        f"  jmp {label}"
    ]

def br(instr, reg_alloc):
    assert len(instr["labels"]) == 2
    assert len(instr["args"]) == 1
    label1 = instr["labels"][0]
    label2 = instr["labels"][1]
    cond = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    return [
        f"  testq {cond}, {cond}",
        f"  jne {label1}",
        f"  jmp {label2}",
    ]

def call(instr, reg_alloc):
    # FIXME, need to a do a couple of things here
    # first need to give the first block in every function a label
    # next need to somehow pass this label to here
    # last need to insert pseudo instruction for pushing parameters on the stack, to handle later
    assert len(instr["funcs"]) == 1
    funcs = instr["funcs"]
    ret = []
    if "args" in instr:
        if len(instr["args"]) > 4:
            raise Exception("Need to push args to stack, todo implement that")
        for idx in range(len(instr["args"])):
            arg = convert_stack_if_needed(reg_alloc[instr["args"][idx]])
            ret.append(f"  movq {arg}, {constants.CACV[idx]}")
    ret.append(f"  call {funcs[0]}")
    if "dest" in instr:
        dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
        ret.append(f"  movq %rax, {dest}")
    return ret

def ret(instr, reg_alloc):
    if "args" in instr and len(instr["args"]) > 0:
        assert len(instr["args"]) == 1
        arg = convert_stack_if_needed(reg_alloc[instr["args"][0]])
        return [
            f"  movq {arg}, %rax",
            f"  ret"
        ]
    else:
        return [
            f"  xor %rax, %rax",
            f"  ret"
        ]

def nop(instr, reg_alloc):
    return [
        f"  nop"
    ]

def label(instr, reg_alloc):
    label = instr["label"]
    return [
        f"{label}:"
    ]

def idi(instr, reg_alloc):
    assert len(instr["args"]) == 1
    src = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    if src == dest:
        return []
    else:
        return [
            f"  movq {src}, {dest}"
        ]

def printi(instr, reg_alloc):
    assert "var_types" in instr
    assert len(instr["args"]) == 1
    for vt in instr["var_types"]:
        if vt != "bool" and vt != "int":
            raise Exception(f"Instruction attempting to print non integer or boolean value: {vt}")
    arg = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    assert "st" not in arg # TODO handle when variables are on the stack
    return [
        f"__stub__print",
        f"  push %rdi",
        f"  movq {arg}, %rdi",
        f"  call print",
        f"  pop %rdi",
    ]

def const(instr, reg_alloc):
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    value = instr["value"]
    return [
        f"  movq ${value}, {dest}"
    ]

def alloc(instr, reg_alloc):
    assert len(instr["args"]) == 1
    size = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"__stub__alloc",
        f"  movq {size}, %rdi",
        f"  call alloc",
        f"  movq %rax, {dest}",
    ]

def store(instr, reg_alloc):
    assert len(instr["args"]) == 2
    loc = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    val = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    return [
        f"  movq {val}, ({loc})",
    ]

def load(instr, reg_alloc):
    assert len(instr["args"]) == 1
    ptr = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    if "(" not in ptr:
        return [
            f"  movq ({ptr}), {dest}",
        ]
    else:
        return [
            f"  movq {ptr}, %rax",
            f"  movq %rax, {dest}",
        ]

def ptradd(instr, reg_alloc):
    assert len(instr["args"]) == 2
    ptr = convert_stack_if_needed(reg_alloc[instr["args"][0]])
    inc = convert_stack_if_needed(reg_alloc[instr["args"][1]])
    dest = convert_stack_if_needed(reg_alloc[instr["dest"]])
    return [
        f"  imul $8, {inc}, {inc}",
        f"  movq {inc}, {dest}",
        f"  addq {ptr}, {dest}",
    ]

def handle_args(instr, reg_alloc):
    ret = []
    for idx in range(len(instr["args"])):
        arg = instr["args"][idx]
        reg = constants.CACV[idx]
        dest = convert_stack_if_needed(reg_alloc[arg])
        ret.append(f"  movq {reg}, {dest}")

    return ret

def handle_clobber_push(instr, reg_alloc):
    clobber = list(instr["clobber"])
    return [f"  pushq {reg}" for reg in clobber]

def handle_clobber_pop(instr, reg_alloc):
    clobber = list(instr["clobber"])
    clobber.reverse()
    return [f"  popq {reg}" for reg in clobber] + [f"__stub__reorder{len(clobber)}"]

def handle_scan_arg(instr, reg_alloc):
    arg = convert_stack_if_needed(reg_alloc[instr["arg"]])
    return [
        f"__stub__scan",
        f"  call scan",
        f"  movq %rax, {arg}"
    ]

def handle_stack_vars_alloc(instr, reg_alloc):
    num_vars = instr["num_vars"]
    return [ # TODO simplify this math I know theres a way to subtract immediates in one instruction
        f"  push %rsp",
        f"  subq ${8 * num_vars}, %rsp", # 8 bytes per slot
    ]

def handle_stack_vars_free(instr, reg_alloc):
    num_vars = instr["num_vars"]
    return [
        f"  addq ${8 * num_vars}, %rsp",
        f"  pop %rsp",
    ]

def todo(instr, reg_alloc):
    return [f"TODO {instr["op"]}"]

map = {
    "add": add,
    "mul": mul,
    "sub": sub,
    "div": div,

    "eq": eq,
    "lt": lt,
    "gt": gt,
    "le": lte,
    "ge": gte,

    "not": noti,
    "and": andi,
    "or": ori,

    "jmp": jmp,
    "br": br,
    "call": call,
    "ret": ret,

    "nop": nop,
    "print": printi,
    "id": idi,
    "const": const,

    "alloc": alloc,
    "free": nop, # TODO not enough time to implement this
    "store": store,
    "load": load,
    "ptradd": ptradd,

    # pseudo instructions
    "handle_args": handle_args,
    "handle_clobber_push": handle_clobber_push,
    "handle_clobber_pop": handle_clobber_pop,
    "handle_scan_arg": handle_scan_arg,
    "handle_stack_vars_alloc": handle_stack_vars_alloc,
    "handle_stack_vars_free": handle_stack_vars_free,
}
