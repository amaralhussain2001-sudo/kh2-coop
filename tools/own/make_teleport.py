"""TEST ONLY (ninth round, job 5): <base patch> + ONE MOVE OF A HERO TO A PLACE at one frame (tools/own/make_once.py with
the nine copies of an object's place that tools/own/make_pin.py writes: object + 0x70, 0x540, 0x590, 0x5C0, 0x6E0,
0x720, 0x730, 0x840, 0xC40; x at + 0, y at + 4, z at + 8). For walking a hero to a talk point of a story room.
  python -I tools/own/make_teleport.py <baseDir> <outDir> <sessionFrame> <objectHex> <x> <y|-> <z>     ("-" = keep y)"""
import pathlib
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out, frame, obj = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4], 16)
x, y, z = sys.argv[5], sys.argv[6], sys.argv[7]


def word(v):
    return "%08X" % struct.unpack("<I", struct.pack("<f", float(v)))[0]


args = []
for off in (0x70, 0x540, 0x590, 0x5C0, 0x6E0, 0x720, 0x730, 0x840, 0xC40):
    args.append("%08X=%s" % (obj + off, word(x)))
    if y != "-":
        args.append("%08X=%s" % (obj + off + 4, word(y)))
    args.append("%08X=%s" % (obj + off + 8, word(z)))
subprocess.check_call([sys.executable, "-I", str(ROOT / "tools" / "own" / "make_once.py"), base, out, frame] + args)
