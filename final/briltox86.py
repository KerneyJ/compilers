import constants

# TODO need to check if the args/dest are stack positions or registers
# arithmetic
def add(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  addq %{arg2}, %rax",
        f"  movq %rax, %{dest}"
    ]

def sub(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  subq %{arg2}, %rax",
        f"  movq %rax, %{dest}"
    ]

def mul(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  imul %{arg2}, %rax",
        f"  movq %rax, %{dest}"
    ]

def div(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  cltd",
        f"  divq %{arg2}",
        f"  movq %rax, %{dest}"
    ]

# comparrison
def eq(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  cmpq %{arg1}, %{arg2}",
        f"  xor %rax %rax",
        f"  setne %al",
        f"  movq %rax %{dest}",
    ]

def lt(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  cmpq %{arg1}, %{arg2}",
        f"  xor %rax %rax",
        f"  setl %al",
        f"  movq %rax %{dest}",
    ]

def lte(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  cmpq %{arg1}, %{arg2}",
        f"  xor %rax %rax",
        f"  setle %al",
        f"  movq %rax %{dest}",
    ]

def gt(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  cmpq %{arg1}, %{arg2}",
        f"  xor %rax %rax",
        f"  setg %al",
        f"  movq %rax %{dest}",
    ]

def gte(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  cmpq %{arg1}, %{arg2}",
        f"  xor %rax %rax",
        f"  setge %al",
        f"  movq %rax %{dest}",
    ]

def noti(instr, reg_alloc):
    dest = reg_alloc[instr["dest"]]
    return [
        f"  not %{dest}"
    ]

def andi(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  andq %{arg2}, %rax",
        f"  movq %rax, %{dest}"
    ]

def ori(instr, reg_alloc):
    assert len(instr["args"]) == 2
    arg1 = reg_alloc[instr["args"][0]]
    arg2 = reg_alloc[instr["args"][1]]
    dest = reg_alloc[instr["dest"]]
    return [
        f"  movq %{arg1}, %rax",
        f"  orq %{arg2}, %rax",
        f"  movq %rax, %{dest}"
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
    label2 = instr["labels"][0]
    cond = reg_alloc[instr["args"][0]]
    return [
        f"  testq %{cond}",
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
            arg = reg_alloc[instr["args"][idx]]
            ret.append(f"  movq %{arg}, %{constants.CACV[idx]}")
    ret.append(f"  call {funcs[0]}")
    if "dest" in instr:
        dest = reg_alloc[instr["dest"]]
        ret.append(f"  movq %rax, %{dest}")
    return ret

def ret(instr, reg_alloc):
    if "args" in instr and len(instr["args"]) > 0:
        assert len(instr["args"]) == 1
        arg = reg_alloc[instr["args"][0]]
        return [
            f"  movq %{arg}, %rax",
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
    src = reg_alloc[instr["args"][0]]
    dest = reg_alloc[instr["dest"]]
    if src == dest:
        return []
    else:
        return [
            f"  movq %{src}, %{dest}"
        ]

def const(instr, reg_alloc):
    dest = reg_alloc[instr["dest"]]
    value = instr["value"]
    return [
        f"  movq ${value}, %{dest}"
    ]

def printi(instr, reg_alloc):
    assert "var_types" in instr
    assert len(instr["args"]) == 1
    for vt in instr["var_types"]:
        if vt != "bool" and vt != "int":
            raise Exception(f"Instruction attempting to print non integer or boolean value: {vt}")
    arg = reg_alloc[instr["args"][0]]
    assert "st" not in arg # TODO handle when variables are on the stack
    return [
        f"__stub__print",
        f"  push %rdi",
        f"  movq %{arg}, %rdi",
        f"  call print",
        f"  pop %rdi",
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

    "free": todo,
    "store": todo,
    "load": todo,
    "ptradd": todo,
}
def todo(instr, reg_alloc):
    return [f"TODO {instr["op"]}"]
