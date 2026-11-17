"""Lane R: is the engine's player pointer ever LEFT on the twin, or only seen there for an instant?

Reads (engine player 0x0034E948, lane E's twin pointer, the second-offer flag, player 1's hero kept during the
second offer) as fast as PINE allows for some seconds and counts the combinations. Read-only.

  python -I tools/lane-r/gsample.py <test-out-dir> <pinePort> <startFrame> <seconds>
Waits for the screenshot of <startFrame> first (it must be in the run's --snap list).
"""
import collections
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out, port, start, secs = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
shot = out / ("p1_f%06d.png" % start)
t0 = time.time()
while not shot.exists():
    if time.time() - t0 > 600:
        sys.exit("timeout waiting for " + shot.name)
    time.sleep(0.05)
p = Pine(port)
G, TWIN, PASS2, P1 = 0x0034E948, 0x000F05CC, 0x000F05D0, 0x000F05D4
cnt = collections.Counter()
runs, longest, cur = 0, 0, 0
t0 = time.time()
n = 0
while time.time() - t0 < secs:
    try:
        g, tw, ps = p.r32(G), p.r32(TWIN), p.r32(PASS2)
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
        continue
    n += 1
    if tw and g == tw:
        key = "engine player = TWIN, second-offer flag %d" % ps
        cur += 1
        longest = max(longest, cur)
    else:
        key = "engine player = hero (or none), second-offer flag %d" % ps
        cur = 0
    cnt[key] += 1
lines = ["samples: %d in %.1f s" % (n, secs)]
for k, v in sorted(cnt.items()):
    lines.append("  %-52s %7d  (%.2f %%)" % (k, v, 100.0 * v / max(n, 1)))
lines.append("longest run of consecutive samples with the twin as engine player: %d" % longest)
(out / "gsample.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
