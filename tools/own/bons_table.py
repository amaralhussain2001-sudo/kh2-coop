"""Read-only: the game's bonus table (00battle.bin, BAR entry "bons") of the original disc's extracted files.
The game applies an entry to a unit slot with 0x001C0690(entry, slot) (read 2026-11-15): entry (16 bytes): + 0
reward id u8, + 1 character u8, + 2 HP up, + 3 MP up, + 4 Drive bar up, + 5 ITEM PLACES up, + 6 accessory places
up, + 7 armour places up, + 8 .. four shorts (abilities / items given). The item-place count goes through
0x00188958(record, count + up): the new places (record + 0x34 and + 0x44) are cleared.
  python -I tools/own/bons_table.py [character ...]      (default: a count per character; 4 = King Mickey)"""
import collections
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
d = (ROOT / "local" / "extract" / "kh2" / "00battle.bin").read_bytes()
assert d[:4] == b"BAR\x01", d[:4]
n = struct.unpack_from("<I", d, 4)[0]
ents = {}
for i in range(n):
    typ, name, off, size = struct.unpack_from("<I4sII", d, 16 + 16 * i)
    ents[name.rstrip(b"\0").decode("ascii", "replace")] = (typ, off, size)
typ, off, size = ents["bons"]
ver, cnt = struct.unpack_from("<II", d, off)
print("bons table: version %d, %d entries, size %d (8 + %d x 16 = %d)" % (ver, cnt, size, cnt, 8 + cnt * 16))
want = [int(x, 0) for x in sys.argv[1:]]
per = collections.Counter()
slots = collections.Counter()
for k in range(cnt):
    e = d[off + 8 + 16 * k: off + 8 + 16 * (k + 1)]
    rid, ch, hp, mp, drv, itm, acc, arm = struct.unpack_from("<8B", e, 0)
    things = struct.unpack_from("<4H", e, 8)
    per[ch] += 1
    slots[ch] += itm
    if ch in want:
        print("reward %3d char %2d HP+%d MP+%d drive+%d ITEM PLACES+%d accessory+%d armour+%d | %s" % (
            rid, ch, hp, mp, drv, itm, acc, arm, " ".join("%04X" % x for x in things)))
print("entries per character:", ", ".join("%d: %d (item places up, sum %d)" % (c, per[c], slots[c]) for c in sorted(per)))
