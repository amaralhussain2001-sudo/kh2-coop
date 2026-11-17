"""Read-only probe: is a memory range unused? At every snapshot frame the ranges are read and every run of bytes that
is not zero is listed (start, length, first bytes), and whether the range changed since the last frame.
  RANGES=00080000:70000 python -I tools/own/zero_probe.py <testDir> <pinePort> <frame,...> <out.txt>
(For finding room for new patch routines: memory below the game program, 0x00080000-0x000EFFFF.)"""
import hashlib
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
ranges = [tuple(int(v, 16) for v in r.split(":")) for r in os.environ.get("RANGES", "00080000:70000").split(",")]
p = Pine(port, wait=120)
t0, lines, last = time.time(), [], {}
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "600"))
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
        h = hashlib.sha1(data).hexdigest()[:10]
        runs, i = [], 0
        while i < n:
            if data[i]:
                j = i
                gap = 0
                while j < n and gap < 64:           # a run ends after 64 zero bytes
                    gap = gap + 1 if not data[j] else 0
                    j += 1
                end = j - gap
                runs.append((a + i, end - i, data[i:i + 8].hex()))
                i = j
            else:
                i += 1
        nz = sum(1 for b in data if b)
        lines.append("f%d %08X-%08X: %d bytes not zero in %d runs, sum %s%s" % (
            fr, a, a + n - 1, nz, len(runs), h, "" if last.get(a) in (None, h) else " CHANGED"))
        last[a] = h
        for s, ln, hx in runs[:40]:
            lines.append("    %08X +%X  %s" % (s, ln, hx))
        if len(runs) > 40:
            lines.append("    ... %d more runs, the last at %08X" % (len(runs) - 40, runs[-1][0]))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
