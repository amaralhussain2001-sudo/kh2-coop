"""Read-only probe for tools/own/make_rec_prize.py. At each snapshot frame: for both heroes HP / most HP, MP / most MP (unit slot
+ 0 / + 4, + 0x180 / + 0x184), the Drive gauge (slot + 0x1B0, bars + 0x1B1); the two wallets (save + 0x2440 = 0x0032DF70;
player 2's: King Mickey's record + 0x48 = 0x0032E3A4); the sum of the material places of the bag (save + 0x360F .. 0x366D =
0x0032F13F .. 0x0032F19D); then the recorder's counts (kind: player 1 / player 2 / others) that are not 0.
  python -I tools/own/prize_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def ok(a):
    return 0x00100000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return "none"
    s = p.r32(o + 0x48C)
    if not ok(s):
        return "no slot"
    hp, mhp = struct.unpack("<2I", p.read(s, 8))
    mp, mmp = struct.unpack("<2I", p.read(s + 0x180, 8))
    d = p.read(s + 0x1B0, 3)
    return "HP %d/%d MP %d/%d Drive %d bars %d/%d" % (hp, mhp, mp, mmp, d[0], d[1], d[2])


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        mats = sum(p.read(0x0032F13F, 0x0032F19E - 0x0032F13F))
        cnt = struct.unpack("<96I", p.read(0x000F1D10, 384))
        rows = []
        for k in range(32):
            a, b, c = cnt[k], cnt[32 + k], cnt[64 + k]
            if a or b or c:
                rows.append("k%d %d/%d/%d" % (k, a, b, c))
        lines.append("f%d | P1 %s | P2 %s | munny P1 %d P2 %d | materials in the bag %d | prizes (kind P1/P2/others): %s" % (
            fr, hero(h1), hero(h2), p.r32(0x0032DF70), p.r32(0x0032E3A4), mats, " ".join(rows) or "none"))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
