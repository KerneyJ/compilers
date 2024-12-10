# arithmetic
def add(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"addq {arg2}, %rax",
        f"movq %rax, {dest}"
    ]

def sub(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"subq {arg2}, %rax",
        f"movq %rax, {dest}"
    ]

def mul(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"imul {arg2}, %rax",
        f"movq %rax, {dest}"
    ]

def div(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"cltd",
        f"divq {arg2}",
        f"movq %rax, {dest}"
    ]

# comparrison
def eq(dest, arg1, arg2):
    return [
        f"cmpq {arg1}, {arg2}",
        f"xor %rax %rax",
        f"setne %al",
        f"movq %rax {dest}",
    ]

def lt(dest, arg1, arg2):
    return [
        f"cmpq {arg1}, {arg2}",
        f"xor %rax %rax",
        f"setl %al",
        f"movq %rax {dest}",
    ]

def lte(dest, arg1, arg2):
    return [
        f"cmpq {arg1}, {arg2}",
        f"xor %rax %rax",
        f"setle %al",
        f"movq %rax {dest}",
    ]

def gt(dest, arg1, arg2):
    return [
        f"cmpq {arg1}, {arg2}",
        f"xor %rax %rax",
        f"setg %al",
        f"movq %rax {dest}",
    ]

def gte(dest, arg1, arg2):
    return [
        f"cmpq {arg1}, {arg2}",
        f"xor %rax %rax",
        f"setge %al",
        f"movq %rax {dest}",
    ]

def noti(arg):
    return [
        f"not {arg}"
    ]

def andi(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"andq {arg2}, %rax",
        f"movq %rax, {dest}"
    ]

def ori(dest, arg1, arg2):
    return [
        f"movq {arg1}, %rax",
        f"orq {arg2}, %rax",
        f"movq %rax, {dest}"
    ]

def jmp(label):
    return [
        f"jmp {label}"
    ]

def br(cond, label1, label2):
    return [
        f"testq {cond}",
        f"jne {label1}",
        f"jmp {label2}",
    ]

def call(label):
    return [
        f"call {label}"
    ]

def ret(arg=None):
    if arg:
        return [
            f"movq {arg}, %rax",
            f"ret"
        ]
    else:
        return [
            f"xor %rax, %rax",
            f"ret"
        ]

def nop():
    return [
        f"nop"
    ]

def label(label):
    return [
        f"{label}:"
    ]

def idi(src, dst):
    return [
        f"movq {src}, {dest}"
    ]


