"""Read-only probe: a timeline of both heroes' action words and places, polled as fast as PINE answers (no waiting
for pictures). A line is written whenever a hero's action word changes, with the frame, both actions, both
places and both HP values. For "whose button did that": compare the frames with the button scripts.
  python -I tools/own/act_poll_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>
FROM=<frame> (default 4600), TO=<frame> (default 8950)."""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
start, end = int(os.environ.get("FROM", "4600")), int(os.environ.get("TO", "8950"))
p = Pine(int(sys.argv[2]), wait=120)
lines, last, t0 = [], None, time.time()


def ok(a):
    return 0x00100000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return (None, "none")
    d = p.read(o + 0x70, 12)
    x, y, z = struct.unpack("<3f", d)
    act = p.r32(o + 0x154) & 0xFFFF
    s = p.r32(o + 0x48C)
    hp = p.r32(s) if ok(s) else -1
    return (act, "a%02X (%.0f, %.0f, %.0f) hp %d" % (act, x, y, z, hp))


try:
    while time.time() - t0 < 600:
        try:
            fr = p.r32(0x0034D4BC) + 152
        except RuntimeError:
            time.sleep(0.3)
            continue
        if fr < start:
            time.sleep(0.1)
            continue
        if fr > end:
            break
        a1, s1 = hero(p.r32(0x0034E948))
        a2, s2 = hero(p.r32(0x000F05CC))
        if (a1, a2) != last:
            lines.append("f%d P1 %s | P2 %s" % (fr, s1, s2))
            last = (a1, a2)
            if len(lines) % 50 == 0:
                pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
