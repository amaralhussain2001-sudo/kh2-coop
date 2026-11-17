"""TEST ONLY: like tools/own/make_jumpkit1.py (a Type 1 jump into one room of the jump disc test-s1-tt137), but the
room's THREE program numbers are given one by one: map, battle, event. For the missions whose number exists only
in the room's battle programs (the heroes come from another map program; with one number for all three the room
has no hero: the sweep's class NO-HERO). Same on both PCs. Never part of the real patch.

  python -I tools/own/make_jumpkit2.py <baseDir> <outDir> <worldHex> <areaDecimal> <map> <battle> <event> [entrance]
  (save words of the room: 0x0032BB30 + 0x10 + world * 0x180 + area * 6: map, battle, event)
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
import os
REC = int(os.environ.get("JUMPREC", "01C56310"), 16)     # the jump record's address (another disc: find it with jumpfind_probe.py)
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
world, area = int(sys.argv[3], 16), int(sys.argv[4])
pm, pb, pe = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
entrance = int(sys.argv[8]) if len(sys.argv) > 8 else 0
table = 0x0032BB30 + 0x10 + world * 0x180 + area * 6
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_jumpkit2.py world %02X area %d programs %d / %d / %d entrance %d): for tests only."
             % (world, area, pm, pb, pe, entrance))
writes = [(REC + 4, 1), (REC + 6, world), (REC + 8, area), (REC + 10, entrance),
          (table, pm), (table + 2, pb), (table + 4, pe),
          (REC + 12, 0)]                       # the last one ends the condition
lines.append("patch=1,EE,E0%02X4002,extended,%08X" % (len(writes) + 1, REC + 14))
lines.append("patch=1,EE,E0%02X0089,extended,%08X" % (len(writes), REC + 12))
for a, v in writes:
    lines.append("patch=1,EE,%08X,extended,%08X" % (0x10000000 | a, v))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "world %02X area %d programs %d/%d/%d entrance %d" % (world, area, pm, pb, pe, entrance))
