"""Read-only probe: poll a few words all through a run and write a line whenever one changes.
Addresses come from the environment variable WATCH (hex, comma separated; default: camera hold, story event
flag, view layout). Same arguments as the other probes.

  python -I tools/own/watch_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 900.0
addrs = [int(x, 16) for x in os.environ.get("WATCH", "0033CC38,0035037C,000F6F00").split(",")]
p = Pine(port, wait=120)
t0 = time.time()
lines = []
last = None
seen = 0
final = test_dir / ("p1_f%06d.png" % frames[-1])
while not final.exists() and time.time() - t0 < timeout:
    try:
        vals = tuple(p.r32(a) for a in addrs)
    except Exception:  # noqa: BLE001
        time.sleep(0.05)
        continue
    while seen < len(frames) and (test_dir / ("p1_f%06d.png" % frames[seen])).exists():
        lines.append("-- snapshot %d" % frames[seen])
        seen += 1
    if vals != last:
        lines.append("%7.2fs " % (time.time() - t0) + " ".join("%08X=%08X" % (a, v) for a, v in zip(addrs, vals)))
        last = vals
    time.sleep(0.01)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
