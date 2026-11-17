"""Read-only probe: where the helpers are. At each snapshot frame: the party table (0x00348638: the player and two
friends), each one's class table and update method, position, HP, and the distance to each hero; the first two
mission gauges and counters.

  python -I tools/own/party_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import math
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []


def pos(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12))


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        party = struct.unpack("<3I", p.read(0x00348638, 12))
        g = struct.unpack("<2f", p.read(0x01D48FA4, 4) + p.read(0x01D48FA4 + 0x34, 4))
        c = (p.r32(0x01D48EFC), p.r32(0x01D48EFC + 0x38))
        lines.append("frame %d layout %d | player %08X twin %08X | gauges %.1f %.1f counters %d %d" % (
            fr, p.read(0x000F6F00, 1)[0], pl, tw, g[0], g[1], c[0], c[1]))
        pp = pos(pl) if pl else None
        tp = pos(tw) if tw else None
        if pp and tp:
            lines.append("  heroes %.0f apart; player at %s, twin at %s" % (dist(pp, tp), " ".join("%.0f" % v for v in pp), " ".join("%.0f" % v for v in tp)))
        for i, o in enumerate(party):
            if not o:
                lines.append("  party %d: none" % i)
                continue
            cls = p.r32(o)
            q = pos(o)
            slot = p.r32(o + 0x48C)
            hp = "HP %d/%d" % (p.r32(slot), p.r32(slot + 4)) if slot else "no slot"
            s = "  party %d: %08X class %08X update %08X %s at %s" % (i, o, cls, p.r32(cls + 0x10), hp, " ".join("%.0f" % v for v in q))
            if pp:
                s += " | to player %.0f" % dist(q, pp)
            if tp:
                s += " to twin %.0f" % dist(q, tp)
            lines.append(s)
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
