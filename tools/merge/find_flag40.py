"""Search helper: small routines of the game program that set or clear flag 0x40 (hidden) in a 2D object's
flag word (+12), and their callers inside a given address range.

  python -I tools/merge/find_flag40.py <elf> <rangeStartHex> <rangeEndHex>
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)


def addr(i):
    return va + 4 * i


# 1. routines: lw rX,12(a0) ; ori rX,rX,0x40 ; ... sw rX,12(a0)   or   and with ~0x40
setters, clearers = [], []
for i, w in enumerate(words[:-4]):
    if (w & 0xFFE0FFFF) == 0x8C80000C:                       # lw rt,12(a0)
        rt = (w >> 16) & 31
        nxt = words[i + 1:i + 5]
        for k, n in enumerate(nxt):
            if n == (0x34000040 | (rt << 21) | (rt << 16)):  # ori rt,rt,0x40
                setters.append(addr(i))
            if (n & 0xFC00FFFF) == 0x2400FFBF:               # addiu rX,zero,-65
                clearers.append(addr(i))
print("routines that set flag 0x40 through a0+12:", ["%08X" % a for a in setters])
print("routines that clear flag 0x40 through a0+12:", ["%08X" % a for a in clearers])

# 2. inline uses inside the range
for i, w in enumerate(words):
    a = addr(i)
    if lo <= a < hi:
        if (w & 0xFC00FFFF) == 0x34000040 and ((w >> 21) & 31) == ((w >> 16) & 31):
            print("  inline ori 0x40 at %08X: %s" % (a, mips.dis(w, a)))
        if (w & 0xFC00FFFF) == 0x2400FFBF:
            print("  inline mask -65 at %08X: %s" % (a, mips.dis(w, a)))

# 3. calls from the range to those routines (allowing an entry a few words before the lw)
targets = {}
for s in setters:
    for back in range(0, 3):
        targets[s - 4 * back] = "set"
for c in clearers:
    for back in range(0, 3):
        targets[c - 4 * back] = "clear"
for i, w in enumerate(words):
    a = addr(i)
    if lo <= a < hi and (w >> 26) in (2, 3):
        t = (w & 0x03FFFFFF) << 2
        if t in targets:
            print("  %08X %s -> %s routine %08X" % (a, mips.dis(w, a), targets[t], t))
