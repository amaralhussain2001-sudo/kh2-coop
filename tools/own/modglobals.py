"""Read-only: the global data addresses a range of the game program refers to (lui + offset pairs), grouped.
  python -I tools/own/modglobals.py <startHex> <endHex> [minDataHex]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
mind = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x00330000
OPS = {0x09: "addr", 0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x28: "sb", 0x29: "sh", 0x2B: "sw",
       0x31: "lwc1", 0x39: "swc1", 0x37: "ld", 0x3F: "sd", 0x1E: "lq", 0x1F: "sq"}
found = {}
for i in range((lo - va) // 4, (hi - va) // 4):
    w = words[i]
    op = w >> 26
    if op not in OPS:
        continue
    base = (w >> 21) & 31
    imm = w & 0xFFFF
    if imm >= 0x8000:
        imm -= 0x10000
    for j in range(i - 1, max(i - 16, -1), -1):
        x = words[j]
        if (x >> 26) == 0x0F and ((x >> 16) & 31) == base:
            addr = ((x & 0xFFFF) << 16) + imm
            if addr >= mind and (x & 0xFFFF) < 0x200:
                found.setdefault(addr, []).append((va + 4 * i, OPS[op]))
            break
for a in sorted(found):
    kinds = sorted({k for _, k in found[a]})
    print("%08X  %3d refs  %-24s first at %08X" % (a, len(found[a]), ",".join(kinds), found[a][0][0]))
