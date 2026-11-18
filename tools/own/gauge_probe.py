"""Read-only probe (partner's Drive display, part 150): at every snapshot frame dump both big gauge objects' parts.
  python -I tools/own/gauge_probe.py <testDir> <pinePort> <frame,...> <out.txt>
Gauges: player 1's [0x003485EC], player 2's [0x000F7F20]. Parts: +0x0394 and +0x1A30 + k*0x19C (k = 0..17). Per part: flags +12,
absolute position +0x170/+0x174, relative +0x178/+0x17C, parent +0x18C (shown as an offset when inside the same object), +0x190,
and the words +0x00..+0x2C (class, sequence, ...). Also the object's own +0x00..+0x40 and O_PMODE 0x000F7F14.
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
OFFS = [0x0394] + [0x1A30 + k * 0x19C for k in range(18)] + [0x33B0]
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
        lines.append("f%d pmode %d" % (f, p.r32(0x000F7F14)))
        for name, ptr in (("G1", 0x003485EC), ("G2", 0x000F7F20)):
            g = p.r32(ptr)
            if not 0x00100000 <= g < 0x02000000:
                lines.append("f%d %s -> %08X (none)" % (f, name, g))
                continue
            head = p.read(g, 0x40)
            lines.append("f%d %s %08X head %s" % (f, name, g, " ".join("%08X" % w for w in struct.unpack("<16I", head))))
            for o in OFFS:
                b = p.read(g + o, 0x19C)
                w = struct.unpack_from("<12I", b, 0)
                ax, ay, rx, ry = struct.unpack_from("<iiii", b, 0x170)
                par, x190 = struct.unpack_from("<II", b, 0x18C)
                pr = ("+%04X" % (par - g)) if g <= par < g + 0x4000 else "%08X" % par
                lines.append("f%d %s +%04X flags %08X abs (%d %d) rel (%d %d) parent %s 190 %08X | %s" % (
                    f, name, o, w[3], ax, ay, rx, ry, pr, x190, " ".join("%08X" % x for x in w)))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d read failed: %r" % (f, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
