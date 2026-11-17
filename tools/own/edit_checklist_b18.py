"""One-off: docs/PARITY-CHECKLIST.md after test build 18 (eighth round): the three rows of the small games that had
one hero for both players (the toy cannon, the carpet escape, the sidecar). Run once, AFTER the build is in dist:
  python -I tools/own/edit_checklist_b18.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "PARITY-CHECKLIST.md"
t = p.read_text(encoding="utf-8")
if "SINCE BUILD 18" in t:
    raise SystemExit("already there")
PAIRS = [
    ("| NM-07 Gift Wrapping (toy cannon) | ONE cannon; both controllers aim and shoot it (twenty-eighth glue). A second "
     "cannon was tried: wrong view for player 2 and 50 fault lines | part 7e: nt-nm63, sp-nm63 |",
     "| NM-07 Gift Wrapping (toy cannon) | SINCE BUILD 18 TWO CANNONS: a second cannon is made at run time beside the "
     "first (glue 56), each turned and fired by its own controller; ONE shared view (own-screen option --cannon1view: "
     "the cannon's camera kind exists for camera 1 only); one score and one toy count for both, \"Reload\" loads "
     "both. Played by a script to the game's end and on into the next room, no fault line (glue 57) | eighth "
     "round parts 71, 74 to 78: one4, one7, one8, one10 (v88: 50 fault lines at the end), one16, one17 (v89: none) |"),
    ("| AL-07 carpet escape | One hero by the game's design; both controllers drive him | nt-al61 |",
     "| AL-07 carpet escape | SINCE BUILD 18 TWO HEROES, EACH ON HIS OWN ESCAPE CARPET (glues 54 and 56: the second "
     "hero and his carpet are made at run time): own steering, own HP, down-and-rescue as in a fight; flown to the "
     "end by a script. Player 1's gauge shows player 1 (hud_probe) | eighth round parts 71, 74, 77, 78: one4, "
     "one5, one6, one9, one14, one18 |"),
    ("| EH-09 the dragon (flying bike / sidecar) | One bike; both controllers | nt-eh72 |",
     "| EH-09 the dragon (flying bike / sidecar) | SINCE BUILD 18 TWO MACHINES (glues 55 and 56: the second hero is "
     "made at run time and gets the sidecar's state): own \"Attack / Laser / Drain\", own HP; a Game Over and "
     "\"Continue\" bring both back. Player 1's gauge shows player 1 (hud_probe) | eighth round parts 71, 74, "
     "77, 78: one4, one5, one6, one9, one14, one18 |"),
]
for old, new in PAIRS:
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("checklist: the three small-game rows say build 18")
