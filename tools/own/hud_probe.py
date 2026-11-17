"""Read-only probe (eighth round, part 77): WHOSE HP DOES PLAYER 1's GAUGE SHOW. At each snapshot frame the room,
the engine's player (0x0034E948) and the twin (0x000F05CC) with HP, and the HUD's party table (0x00348638: three
objects, then three flag words): slot 0 is the hero the game's own player gauge shows.
  python -I tools/own/hud_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "600"))
p = Pine(port, wait=120)
t0, lines = time.time(), []


def ok(a):
    return 0x00100000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return "none"
    s = p.r32(o + 0x48C)
    hp = "%d/%d" % (p.r32(s), p.r32(s + 4)) if ok(s) else "noslot"
    return "%08X hp %s" % (o, hp)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        t = struct.unpack("<6I", p.read(0x00348638, 24))
        who = "PLAYER 1's" if t[0] == pl and pl else "THE TWIN" if t[0] == tw and tw else "nobody" if not t[0] else "another object"
        lines.append("f%d room %04X | P1 %s | P2 %s | HUD slot 0 = %08X (%s), slots 1, 2 = %08X %08X, flags %X %X %X" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, hero(pl), hero(tw), t[0], who, t[1], t[2], t[3], t[4], t[5]))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail %s" % (fr, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
