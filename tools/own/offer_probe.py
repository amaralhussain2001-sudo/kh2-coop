"""Read-only probe for tools/own/make_rec_offer2.py. At each snapshot frame: offers since the first counter; at the last frame
the noted offers, each control object named by the hero whose + 0xB44 holds it.
  python -I tools/own/offer_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))
for k, fr in enumerate(frames):
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        c1 = p.r32(h1 + 0xB44) if h1 else 0
        c2 = p.r32(h2 + 0xB44) if h2 else 0
        lines.append("f%d counter %d | offers %d | control objects P1 %08X P2 %08X | engine's player %s" % (
            fr, p.r32(0x0034D4BC), p.r32(0x000F1D08), c1, c2,
            "P1" if p.r32(0x0034E948) == h1 else "P2" if p.r32(0x0034E948) == h2 else "%08X" % p.r32(0x0034E948)))
        if k == len(frames) - 1:
            n = min(p.r32(0x000F1D00), 16)
            raw = p.read(0x000F1D10, 16 * n)
            for i in range(n):
                ctl, ra, pl, c = struct.unpack_from("<4I", raw, 16 * i)
                lines.append("offer %d counter %d to %s ra %08X engine's player %s" % (
                    i, c, "P1's menu" if ctl == c1 else "P2's menu" if ctl == c2 else "%08X" % ctl, ra,
                    "P1" if pl == h1 else "P2" if pl == h2 else "%08X" % pl))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
