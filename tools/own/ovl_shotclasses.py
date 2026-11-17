"""The Gummi flight's shot classes (ninth round, job 6): for each call of "an enemy takes a hit" 0x01F26998: the
routine it is in, the class table that holds that routine, and the class's other routines (so that the start-up
of each kind of shot can be found).
  python -I tools/own/ovl_shotclasses.py"""
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "analysis" / "lane-s3" / "ovl" / "ovl_gumibattle.x").read_bytes()
BASE = 0x01F18000
n = len(d) // 4
w = struct.unpack("<%dI" % n, d[:n * 4])
jal = 0x0C000000 | (0x01F26998 >> 2)
for i, x in enumerate(w):
    if x != jal:
        continue
    k = i
    while k > 0 and (w[k] & 0xFFFF8000) != 0x27BD8000:      # addiu sp,sp,-N
        k -= 1
    start = BASE + 4 * k
    tabs = [BASE + 4 * t for t, y in enumerate(w) if y == start]
    row = "call at %08X in routine %08X" % (BASE + 4 * i, start)
    for t in tabs:
        ti = (t - BASE) // 4
        b = ti
        while b > 0 and BASE <= w[b - 1] < BASE + len(d) and ti - b < 16:
            b -= 1
        row += " | table %08X (the routine is its entry %d): %s" % (BASE + 4 * b, ti - b, " ".join("%08X" % y for y in w[b:b + 11]))
    print(row)
