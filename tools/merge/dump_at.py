"""Read-only probe: dump a memory range (hex) each time a given screenshot appears.

  python -I tools/merge/dump_at.py <testDir> <pinePort> <frame,frame,...> <startHex> <length> <out.txt> [--timeout 600]
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
start, length, out = int(sys.argv[4], 16), int(sys.argv[5], 0), sys.argv[6]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        data = p.read(start, length)
        lines.append("=== frame %d" % fr)
        for i in range(0, length, 16):
            lines.append("%08X  %s" % (start + i, " ".join("%02X" % b for b in data[i:i + 16])))
    except Exception as ex:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("dumped", len(frames), "frames to", out)
