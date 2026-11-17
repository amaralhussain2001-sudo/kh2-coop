"""Read-only: find a text in the game program's data and the code that makes its address (lui / addiu pairs).
  python -I tools/own/strrefs.py <text> [<text> ...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)


def refs(target):
    lo = target & 0xFFFF
    hi = (target >> 16) + (1 if lo >= 0x8000 else 0)
    out = []
    for i, w in enumerate(words):
        if (w >> 26) == 0x09 and (w & 0xFFFF) == lo:
            b = (w >> 21) & 31
            for j in range(i - 1, max(i - 12, -1), -1):
                x = words[j]
                if (x >> 26) == 0x0F and ((x >> 16) & 31) == b:
                    if (x & 0xFFFF) == hi:
                        out.append(va + 4 * i)
                    break
    out += [va + 4 * i for i, w in enumerate(words) if w == target]
    return out


for text in sys.argv[1:]:
    name = text.encode("ascii") + b"\0"
    for sva, soff, sfs in e.segs:
        blob = e.data[soff:soff + sfs]
        i = blob.find(name)
        while i >= 0:
            if i == 0 or blob[i - 1] == 0:
                a = sva + i
                near = [x.decode("ascii", "replace") for x in blob[max(i - 48, 0):i + 48].split(b"\0") if x and all(32 <= c < 127 for c in x)]
                print("%s at %08X  near: %s  used at: %s" % (text, a, " | ".join(near), " ".join("%08X" % r for r in refs(a)) or "-"))
            i = blob.find(name, i + 1)
