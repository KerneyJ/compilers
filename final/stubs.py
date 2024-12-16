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

        "convert_loop_print:",
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
        "  jne convert_loop_print",     # Continue if not zero

        "print_digits:",
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
    func = [
        "scan: ",
        "  push %rbx",
        "  push %rcx",
        "  push %rdx",
        "  push %rdi",
        "  push %rsi",

        # Read in put from stdin
        "  movq $3, %rax",
        "  movq $0, %rbx",
        "  movq $buffer, %rcx",
        "  movq $buffer_len, %rdx",
        "  int $0x80",

        # move args for conversion
        "  movq $buffer, %rsi",
        "  xorq %rax, %rax",
        "  xorq %rcx, %rcx",

        "convert_loop_scan:",
        # Check for new line if found leave and clear buffer
        "  movzbq (%rsi), %rbx",
        "  cmpb $10, %bl",
        "  je zb_loop_header",

        # Convert character to digit
        "  subb $48, %bl",
        "  cmpb $9, %bl",
        "  ja invalid_input",

        # Multiple previous result by 10 add new digit
        "  imulq $10, %rax",
        "  addq %rbx, %rax",
        
        "  incq %rsi", # move to next character
        "  incq %rcx", # increment digit counter
        "  jmp convert_loop_scan",

        "invalid_input:", # exit of the character does not map to a valid digit
        "  movq $1, %rax",
        "  movq $1, %rbx",
        "  int $0x80",

        "zb_loop_header:", # zero out the buffer so it can be used again
        "  movq $buffer, %rdi",
        "  movq $buffer_len, %rcx",

        "zero_buffer:",
        "  movb $0, (%rdi)",
        "  incq %rdi",
        "  loop zero_buffer",

        # pop everything and return, number in rax
        "done:",
        "  pop %rsi",
        "  pop %rdi",
        "  pop %rdx",
        "  pop %rcx",
        "  pop %rbx",
        "  ret",
    ]

    decl = [
        ".globl scan",
        ".type scan, @function",
    ]

    data = [
        "buffer: .space 20",
        "buffer_len = . - buffer",
    ]

    return {"func": func, "decl": decl, "data": data}

def alloc():
    func = [
        "alloc: ",
        "  push %rbx",
        "  push %rcx",
        "  push %rdx",

        # multiply th input by 8 bytes(size of int)
        "  movq $8, %rax",
        "  imulq %rdi, %rax",
        "  movq %rax, %rcx",

        # Get inital program break
        "  movq $45, %rax",
        "  xorq %rbx, %rbx",
        "  int $0x80",

        # Store initial program break
        "  movq %rax, %rdx",

        # Increment %rbx by the buffer size
        "  movq %rdx, %rbx",
        "  addq %rcx, %rbx",

        # Call brk to extend program break
        "  movq $45, %rax",
        "  int $0x80",

        # Verify that brk was successful
        "  cmpq $0, %rax",
        "  jl allocation_error",

        # Store program break pop and return
        "  movq %rdx, %rax",
        "  pop %rdx",
        "  pop %rcx",
        "  pop %rbx",
        "  ret"

        # If brk fails exit with error
        "allocation_error: ",
        "  movq $1, %rax",
        "  movq $1, %rbx",
        "  int $0x80",
    ]

    decl = [
        ".globl alloc",
        ".type alloc, @function",
    ]

    return {"func": func, "decl": decl}

def exiti():
    stub = [
        "  movq $1, %rax",
        "  xorq %rbx, %rbx",
        "  int $0x80",
    ]
    return {"stub": stub}

map = {
    "print": print,
    "scan": scan,
    "alloc": alloc,
    "exit": exiti,
}
