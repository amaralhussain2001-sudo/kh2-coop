"""Read-only probe for tools/own/make_rec_rc.py (a hero's Reaction Command calls back its source). At each snapshot frame:
the two heroes' calls since the kit's first counter, then (at the last frame) the noted entries.
  python -I tools/own/rc_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def name(x, h1, h2):
    return "P1" if x == h1 and x else "P2" if x == h2 and x else "%08X" % x


for k, fr in enumerate(frames):
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        lines.append("f%d counter %d | calls P1 %d P2 %d | entries %d | pair %s %s captor %08X" % (
            fr, p.r32(0x0034D4BC), p.r32(0x000F1D08), p.r32(0x000F1D0C), p.r32(0x000F1D00),
            name(p.r32(0x000E7EA0), h1, h2), name(p.r32(0x000E7EA4), h1, h2), p.r32(0x000E7EA8)))
        if k == len(frames) - 1:
            n = min(p.r32(0x000F1D00), 16)
            raw = p.read(0x000F1D10, 32 * n)
            for i in range(n):
                c, src, hero, named, other, captor, last, num = struct.unpack_from("<8I", raw, 32 * i)
                lines.append("rc %d counter %d source %08X (object %04X) hero %s | pair %s %s captor %08X%s | last sent %d" % (
                    i, c, src, num & 0xFFFF, name(hero, h1, h2), name(named, h1, h2), name(other, h1, h2), captor,
                    " = the source" if captor == src else "", last))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
