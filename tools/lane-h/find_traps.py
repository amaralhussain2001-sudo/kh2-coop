"""Lane H: find the AI script engine's trap (syscall) tables in the game program.

A trap table is a run of function pointers. We look for runs of words that all point into the code area, and print
runs long enough to be a table, with a few chosen entries.

  python -I tools/lane-h/find_traps.py <elf> [minLen]
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
minlen = int(sys.argv[2]) if len(sys.argv) > 2 else 60
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
LO, HI = 0x00100000, 0x00330000


def is_code(w):
    return LO <= w < HI and w % 4 == 0


runs, i, n = [], 0, len(words)
while i < n:
    if is_code(words[i]):
        j = i
        while j < n and is_code(words[j]):
            j += 1
        if j - i >= minlen:
            runs.append((va + 4 * i, j - i))
        i = j
    else:
        i += 1
for a, ln in runs:
    idx = (a - va) // 4
    print("table at 0x%08X  entries %d   [0]=%08X [3]=%08X [23]=%08X" % (a, ln, words[idx], words[idx + 3], words[idx + 23] if ln > 23 else 0))
