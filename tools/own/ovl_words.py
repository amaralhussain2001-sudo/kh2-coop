"""Words of the Gummi flight module file (ovl_gumibattle.x, loaded at 0x01F18000) at an address.
  python -I tools/own/ovl_words.py <addrHex> [count]"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "analysis" / "lane-s3" / "ovl" / "ovl_gumibattle.x").read_bytes()
a = int(sys.argv[1], 16)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for i in range(n):
    o = a + 4 * i - 0x01F18000
    print("%08X  %08X" % (a + 4 * i, struct.unpack_from("<I", d, o)[0]) if 0 <= o < len(d) - 3 else "%08X  (outside the file)" % (a + 4 * i))
