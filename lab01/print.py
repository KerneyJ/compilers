import json
import sys

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for f in prog["functions"]:
        for instr in f["instrs"]:
            print(instr)
        print()
    
