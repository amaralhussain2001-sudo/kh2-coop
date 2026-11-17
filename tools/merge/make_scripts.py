"""Merge lane: write the button scripts of the combined test run into tests/scripts/merge/.

Japanese layout: Circle (O) confirms and attacks, Cross (X) jumps. Stick: LY=0 up, LY=255 down, LX=0 left, LX=255 right.
Free-roam disc (Merlin's house, hero at (-320, 0, -800), twin at (-210, 0, -800), west door box x -695..-595,
z -625..-475): with the camera still at its start position, up = +z and left = -x, about 8 units per frame.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "tests" / "scripts" / "merge"
OUT.mkdir(parents=True, exist_ok=True)
NEWGAME = ["3000 4 O", "3120 4 O", "3240 4 O", "3360 4 O", "3480 4 O", "3600 4 O"]
OPENING = NEWGAME + ["4200 4 START", "4230 4 DOWN", "4260 4 O", "4680 4 START", "4710 4 DOWN", "4740 4 O"]
BOXES = ["5200 4 O", "5350 4 O", "5500 4 O", "5650 4 O", "5800 4 O", "5950 4 O"]


def w(name, comment, lines):
    (OUT / name).write_text("# " + comment + "\n" + "\n".join(lines) + "\n")


def door(t, who):
    """Walk from the start spot into the west door volume and stop there (found by trial, tests m2-d-*):
    twin 36 frames up then 60 left (ends about (-605, -505)), hero 33 up then 50 left (walks into the door near
    z -600). Longer pushes make the hero slide along the wall out of the door volume."""
    if who == "hero":
        return ["%d 33 LY=0" % t, "%d 50 LX=0" % (t + 60)]
    return ["%d 36 LY=0" % t, "%d 60 LX=0" % (t + 60)]


# (a) who controls whom, paths that do not cross: P1 up, P2 right, then jumps
w("ctl_p1.txt", "roam disc: New Game; P1 runs up 40 frames at 4700; P1 jumps at 5200",
  NEWGAME + ["4700 40 LY=0", "5200 4 X", "5600 1 "])
w("ctl_p2.txt", "roam disc: P2 runs right 40 frames at 4900; P2 jumps at 5100",
  ["4900 40 LX=255", "5100 4 X", "5600 1 "])

# (d) exits. d1: P2 alone at the door (pushes 300 frames), then P1 arrives; afterwards each pad moves its own hero
w("door_p2first_p1.txt", "roam disc: New Game; P1 waits, walks to the door at 4900; in the next room runs right at 5700",
  NEWGAME + door(4900, "hero") + ["5700 40 LX=255", "6200 1 "])
w("door_p2first_p2.txt", "roam disc: P2 walks into the door volume at 4500 and stays; in the next room runs left at 5900",
  door(4500, "twin") + ["5900 40 LX=0", "6200 1 "])
# d2: P1 alone walks into the door and pushes forward again, the twin never moves
w("door_p1alone_p1.txt", "roam disc: New Game; P1 walks into the door at 4500 and pushes forward again at 4800",
  NEWGAME + door(4500, "hero") + ["4800 30 LY=0", "5400 1 "])
w("idle_p2.txt", "pad 2 does nothing", ["5400 1 "])

# (c) fight: both idle
w("fight_idle_p1.txt", "fight disc: New Game, then nothing", NEWGAME + ["7200 1 "])

# (e) New Game on the real disc: opening skipped, tutorial boxes, each pad moves its own Roxas, then the bot
w("newgame_p1.txt", "real start: New Game, skip the opening movie and the first scene, dismiss the tutorial boxes, "
  "P1 runs up at 6300 and jumps at 6900; the bot takes over after 7100",
  OPENING + BOXES + ["6300 60 LY=0", "6900 4 X", "7100 1 "])
w("newgame_p2.txt", "real start: P2 runs right at 6500 and jumps at 6700; the bot takes over after 7100",
  ["6500 60 LX=255", "6700 4 X", "7100 1 "])

# (f) save + defeat + Continue: scripts save_cont_p1.txt / save_cont_p2.txt are written by the test command (see M-merge.md)

# (g) long sync: out of the door (P2 first), back in and out again (both walk 'down' for 150 frames after arriving), then bot
w("sync_roam_p1.txt", "roam disc: New Game; door at 4900; both walk back at 5600 and out again at 6500; bot after 7400",
  NEWGAME + door(4900, "hero") + ["5600 150 LY=255", "6500 150 LY=255", "7400 1 "])
w("sync_roam_p2.txt", "roam disc: P2 door at 4500; both walk back at 5600 and out again at 6500; bot after 7400",
  door(4500, "twin") + ["5600 150 LY=255", "6500 150 LY=255", "7400 1 "])
w("newgame_only.txt", "New Game (Circle x6); the bot takes over after 3700", NEWGAME + ["3700 1 "])
w("wait_3700.txt", "nothing until play, then the bot", ["3700 1 "])

# (h) one player alone: save and walk out of the door (lane B's walk), then the bot
w("solo_p1.txt", "roam disc WITHOUT twin: New Game, walk up and left out of the west door at 4500; bot after 5200",
  NEWGAME + ["4500 30 LY=0", "4560 90 LX=0", "5200 1 "])
w("solo_open_p1.txt", "real start without twin: New Game, skip the opening, dismiss the boxes; bot after 6200",
  OPENING + BOXES + ["6200 1 "])
print("scripts written to", OUT)
