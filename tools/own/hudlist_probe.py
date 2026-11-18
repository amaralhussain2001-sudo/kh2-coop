"""Read-only probe (partner's Drive display, part 150): the field HUD's draw list in order (manager 0x00347EA0: list = [mgr+4],
first = [list+12], next = [object+8]; the draw-all loop 0x00139308 walks it so). Per object: address, class, flags +12, group +16,
and its place inside player 1's / player 2's big gauge ([0x003485EC] / [0x000F7F20]) when it is a part of one.
  python -I tools/own/hudlist_probe.py <testDir> <pinePort> <frame,...> <out.txt>
"""
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
t0 = time.time()
lines = []
seen = 0
while seen < len(frames) and time.time() - t0 < 1200.0:
    f = frames[seen]
    if not (test_dir / ("p1_f%06d.png" % f)).exists():
        time.sleep(0.02)
        continue
    seen += 1
    try:
        g1, g2 = p.r32(0x003485EC), p.r32(0x000F7F20)
        lst = p.r32(0x00347EA0 + 4)
        a = p.r32(lst + 12)
        n = 0
        lines.append("f%d pmode %d list %08X G1 %08X G2 %08X" % (f, p.r32(0x000F7F14), lst, g1, g2))
        while 0x00100000 <= a < 0x02000000 and n < 400:
            b = p.read(a, 0x14)
            cls, l1, nxt, flags, grp = struct.unpack("<5I", b)
            where = ("G1+%04X" % (a - g1)) if g1 <= a < g1 + 0x4000 else ("G2+%04X" % (a - g2)) if g2 <= a < g2 + 0x4000 else ""
            ab = p.read(a + 0x170, 8)
            ax, ay = struct.unpack("<ii", ab)
            lines.append("f%d #%d %08X class %08X flags %08X group %X abs (%d %d) %s" % (f, n, a, cls, flags, grp, ax, ay, where))
            a = nxt
            n += 1
    except Exception as e:  # noqa: BLE001
        lines.append("f%d read failed: %r" % (f, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
