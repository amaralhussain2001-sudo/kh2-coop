"""Write a button script for a boss jump disc: New Game, optional scene skips, then lock on and attack.

  python -I tools/lane-b75/make_fight_script.py <out.txt> <attackFromFrame> <endFrame> [skipFrame ...] [tri=N]

New Game = Circle x6 from frame 3000 (Japanese layout: Circle confirms). A skip = START, DOWN, Circle at the given
frame (pause menu of a scene: Continue / Skip Scene). Do not give a skip frame inside play: START would pause.
From attackFromFrame: R1 (lock on) now and then, Circle every 14 frames, and a short push of the left stick
towards the target every few seconds.
"""
import sys

out, attack_from, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tri = 0   # "tri=N": every N-th press is Triangle (Reaction Command) instead of Circle
skips = []
for x in sys.argv[4:]:
    if x.startswith("tri="):
        tri = int(x[4:])
    else:
        skips.append(int(x))
lines = ["# lane B75 boss test script (made by tools/lane-b75/make_fight_script.py)"]
for f in (3000, 3120, 3240, 3360, 3480, 3600):
    lines.append("%d 4 O" % f)
for t in skips:
    lines += ["%d 4 START" % t, "%d 4 DOWN" % (t + 30), "%d 4 O" % (t + 60)]
f = attack_from
n = 0
while f < end:
    if n % 60 == 0:
        lines.append("%d 4 R1" % f)
        f += 8
    lines.append("%d 4 %s" % (f, "TRI" if tri and n % tri == tri - 1 else "O"))
    f += 14
    n += 1
lines.append("%d 1 " % end)
open(out, "w").write("\n".join(lines) + "\n")
print("script", out, "lines", len(lines))
