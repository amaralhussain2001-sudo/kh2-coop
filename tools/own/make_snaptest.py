"""TEST ONLY: <base patch> + ONE line that lets a shortcut-start mission disc have a valid Continue snapshot, so
"Continue after a Game Over inside a mission" can be tested (sixth round, part 1).

How the game's Continue works (read from the program, VERIFIED with a recorder):
  - At every room load (0x00104910) the routine 0x001CD168 takes a snapshot: the whole save data to 0x01D499B0
    and the place record "now" (0x0032BAE0) to 0x01D5A970. It does so only if 0x001CD4C0 says yes: a mission
    is running that allows it (mission flag bit 12), or no mission runs and the room's first program number is
    below 51 (= a normal room, not a story / mission program).
  - Continue (0x001AF6F0, choice 2) asks 0x001CD520 for the snapshot's place, puts the snapshot back
    (0x001CD388) and jumps there. So the game goes back to the last NORMAL room; the story scene of that room
    plays again and jumps into the fight again.
  - A test disc whose New Game jumps straight into a mission never loads a normal room: the snapshot's place
    stays FF FF FF and the game stops (also with no patch at all).

  python -I tools/own/make_snaptest.py <baseDir> <outDir> A|B
  A: every room load takes the snapshot (0x001CD170: "yes"). Continue starts the mission room again at once.
  B: a first program number below 53 counts as a normal room (0x001CD4E4). On the test discs the New Game room
     (tt01, program 0x34 = 52) is then the remembered room: Continue goes there, its event program jumps into
     the mission again. This is the real game's order: remembered room -> event -> mission.
Identical on both PCs. Never part of the real patch.
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
base, out, kind = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
lines = [x for x in (base / NAME).read_text().splitlines() if x.strip()]
if kind == "A":
    lines.append("comment=TEST ONLY (make_snaptest.py A): the Continue snapshot is taken at every room load.")
    lines.append("patch=1,EE,001CD170,word,24020001")
elif kind == "B":
    lines.append("comment=TEST ONLY (make_snaptest.py B): programs below 53 count as a normal room for the Continue snapshot.")
    lines.append("patch=1,EE,001CD4E4,word,2DCE0035")
else:
    sys.exit("kind must be A or B")
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n")
for extra in base.glob("*.view"):
    (out / extra.name).write_bytes(extra.read_bytes())
print(out, len(lines), "lines")
