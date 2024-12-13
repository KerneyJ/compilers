def print():
    func = [
        "print: ", # (address, size)
        "  push %rax",
        "  push %rbx",
        "  push %rcx",
        "  push %rdx",
        # Convert number to string (manual digit extraction)
        "  movq $0, %rcx", # Counter for digit position
        "  xor %rax, %rax",
        "  movq %rdi, %rax",

        "convert_loop:",
        # Divide by 10 to get rightmost digit
        # Quotient in eax, remainder in edx
        "  xor %rdx, %rdx",
        "  movq $10, %rbx",       # Divisor
        "  divq %rbx",            # Divide rax

        # Convert digit to ASCII (add 48)
        "  addq $48, %rdx",       # Convert remainder to ASCII

        # Push digit onto stack (in reverse order)
        "  pushq %rdx",
        "  incq %rcx",            # Increment digit counter

        # Check if number is zero
        "  cmpq $0, %rax",
        "  jne convert_loop",     # Continue if not zero

        "print_digits:"
        # Print digits from stack
        "  popq %rax",            # Get digit from stack
        "  movb %al, char_buf",     # Store digit in memory

        # System call to write single digit
        "  movq $4, %rax",          # System call number for write
        "  movq $1, %rbx",          # File descriptor (stdout)
        "  movq %rcx, %rdi",        # Save the counter
        "  movq $char_buf, %rcx",   # Buffer address
        "  movq $1, %rdx",          # Length of buffer
        "  int $0x80",              # Invoke system call
        "  movq %rdi, %rcx",        # Restore the counter

        # Decrement counter and loop if more digits
        "  loop print_digits",

        # Print newline
        "  xor %rax, %rax",
        "  movq $10, %rax",
        "  movb %al, char_buf",
        "  movq $4, %rax",         # System call number for write
        "  movq $1, %rbx",         # File descriptor (stdout)
        "  movq $char_buf, %rcx",  # Newline character
        "  movq $1, %rdx",         # Length
        "  int $0x80",             # Invoke system call

        # pop stuff off of the stack
        "  pop %rdx",
        "  pop %rcx",
        "  pop %rbx",
        "  pop %rax",
        "  ret",
    ]

    decl = [
        ".globl print",
        ".type print, @function",
    ]

    data = [
        "char_buf: .byte 0"
    ]

    return {"func": func, "decl": decl, "data": data}

def scan():
    pass

map = {
    "print": print,
}
