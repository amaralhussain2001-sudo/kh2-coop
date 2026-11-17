"""Read-only probe (tenth round, a one-hero jump disc for the jump kits): at each snapshot frame, scan 0x01000000 .. 0x01FFFFFF
for the New Game jump record of a lane S1 jump disc (16-bit words: 1, 0, type, world, area, entrance, program, fade 0x4002; see
tools/own/make_jumpkit1.py, where test-s1-tt137's record sits at 0x01C56310) and print every address that matches
JUMPREC = "type,world,area,entrance,program" (decimal; default "2,2,0,0,137" = test-s1-tt137).
  python -I tools/own/jumprec_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
t, w, a, e, pr = (int(v) for v in os.environ.get("JUMPREC", "2,2,0,0,137").split(","))
pat = struct.pack("<8H", 1, 0, t, w, a, e, pr, 0x4002)
p = Pine(port, wait=120)
t0, lines = time.time(), []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        mem = p.read(0x01000000, 0x01000000)
        hits, i = [], mem.find(pat)
        while i >= 0 and len(hits) < 8:
            hits.append("%08X" % (0x01000000 + i))
            i = mem.find(pat, i + 2)
        lines.append("f%d jump record %s: %s" % (fr, pat.hex(), " ".join(hits) or "none"))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
