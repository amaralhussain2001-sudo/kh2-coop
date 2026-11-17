"""Read-only probe: do the heroes move while an event holds the camera? Polls the camera-hold word, the story
event word and both heroes' positions all through a run; for every hold period one line: how long, and how far
each hero's position moved inside it (path length of the polled positions).

  python -I tools/own/hold_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 900]
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
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 900.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []
final = test_dir / ("p1_f%06d.png" % frames[-1])
cur = None          # [start, last pos p1, last pos p2, path p1, path p2, polls]


def pos(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12)) if o else None


def step(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))) if a and b else 0.0


while not final.exists() and time.time() - t0 < timeout:
    try:
        hold, ev = p.r32(0x0033CC38), p.r32(0x0035037C)
        a, b = pos(p.r32(0x0034E948)), pos(p.r32(0x000F05CC))
    except Exception:  # noqa: BLE001
        time.sleep(0.05)
        continue
    now = time.time() - t0
    if hold:
        if cur is None:
            cur = [now, a, b, 0.0, 0.0, 0, ev]
        cur[3] += step(cur[1], a)
        cur[4] += step(cur[2], b)
        cur[1], cur[2] = a, b
        cur[5] += 1
    elif cur is not None:
        lines.append("hold from %7.2fs for %5.2fs (event %s, %d polls): player 1's hero moved %.0f, the twin moved %.0f" % (
            cur[0], now - cur[0], "yes" if cur[6] else "no", cur[5], cur[3], cur[4]))
        cur = None
    time.sleep(0.005)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
