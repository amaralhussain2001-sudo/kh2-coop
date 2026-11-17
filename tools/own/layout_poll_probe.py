"""Read-only probe: polls the view layout byte (0x000F6F00), the twin pointer, the camera hold word and the Game
Over word all through a run and writes a line with the SESSION FRAME (game counter 0x0034D4BC + 152) whenever
one of them changes.
  python -I tools/own/layout_poll_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
p = Pine(int(sys.argv[2]), wait=120)
lines, last, t0 = [], None, time.time()
try:
    while time.time() - t0 < 900:
        try:
            fr = p.r32(0x0034D4BC) + 152
            key = (p.r8(0x000F6F00), 1 if p.r32(0x000F05CC) else 0, 1 if p.r32(0x0034E948) else 0, 1 if p.r32(0x00350DF0) else 0)
        except RuntimeError:
            time.sleep(0.2)
            continue
        if key != last:
            lines.append("f%d layout %d twin %d hero %d gameover %d" % ((fr,) + key))
            last = key
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
