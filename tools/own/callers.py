"""Read-only: climb the call tree upwards. For an address: the function it is in and every place that calls,
jumps to or stores the address of that function; repeated for those places up to a depth.
  python -I tools/own/callers.py <addrHex> [depth]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
allw = []
for sva, soff, sfs in e.segs:
    allw.append((sva, struct.unpack_from("<%dI" % (sfs // 4), e.data, soff)))


def start(a):
    i = (a - va) // 4
    while i > 0:
        w = words[i]
        if (w >> 16) == 0x27BD and (w & 0x8000):
            # the true start may have instructions before the stack move; step back over a jr ra / nop boundary
            j = i
            while j > 0 and not ((words[j - 2] == 0x03E00008) or (words[j - 1] == 0 and words[j - 3] == 0x03E00008)) and i - j < 6:
                j -= 1
            return va + 4 * (j if i - j < 6 else i)
        i -= 1
    return a


def refs(s):
    out = []
    for sva, ws in allw:
        for i, w in enumerate(ws):
            if w == s:
                out.append(("data", sva + 4 * i))
            elif w == ((3 << 26) | (s >> 2)):
                out.append(("jal", sva + 4 * i))
            elif w == ((2 << 26) | (s >> 2)):
                out.append(("j", sva + 4 * i))
    # lui / addiu pairs that make the address
    lo = s & 0xFFFF
    hi = (s >> 16) + (1 if lo >= 0x8000 else 0)
    for i, w in enumerate(words):
        if (w >> 26) == 0x09 and (w & 0xFFFF) == lo:
            b = (w >> 21) & 31
            for j in range(i - 1, max(i - 8, -1), -1):
                x = words[j]
                if (x >> 26) == 0x0F and ((x >> 16) & 31) == b:
                    if (x & 0xFFFF) == hi:
                        out.append(("address taken", va + 4 * i))
                    break
    return out


def climb(a, depth, ind=""):
    s = start(a)
    r = refs(s)
    print("%s%08X: function %08X <- %s" % (ind, a, s, ", ".join("%s %08X" % x for x in r) or "nothing found"))
    if depth > 0:
        for kind, x in r:
            if kind in ("jal", "j"):
                climb(x, depth - 1, ind + "  ")


climb(int(sys.argv[1], 16), int(sys.argv[2]) if len(sys.argv) > 2 else 3)
