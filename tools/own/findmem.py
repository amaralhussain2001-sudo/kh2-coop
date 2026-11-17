"""List memory instructions (lb/lbu/lh/lhu/lw/sb/sh/sw/ld/sd and addiu) whose 16-bit offset is one of the given
values.  python -I tools/own/findmem.py <hex> [<hex> ...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

e = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
vals = {int(x, 16) for x in sys.argv[1:]}
va, off, fs = e.segs[0]
words = struct.unpack_from("<%dI" % (fs // 4), e.data, off)
OPS = {0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B, 0x37, 0x3F, 0x09}
for i, w in enumerate(words):
    if (w >> 26) in OPS and (w & 0xFFFF) in vals:
        pc = va + 4 * i
        print("%08X  %s" % (pc, mips.dis(w, pc)))
