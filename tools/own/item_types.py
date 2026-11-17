"""Read-only: the game's item table (03system.bin, BAR entry "item") sorted by type: for each type the ids, the
bag places (save + 0x3580 + place) and the buy / sell prices. For the design of plan row 39 (what is doubled).
  python -I tools/own/item_types.py [type ...]      (default: a summary of every type)"""
import collections
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "extract" / "kh2" / "03system.bin").read_bytes()
n = struct.unpack_from("<I", d, 4)[0]
ents = {}
for i in range(n):
    typ, name, off, size = struct.unpack_from("<I4sII", d, 16 + 16 * i)
    ents[name.rstrip(b"\0").decode("ascii", "replace")] = (typ, off, size)
typ, off, size = ents["item"]
ver, cnt = struct.unpack_from("<II", d, off)
by = collections.defaultdict(list)
for k in range(cnt):
    e = d[off + 8 + 0x18 * k: off + 8 + 0x18 * (k + 1)]
    iid, ityp, f0, f1, rank, stat, nm, ds, buy, sell, cmd, slot, pic, i1, i2 = struct.unpack("<HBBBBHHHHHHHHBB", e)
    by[ityp].append((iid, f0, f1, slot, buy, sell, cmd))
want = [int(x, 0) for x in sys.argv[1:]]
for t in sorted(by):
    rows = by[t]
    slots = sorted(r[3] for r in rows if not r[1] & 1)
    loop = [r for r in rows if r[4] and 2 * r[5] > r[4]]
    print("type %2d: %3d items, ids %04X..%04X, bag places %s, flag items %d, sold for more than half the price: %d" % (
        t, len(rows), min(r[0] for r in rows), max(r[0] for r in rows),
        ("%03X..%03X (%d different)" % (slots[0], slots[-1], len(set(slots)))) if slots else "-",
        sum(1 for r in rows if r[1] & 1), len(loop)))
    if t in want:
        for iid, f0, f1, slot, buy, sell, cmd in rows:
            print("    id %04X flags %02X %02X place %03X buy %5d sell %5d command %04X" % (iid, f0, f1, slot, buy, sell, cmd))
