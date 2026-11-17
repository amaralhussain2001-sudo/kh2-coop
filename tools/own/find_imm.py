"""Scan the game's main program for instructions that load or compare a 16-bit number (addiu / ori / li /
slti / sltiu / xori with that immediate), for example an object number.  With a few lines around each place.
  python -I tools/own/find_imm.py <hex16> [contextLines]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = elf.segs[0]
imm = int(sys.argv[1], 16)
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 3
n = 0
for pc in range(0x00100000, 0x00340000, 4):
    if off + pc - va + 4 > len(elf.data):
        break
    w = struct.unpack_from("<I", elf.data, off + pc - va)[0]
    op = w >> 26
    if (w & 0xFFFF) == imm and op in (0x09, 0x0D, 0x0A, 0x0B, 0x0E):
        rs = (w >> 21) & 31
        if op == 0x09 and rs != 0:
            continue                      # an offset added to a pointer, not a number
        n += 1
        print("---- %08X" % pc)
        for q in range(pc - 4 * ctx, pc + 4 * ctx + 4, 4):
            x = struct.unpack_from("<I", elf.data, off + q - va)[0]
            print("%s %08X  %s" % (">" if q == pc else " ", q, mips.dis(x, q)))
print(n, "places")
