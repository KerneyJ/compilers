def print():
    func = [
        f"print: ", # (address, size)
        f"  movq $4, %rax", # System call number for write (4 in 32-bit)
        f"  movq $1, %rbx", # File descriptor (1 = stdout)
        f"  movq %rdi, %rcx", # Address of the character to write
        f"  movq %rsi, %rdx", # Number of bytes to write (1 character)
        f"  int $0x80", # Invoke the system call
        f"  ret",
    ]

    decl = [
        ".globl print",
        ".type print @function",
    ]

    return {"func": func, "decl": decl}

def scan():
    pass
