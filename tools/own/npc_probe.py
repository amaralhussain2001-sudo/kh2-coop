"""Read-only probe (tenth round, the user's shop girl: "after i talk with her i still saw her in Player1 but not player 2"):
at each snapshot frame, EVERY OBJECT of the room's object list (head 0x01D48DA0, next at object + 2228; as enemy_probe.py)
within NPC_RADIUS (default 900) of NPC_AT (default the accessory shop girl's spawn point in Market Street tt07, -2891, -889):
its address, object number and model name (object entry at object + 8), its place (+0x70), the flag word +0x0C (0x02 not
drawn, 0x20 no update, 0x40 hidden, 0x100 paused), +0x08 .. +0x14, and the own-screen layout byte (both heroes' places too).
  python -I tools/own/npc_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import math
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
CX, CZ = (float(v) for v in os.environ.get("NPC_AT", "-2891,-889").split(","))
R = float(os.environ.get("NPC_RADIUS", "900"))
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def ok(a):
    return 0x00080000 <= a < 0x02000000


def text_of(raw):
    best, cur = b"", b""
    for b in raw:
        if 0x20 <= b < 0x7F:
            cur += bytes([b])
        else:
            best, cur = (cur if len(cur) > len(best) else best), b""
    best = cur if len(cur) > len(best) else best
    return best.decode("ascii", "replace") if len(best) >= 4 else ""


def place(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12)) if ok(o) else (0.0, 0.0, 0.0)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x0034E948), p.r32(0x000F05CC)
        x1, _, z1 = place(h1)
        x2, _, z2 = place(h2)
        lines.append("f%d room %04X layout %d | P1 (%.0f, %.0f) P2 (%.0f, %.0f)" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r8(0x000F6F00), x1, z1, x2, z2))
        a, n = p.r32(0x01D48DA0), 0
        while ok(a) and n < 600:
            e = p.r32(a + 8)
            x, y, z = place(a)
            if ok(e) and math.hypot(x - CX, z - CZ) <= R and a not in (h1, h2):
                w = struct.unpack("<4I", p.read(a + 0x08, 16))
                lines.append("  f%d obj %08X %04X %-24s at (%.0f, %.0f, %.0f) flags+0C %08X (+08 %08X +10 %08X +14 %08X)" % (
                    fr, a, p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20)), x, y, z, w[1], w[0], w[2], w[3]))
            a = p.r32(a + 2228)
            n += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
