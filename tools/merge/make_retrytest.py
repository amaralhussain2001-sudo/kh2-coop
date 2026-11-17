"""TEST ONLY: <base patch or "-"> + lines that (1) give the game a valid "retry" record on a shortcut-start
mission disc and (2) hold the HP of the given unit slots at 1, so a Game Over comes quickly.

Background (VERIFIED 2026-11-10, test c1-fightmem): the game keeps location records after "Now" (0x0032BAE0):
0x0032BAF0, 0x0032BB00 and 0x0032BB10, each = world, room, door, a byte, then three 16-bit event numbers.
On a disc whose New Game jumps straight into a mission the record at 0x0032BB00 is all FF, and Continue after a
Game Over then goes to "room FFFF" and stops (also in the unmodified game). This tool writes the mission's own
location into that record every frame.

  python -I tools/merge/make_retrytest.py <basePatchDir|-> <outDir> <world> <room> <event> [slotHex ...]
  all numbers hex, for example: 10 02 37 01C6C4E8 01C6C750
Identical on both PCs, so a linked session stays in sync. Never part of the real game patch.
"""
import pathlib
import sys

base, out = sys.argv[1], pathlib.Path(sys.argv[2])
world, room, event = (int(x, 16) for x in sys.argv[3:6])
slots = [int(x, 16) for x in sys.argv[6:]]
if base != "-":
    lines = [x for x in (pathlib.Path(base) / "SLPM-66675_F266B00B.pnach").read_text().splitlines() if x.strip()]
else:
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)"]
lines.append("comment=TEST ONLY: retry record 0x0032BB00 = world %02X room %02X, events %02X; HP of %d unit slot(s) held at 1."
             % (world, room, event, len(slots)))
lines.append("patch=1,EE,0032BB00,byte,%02X" % world)
lines.append("patch=1,EE,0032BB01,byte,%02X" % room)
lines.append("patch=1,EE,0032BB02,byte,00")
for a in (0x0032BB04, 0x0032BB06, 0x0032BB08):
    lines.append("patch=1,EE,%08X,short,%04X" % (a, event))
for s in slots:
    lines.append("patch=1,EE,%08X,word,00000001" % s)
out.mkdir(parents=True, exist_ok=True)
(out / "SLPM-66675_F266B00B.pnach").write_text(chr(10).join(lines) + chr(10))
print(out, len(lines), "lines")
