"""Read-only probe: the Drive bytes of both heroes' unit slots, the save data's copy, the second hero's own copy and
the glue's variables, at each snapshot frame (one line per frame).

  python -I tools/own/drv_probe2.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import pathlib
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


def hx(a, n):
    return " ".join("%02X" % b for b in p.read(a, n))


def slot(o):
    if not o:
        return "none"
    s = p.r32(o + 0x48C)
    if not s:
        return "%08X no slot" % o
    return "%08X slot %08X m%d sh%d form %02X drv %s" % (o, s, p.r32(s + 0x250) >> 31, p.r32(s + 0x258), p.read(s + 0x1AF, 1)[0], hx(s + 0x1B0, 12))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.02)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        lines.append("f%d L%d | P1 %s | TW %s | save form %02X drv %s | own %s valid %d last %s | ft %d %d" % (
            fr, p.read(0x000F6F00, 1)[0], slot(p.r32(0x0034E948)), slot(p.r32(0x000F05CC)), p.read(0x0032F054, 1)[0],
            hx(0x0032F058, 12), hx(0x000F47D0, 12), p.r32(0x000F47C0), hx(0x000F47C4, 12), p.r32(0x000F47E0), p.r32(0x000F47E4)) + " tform %d tfv %d" % (p.read(0x000F47E8, 1)[0], p.r32(0x000F47EC)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
