"""TEST ONLY: <base patch> + lines that send a jump test disc into ONE ROOM WITH ONE PROGRAM NUMBER after New Game.
For the mission programs that the world's own table does not know (small numbers: Mushroom XIII, room puzzles,
the phases of the carpet ride, the ship battles), where the Type 2 jump of tools/own/make_jumpkit.py shows a
black screen. Same on both PCs. Never part of the real patch.

How: the disc test-s1-tt137 has its jump record at 0x01C56310 (01 00 00 00 | type | world | area | entrance |
program | fade 0x4002, 16 bits each from +4). While the record still holds the disc's own values, the lines make
it a Type 1 jump (the room's programs come from the save data) to world / area / entrance 0, and write the
program number into the save data's three program words of that room (map, battle, event):
save 0x0032BB30 + 0x10 + world * 0x180 + area * 6.

  python -I tools/own/make_jumpkit1.py <baseDir> <outDir> <worldHex> <areaDecimal> <programDecimal> [entranceDecimal]
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REC = 0x01C56310
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
world, area, prog = int(sys.argv[3], 16), int(sys.argv[4]), int(sys.argv[5])
entrance = int(sys.argv[6]) if len(sys.argv) > 6 else 0
table = 0x0032BB30 + 0x10 + world * 0x180 + area * 6
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_jumpkit1.py world %02X area %d program %d): for tests only." % (world, area, prog))
writes = [(REC + 4, 1), (REC + 6, world), (REC + 8, area), (REC + 10, entrance),
          (table, prog), (table + 2, prog), (table + 4, prog),
          (REC + 12, 0)]                       # the last one ends the condition
lines.append("patch=1,EE,E0%02X4002,extended,%08X" % (len(writes) + 1, REC + 14))   # the fade word of the jump record
lines.append("patch=1,EE,E0%02X0089,extended,%08X" % (len(writes), REC + 12))       # still the disc's own program (137)
for a, v in writes:
    lines.append("patch=1,EE,%08X,extended,%08X" % (0x10000000 | a, v))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "world %02X area %d program %d (save words at %08X)" % (world, area, prog, table))
