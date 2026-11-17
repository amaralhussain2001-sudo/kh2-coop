"""Read-only probe: the long runs of ZERO bytes inside a memory range, at every snapshot frame (for finding a place
in the save data for new values: plan row 39). A run is listed when it is at least MINLEN bytes long.
  RANGES=0032BB30:10FC0 MINLEN=100 python -I tools/own/zrun_probe.py <testDir> <pinePort> <frame,...> <out.txt>
Line: f<frame> <start>-<end> (+<offset from the range start>, <length> bytes).  At the end: the runs that were zero
at EVERY frame of this run (the common part)."""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
ranges = [tuple(int(v, 16) for v in r.split(":")) for r in os.environ.get("RANGES", "0032BB30:10FC0").split(",")]
minlen = int(os.environ.get("MINLEN", "100"), 16)
p = Pine(port, wait=120)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "600"))
common = {}


def zero_runs(data):
    runs, i, n = [], 0, len(data)
    while i < n:
        if data[i] == 0:
            j = i
            while j < n and data[j] == 0:
                j += 1
            if j - i >= minlen:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    for a, n in ranges:
        try:
            data = p.read(a, n)
        except Exception as e:  # noqa: BLE001
            lines.append("f%d %08X read failed" % (fr, a))
            continue
        z = bytearray(1 if b == 0 else 0 for b in data)
        if a in common:
            common[a] = bytearray(x & y for x, y in zip(common[a], z))
        else:
            common[a] = z
        runs = zero_runs(data)
        lines.append("f%d %08X: %d zero runs of %d bytes or more, %d bytes in all" % (fr, a, len(runs), minlen, sum(j - i for i, j in runs)))
for a, z in common.items():
    inv = bytes(0 if x else 1 for x in z)
    for i, j in zero_runs(inv):
        lines.append("ALWAYS ZERO %08X-%08X (+%05X, %d bytes)" % (a + i, a + j - 1, i, j - i))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
