"""Read-only: the game's "player parameters" table (00battle.bin, BAR entry "plrp") of the original disc's
extracted files. The game applies an entry with 0x001C2EB8(id) -> 0x001C2D88(entry) (read 2026-11-15):
entry (0x80 bytes): + 0 id u16, + 2 character u8 (bit 0x80 = a Drive Form's record), + 3 HP, + 4 MP, + 5 AP,
+ 6 .. + 8 three more bytes, + 9 armour places, + 10 accessory places, + 11 ITEM PLACES, + 12 thirty-two shorts
(things given: item or ability number, bit 15 = on).
The item-place count goes through 0x00188958(record, count): when the count GROWS the new places (record + 0x34
and + 0x44) are cleared.
  python -I tools/own/plrp_table.py [character ...]      (default: every entry; character 4 = King Mickey)"""
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
print("bar entries:", ", ".join(sorted(ents)))
typ, off, size = ents["plrp"]
ver, cnt = struct.unpack_from("<II", d, off)
print("plrp table: version %d, %d entries, size %d (8 + %d x 0x80 = %d)" % (ver, cnt, size, cnt, 8 + cnt * 0x80))
want = [int(x, 0) for x in sys.argv[1:]]
for k in range(cnt):
    e = d[off + 8 + 0x80 * k: off + 8 + 0x80 * (k + 1)]
    pid, ch, hp, mp, ap, b6, b7, b8, arm, acc, itm = struct.unpack_from("<HBBBBBBBBBB", e, 0)
    things = [x for x in struct.unpack_from("<32H", e, 12) if x]
    tail = e[76:]
    if want and (ch & 0x7F) not in want:
        continue
    print("id %3d char %2d%s HP %3d MP %3d AP %3d (%d %d %d) armour %d accessory %d ITEM PLACES %d | given: %s%s" % (
        pid, ch & 0x7F, " FORM" if ch & 0x80 else "     ", hp, mp, ap, b6, b7, b8, arm, acc, itm,
        " ".join("%04X" % x for x in things), "" if not any(tail) else " | tail " + tail.hex()))
