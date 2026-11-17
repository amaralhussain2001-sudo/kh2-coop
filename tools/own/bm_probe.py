"""Read-only probe: at each snapshot frame the camera hold, the event's hero (player 1 / twin / none) and the
view layout byte (one line per frame).
  python -I tools/own/bm_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]"""
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
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.02)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        hold, ev = p.r32(0x0033CC38), p.r32(0x0035037C)
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        subj = p.r32(ev + 0x44) if ev else 0
        who = "P1:%04X TW:%04X owner %08X" % (p.r32(pl + 0x160) & 0xFFFF, p.r32(tw + 0x160) & 0xFFFF, p.r32(ev + 8) if ev else 0)
        lines.append("frame %d hold %d event %s hero %s layout %d" % (fr, hold, "yes" if ev else "no", who, p.r32(0x000F6F00) & 0xFF))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
