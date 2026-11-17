"""Disassemble a range of a module file (default the Gummi flight, ovl_gumibattle.x; loaded at 0x01F18000), for reading.
  python -I tools/own/ovl_dis.py <startHex> <endHex> [<module name, e.g. ovl_shop>]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
import mips  # noqa: E402

MOD = sys.argv[3] if len(sys.argv) > 3 else "ovl_gumibattle"
d = (ROOT / "local" / "analysis" / "lane-s3" / "ovl" / (MOD + ".x")).read_bytes()
BASE = 0x01F18000
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
for pc in range(a, b, 4):
    w = struct.unpack_from("<I", d, pc - BASE)[0]
    print("%08X  %08X  %s" % (pc, w, mips.dis(w, pc)))
