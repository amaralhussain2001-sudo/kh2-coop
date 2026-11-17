"""Lane A: list every 'jal <target>' in the game program and how a0 is set just before it.

  python -I tools/lane-a/callers.py <elf> <targetHex> [contextLines]
"""
import struct
import sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import mips  # noqa: E402

e = mips.Elf(sys.argv[1])
target = int(sys.argv[2], 16)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
jal = (0x03 << 26) | ((target >> 2) & 0x3FFFFFF)
jmp = (0x02 << 26) | ((target >> 2) & 0x3FFFFFF)
va, off, fs = e.segs[0]
words = struct.unpack_from(f"<{fs // 4}I", e.data, off)
sites = [i for i, w in enumerate(words) if w in (jal, jmp)]
print(f"calls to 0x{target:08X}: {len(sites)}")
kinds = {}
for i in sites:
    pc = va + 4 * i
    # look at the delay slot and up to 6 instructions back for the last write to a0
    how = "?"
    cand = [i + 1] + list(range(i - 1, i - 8, -1))
    for k in cand:
        w = words[k]
        op, rs, rt, rd, fn = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, w & 63
        if op == 0 and rd == 4 and fn in (0x2D, 0x21, 0x25):
            how = "a0 = " + (mips.R[rs] if rt == 0 else mips.R[rt] if rs == 0 else f"{mips.R[rs]}+{mips.R[rt]}")
            if rs == 0 and rt == 0:
                how = "a0 = 0"
            break
        if op in (0x09, 0x19, 0x0D) and rt == 4:
            how = f"a0 = {mips.R[rs]} + {mips.s16(w & 0xFFFF)}" if rs else f"a0 = {mips.s16(w & 0xFFFF)}"
            break
        if op in mips.MEM and rt == 4 and op in (0x23, 0x24, 0x25, 0x20, 0x21, 0x37, 0x27):
            how = f"a0 = {mips.MEM[op]} {mips.s16(w & 0xFFFF)}({mips.R[rs]})"
            break
    kinds[how] = kinds.get(how, 0) + 1
    print(f"0x{pc:08X}  {'jal' if words[i] == jal else 'j  '}  {how}")
    if ctx:
        for k in range(i - ctx, i + 2):
            print(f"      {va + 4 * k:08X}  {mips.dis(words[k], va + 4 * k)}")
print("summary:", sorted(kinds.items(), key=lambda x: -x[1]))
