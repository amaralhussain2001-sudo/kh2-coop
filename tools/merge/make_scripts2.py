"""Merge lane: button scripts for the tests added with merged build v2 (lane G: own attacks and commands).

A script line that matches a frame first wins (lines do not add up), so holds are written as back-to-back lines.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "tests" / "scripts" / "merge"
NEWGAME = ["3000 4 O", "3120 4 O", "3240 4 O", "3360 4 O", "3480 4 O", "3600 4 O"]


def w(name, comment, lines):
    (OUT / name).write_text("# " + comment + "\n" + "\n".join(lines) + "\n")


def mash(a, b, step=20):
    return ["%d 4 O" % t for t in range(a, b, step)]


def fire(t):
    """L1 held for 60 frames with one Circle press inside (shortcut 1 = Fire with the test-only skill kit)."""
    return ["%d 20 L1" % t, "%d 4 L1 O" % (t + 20), "%d 36 L1" % (t + 24)]


# (i) attacks: only pad 2 presses Circle 4700-5000, only pad 1 5100-5400, both 5500-5800
w("atk_p1.txt", "fight disc: New Game; P1 presses Circle 5100-5400 and 5500-5800",
  NEWGAME + mash(5100, 5400) + mash(5500, 5800) + ["5900 1 "])
w("atk_p2.txt", "fight disc: P2 presses Circle 4700-5000 and 5500-5800",
  mash(4700, 5000) + mash(5500, 5800) + ["5900 1 "])

# (j) magic (test-only skill kit): P1 first leaves the save point (it refills HP and MP); then P2 casts Fire three
# times (4700-4940), then P1 three times (5000-5240)
w("fire_p1.txt", "roam disc + test kit: New Game; P1 walks off the save point at 4500; three Fire casts from 5000",
  NEWGAME + ["4500 33 LY=0"] + fire(5000) + fire(5080) + fire(5160) + ["5400 1 "])
w("fire_p2.txt", "roam disc + test kit: P2 casts Fire three times from 4700",
  fire(4700) + fire(4780) + fire(4860) + ["5400 1 "])
print("scripts written to", OUT)
