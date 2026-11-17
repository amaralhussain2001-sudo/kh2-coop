"""Lane H: for every code site that loads a given global, show the instructions around it when the surrounding
function is short, and report where the function's address is stored in data (for example in a trap table).

  python -I tools/lane-h/short_refs.py <elf> <globalHex> [maxLen]
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
glob = int(sys.argv[2], 16)
maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 14
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
n = len(words)
JR_RA = 0x03E00008


def refs():
    out = []
    for i, w in enumerate(words):
        if (w >> 26) != 0x0F:
            continue
        reg = (w >> 16) & 31
        upper = (w & 0xFFFF) << 16
        for j in range(i + 1, min(n, i + 12)):
            x = words[j]
            op, rs = x >> 26, (x >> 21) & 31
            if op == 0x23 and rs == reg and ((upper + mips.s16(x & 0xFFFF)) & 0xFFFFFFFF) == glob:
                out.append(j)
                break
    return out


where = {}
for i, w in enumerate(words):
    where.setdefault(w, []).append(va + 4 * i)

for j in refs():
    # function start: walk back to the instruction after the previous 'jr ra' + delay slot
    s = j
    while s > 0 and j - s < 40 and words[s - 2] != JR_RA:
        s -= 1
    t = j
    while t < n and t - j < 40 and words[t] != JR_RA:
        t += 1
    length = t + 2 - s
    if length > maxlen or j - s >= 40:
        continue
    start = va + 4 * s
    print("function 0x%08X (%d instructions), stored at: %s" % (start, length, ", ".join("0x%08X" % a for a in where.get(start, [])[:4]) or "-"))
    for k in range(s, t + 2):
        print("    %08X  %s" % (va + 4 * k, mips.dis(words[k], va + 4 * k)))
