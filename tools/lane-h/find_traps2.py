"""Lane H: find trap tables stored as records (function pointer + small numbers).

Looks for runs of records of 8 or 12 bytes whose first word points into code and whose other words are small.
  python -I tools/lane-h/find_traps2.py <elf> [minRecords]
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
minrec = int(sys.argv[2]) if len(sys.argv) > 2 else 20
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
LO, HI = 0x00100000, 0x00330000
n = len(words)


def is_code(w):
    return LO <= w < HI and w % 4 == 0


for rec in (2, 3):
    for ptr_pos in range(rec):
        i = 0
        while i + rec <= n:
            j = i
            while j + rec <= n:
                ok = True
                for k in range(rec):
                    w = words[j + k]
                    if k == ptr_pos:
                        ok = ok and is_code(w)
                    else:
                        ok = ok and w < 0x10000
                if not ok:
                    break
                j += rec
            cnt = (j - i) // rec
            if cnt >= minrec:
                a = va + 4 * i
                first = [words[i + r * rec + ptr_pos] for r in range(min(cnt, 4))]
                small = [tuple(words[i + r * rec + k] for k in range(rec) if k != ptr_pos) for r in range(min(cnt, 6))]
                print("records of %d words, pointer at word %d: 0x%08X, %d records; first functions %s; numbers %s" % (
                    rec, ptr_pos, a, cnt, " ".join("%08X" % x for x in first), small))
                i = j
            else:
                i += 1
