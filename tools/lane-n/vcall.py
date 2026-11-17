"""Lane N: list the places in the game program that call a class-table method by its offset
(lw rX, OFF(rY) followed within 8 instructions by jalr rX).   python -I tools/lane-n/vcall.py <hexoffset> [lo hi]
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
off = int(sys.argv[1], 16)
lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x00100000
hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x00330000
for pc in range(lo, hi, 4):
    w = e.word(pc)
    if w is None or (w >> 26) != 0x23 or (w & 0xFFFF) != off:
        continue
    rt = (w >> 16) & 31
    for k in range(1, 9):
        w2 = e.word(pc + 4 * k)
        if w2 is None:
            break
        if (w2 & 0xFC1FFFFF) == 0x0000F809 and ((w2 >> 21) & 31) == rt:
            print("0x%08X: lw then jalr at 0x%08X" % (pc, pc + 4 * k))
            break
