"""Print chosen functions from decompile dumps (text files made by the Lane*Dump Ghidra script).

  python -I tools/lane-v1/showfn.py <hexaddr[,hexaddr...]> <dump.txt> [<dump.txt> ...] [--refs]
Prints the first copy of each function found. --refs keeps the 'REFERENCES TO IT' list (dropped by default).
"""
import re
import sys

want = [int(x, 16) for x in sys.argv[1].split(",")]
files = [a for a in sys.argv[2:] if not a.startswith("--")]
refs = "--refs" in sys.argv
found = {}
for path in files:
    text = open(path, encoding="utf-8", errors="replace").read()
    parts = re.split(r"^=+\n", text, flags=re.M)
    for part in parts:
        m = re.match(r"FUNCTION (\S+) @ ([0-9a-fA-F]+)\s+body ([0-9a-fA-F]+)-([0-9a-fA-F]+)", part)
        if not m:
            continue
        lo, hi = int(m.group(3), 16), int(m.group(4), 16)
        for w in want:
            if lo <= w <= hi and w not in found:
                found[w] = part
for w in want:
    if w not in found:
        print("---- %08X: not in these dumps" % w)
        continue
    part = found[w]
    if not refs:
        lines = part.split("\n")
        out, skipping = [], False
        for line in lines:
            if line.startswith("REFERENCES TO IT"):
                skipping = True
                out.append(line)
                continue
            if skipping:
                if line.startswith("   "):
                    continue
                skipping = False
            out.append(line)
        part = "\n".join(out)
    print("=" * 60)
    print(part.rstrip())
