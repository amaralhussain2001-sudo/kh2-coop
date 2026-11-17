"""Lane H: list the AI script engine's trap tables: runs of records (function pointer, argument word), where the
argument word is the number of inputs, plus 0x40000000 when the trap returns a value.

  python -I tools/lane-h/traptables.py <elf>                 list the tables
  python -I tools/lane-h/traptables.py <elf> <baseHex> <index> [index ...]   print chosen records of one table
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
n = len(words)
LO, HI = 0x00100000, 0x00330000


def rec_ok(i):
    p, s = words[i], words[i + 1]
    return LO <= p < HI and p % 4 == 0 and (s & 0xBFFFFFE0) == 0


if len(sys.argv) > 2:
    base = int(sys.argv[2], 16)
    b = (base - va) // 4
    for a in sys.argv[3:]:
        k = int(a)
        p, s = words[b + 2 * k], words[b + 2 * k + 1]
        print("index %d: function 0x%08X, %d in, %d out" % (k, p, s & 0x1F, 1 if s & 0x40000000 else 0))
    sys.exit(0)

i = 0
while i + 1 < n:
    if rec_ok(i):
        j = i
        while j + 1 < n and rec_ok(j):
            j += 2
        cnt = (j - i) // 2
        if cnt >= 8:
            print("table at 0x%08X: %d records" % (va + 4 * i, cnt))
        i = j
    else:
        i += 1
