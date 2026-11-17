"""Scan the Gummi flight module (ovl_gumibattle.x, loaded at 0x01F18000) for calls of / jumps to a routine and for
words that hold its address.
  python -I tools/own/ovl_find.py <targetHex> [...]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "analysis" / "lane-s3" / "ovl" / "ovl_gumibattle.x").read_bytes()
BASE = 0x01F18000
n = len(d) // 4
w = struct.unpack("<%dI" % n, d[:n * 4])
for arg in sys.argv[1:]:
    t = int(arg, 16)
    jal, j = 0x0C000000 | (t >> 2), 0x08000000 | (t >> 2)
    for i, x in enumerate(w):
        if x == jal:
            print("%08X  jal %08X" % (BASE + 4 * i, t))
        elif x == j:
            print("%08X  j   %08X" % (BASE + 4 * i, t))
        elif x == t:
            print("%08X  holds %08X" % (BASE + 4 * i, t))
