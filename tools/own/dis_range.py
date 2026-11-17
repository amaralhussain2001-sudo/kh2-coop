"""Disassemble a range of the game's main program (the ELF on disc), for reading.
  python -I tools/own/dis_range.py <startHex> <endHex>"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, _fs = elf.segs[0]
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
for pc in range(a, b, 4):
    w = struct.unpack_from("<I", elf.data, off + pc - va)[0]
    print("%08X  %08X  %s" % (pc, w, mips.dis(w, pc)))
