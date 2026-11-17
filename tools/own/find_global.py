"""Scan the game's main program for instructions that read or write one global address through a
"lui reg,hi" + "op reg2,lo(reg)" pair (the lui within the 12 instructions before). With lines around each place.
  python -I tools/own/find_global.py <addrHex> [linesBefore] [linesAfter]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = elf.segs[0]
addr = int(sys.argv[1], 16)
before = int(sys.argv[2]) if len(sys.argv) > 2 else 4
after = int(sys.argv[3]) if len(sys.argv) > 3 else 3
lo = addr & 0xFFFF
hi = ((addr + 0x8000) >> 16) & 0xFFFF
MEM = {0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B, 0x37, 0x3F, 0x31, 0x39, 0x09}


def word(pc):
    return struct.unpack_from("<I", elf.data, off + pc - va)[0]


n = 0
for pc in range(0x00100000, 0x00340000, 4):
    if off + pc - va + 4 > len(elf.data):
        break
    w = word(pc)
    if (w >> 26) in MEM and (w & 0xFFFF) == lo:
        base = (w >> 21) & 31
        ok = False
        for q in range(pc - 4, pc - 52, -4):
            x = word(q)
            if (x >> 26) == 0x0F and ((x >> 16) & 31) == base:
                ok = (x & 0xFFFF) == hi
                break
        if ok:
            n += 1
            print("---- %08X" % pc)
            for q in range(pc - 4 * before, pc + 4 * after + 4, 4):
                print("%s %08X  %s" % (">" if q == pc else " ", q, mips.dis(word(q), q)))
print(n, "places")
