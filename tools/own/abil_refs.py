"""Read-only (ninth round, answer D): the places in the main program that may walk A CHARACTER RECORD'S ABILITY LIST (record +
0x54, 80 shorts): every instruction that adds 84 to a register that is not the stack pointer, or loads / stores a
short at 84(register). For each: the routine it stands in (the nearest "addiu sp,sp,-N" above) and the line.
  python -I tools/own/abil_refs.py [<fromHex> <toHex>]      (default 0x00100000 .. 0x00320000)"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, fs = elf.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), elf.data, off)
lo = int(sys.argv[1], 16) if len(sys.argv) > 2 else 0x00100000
hi = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x00320000
for i, w in enumerate(words):
    pc = va + 4 * i
    if not lo <= pc < hi:
        continue
    op, rs, imm = w >> 26, (w >> 21) & 31, w & 0xFFFF
    if imm != 84 or rs == 29:
        continue
    if op in (0x09, 0x19, 0x21, 0x25, 0x29):                  # addiu / daddiu / lh / lhu / sh
        k = i
        while k > 0 and not ((words[k] >> 16) == 0x27BD and (words[k] & 0x8000)):
            k -= 1
        print("%08X  %-34s routine %08X" % (pc, mips.dis(w, pc), va + 4 * k))
