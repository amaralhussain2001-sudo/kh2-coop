"""Lane B75: find places where a register is loaded with a small constant and a div/divu follows within a few instructions.

  python -I tools/lane-b75/find_const_div.py <elf> <constant> [window]
"""
import struct
import sys
sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 2)[0] + "/lane-a")
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
c = int(sys.argv[2], 0)
win = int(sys.argv[3]) if len(sys.argv) > 3 else 6
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
n = 0
for i, w in enumerate(words):
    op, rs, imm = w >> 26, (w >> 21) & 31, w & 0xFFFF
    if op in (0x09, 0x0D) and rs == 0 and imm == c:
        rt = (w >> 16) & 31
        for k in range(i + 1, min(len(words), i + 1 + win)):
            x = words[k]
            if (x >> 26) == 0 and (x & 0x3F) in (0x1A, 0x1B) and (((x >> 16) & 31) == rt or ((x >> 21) & 31) == rt):
                print("0x%08X  const in %s, div at 0x%08X" % (va + 4 * i, mips.R[rt], va + 4 * k))
                n += 1
                break
print("found", n)
