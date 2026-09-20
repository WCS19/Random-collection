import sys

def run(code, inp=""):
    code = [c for c in code if c in "><+-.,[]"]
    tape = [0] * 30000
    ptr = pc = 0
    stack, jumps = [], {}
    for i, c in enumerate(code):
        if c == "[": stack.append(i)
        elif c == "]":
            j = stack.pop()
            jumps[j] = i
            jumps[i] = j
    inputs = iter(inp)
    out = []
    while pc < len(code):
        c = code[pc]
        if c == ">": ptr += 1
        elif c == "<": ptr -= 1
        elif c == "+": tape[ptr] = (tape[ptr] + 1) % 256
        elif c == "-": tape[ptr] = (tape[ptr] - 1) % 256
        elif c == ".": out.append(chr(tape[ptr]))
        elif c == ",":
            try: tape[ptr] = ord(next(inputs))
            except StopIteration: tape[ptr] = 0
        elif c == "[" and tape[ptr] == 0: pc = jumps[pc]
        elif c == "]" and tape[ptr] != 0: pc = jumps[pc]
        pc += 1
    return "".join(out)

code = open(sys.argv[1]).read()
inp = sys.argv[2] if len(sys.argv) > 2 else ""
print(run(code, inp), end="")