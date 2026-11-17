"""Read-only probe: at each snapshot frame, for both heroes (the engine's player 0x0034E948, the twin 0x000F05CC):
the object's address, its class table (object + 0), the table's defeat method (+0x5C) and per-frame method
(+0x0C), the unit slot's address (object + 0x48C), HP, the action word and the place.
  python -I tools/own/cls_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=120)
t0, lines = time.time(), []


def ok(a):
    return 0x000F0000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return "none"
    cls = p.r32(o)
    s = p.r32(o + 0x48C)
    x, y, z = struct.unpack("<3f", p.read(o + 0x70, 12))
    return "%08X class %08X (defeat %08X, step %08X) slot %08X hp %s a%02X (%.0f, %.0f, %.0f)" % (
        o, cls, p.r32(cls + 0x5C) if ok(cls) else 0, p.r32(cls + 0x0C) if ok(cls) else 0, s,
        "%d/%d" % (p.r32(s), p.r32(s + 4)) if ok(s) else "-", p.r32(o + 0x154) & 0xFFFF, x, y, z)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 600:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        lines.append("f%d room %04X go %d | P1 %s | P2 %s" % (fr, p.r32(0x0032BAE0) & 0xFFFF, 1 if p.r32(0x00350DF0) else 0,
                                                             hero(p.r32(0x0034E948)), hero(p.r32(0x000F05CC))))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail %s" % (fr, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
