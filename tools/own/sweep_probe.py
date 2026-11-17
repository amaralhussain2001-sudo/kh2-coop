"""Read-only probe for the mission sweep (tools/own/sweep.sh): one line per snapshot frame with the room, the
battle word, the view layout, the twin, both heroes' HP and action, the mission object and the Game Over word.
  python -I tools/own/sweep_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "200"))   # seconds from the start (long runs: more)


def hero(o):
    if not 0x00100000 <= o < 0x02000000:
        return "none"
    s = p.r32(o + 0x48C)
    if not 0x00100000 <= s < 0x02000000:
        return "noslot"
    return "%d/%d a%02X" % (p.r32(s), p.r32(s + 4), p.r32(o + 0x154) & 0xFFFF)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        lines.append("f%d room %04X btl %d L%d P1 %s P2 %s msn %d go %d" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r8(0x000F6F00), hero(p.r32(0x0034E948)),
            hero(p.r32(0x000F05CC)), 1 if p.r32(0x01D49320) else 0, 1 if p.r32(0x00350DF0) else 0))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail" % fr)
pathlib.Path(out).write_text(" ; ".join(lines) + "\n", encoding="utf-8")
