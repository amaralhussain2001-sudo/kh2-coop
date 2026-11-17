"""Scan the game's main program for every instruction whose 16-bit field is one number (a load, a store or an
addiu with that offset), for example a field of an object.
  python -I tools/own/find_off.py <hex16> [fromHex] [toHex]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
va, off, _fs = elf.segs[0]
want = int(sys.argv[1], 16)
a = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x00100000
b = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x002FF000
n = 0
for pc in range(a, b, 4):
    w = struct.unpack_from("<I", elf.data, off + pc - va)[0]
    op = w >> 26
    if (w & 0xFFFF) == want and (op in (9, 13, 25) or 32 <= op <= 63 or op in (26, 27, 30, 31)):
        print("%08X  %08X  %s" % (pc, w, mips.dis(w, pc)))
        n += 1
print(n, "places")
