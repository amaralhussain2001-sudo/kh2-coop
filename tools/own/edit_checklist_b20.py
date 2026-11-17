"""One-off: docs/PARITY-CHECKLIST.md after test build 20 (ninth round): the toy cannon's own views and the Gummi
flight's score for each player. Run once, AFTER the build is in dist:
  python -I tools/own/edit_checklist_b20.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "PARITY-CHECKLIST.md"
t = p.read_bytes().decode("utf-8")
if "SINCE BUILD 20" in t:
    raise SystemExit("already there")
PAIRS = [
    ("each turned and fired by its own controller; ONE shared view (own-screen option --cannon1view: the cannon's "
     "camera kind exists for camera 1 only); one score and one toy count for both, \"Reload\" loads both.",
     "each turned and fired by its own controller; SINCE BUILD 20 A VIEW FOR EACH PLAYER (own-screen option "
     "--cannon2view: camera 2 is the game's still view, moved to player 2's cannon; ninth round parts 95 and 98: "
     "runs cnE, cnF, t2A); one score and one toy count for both, \"Reload\" loads both."),
    ("the one hull gauge shows the weaker ship; a repair mends both. Still one score and one gauge |",
     "the one hull gauge shows the weaker ship; a repair mends both. SINCE BUILD 20 A SCORE FOR EACH PLAYER (glue 66: "
     "a cannon shot's points go to the ship that fired it; player 1's number in the SCORE frame, player 2's beside "
     "it; other weapons count for player 1) and a digit at the gauge for whose ship it shows (ninth round part 97: "
     "runs gr1 to gr3, gu1 to gu3) |"),
]
for old, new in PAIRS:
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)
p.write_bytes(t.encode("utf-8"))
print("checklist: the toy cannon and the Gummi routes have their build 20 text")
