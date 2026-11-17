"""Read-only probe for the hurt recorder kit (tools/own/make_hurtkit.py): sweep_probe.py's line for each snapshot
frame, and at the end the two tables "in which action was this hero hurt, how many steps".
  python -I tools/own/hurt_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
Last lines:  HURT P1 total N: aXX xCount (first at session frame F, HP seen H) ...   and the same for P2."""
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
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "200"))


def hero(o):
    if not 0x00100000 <= o < 0x02000000:
        return "none"
    s = p.r32(o + 0x48C)
    if not 0x00100000 <= s < 0x02000000:
        return "noslot"
    return "%d/%d a%02X" % (p.r32(s), p.r32(s + 4), p.r32(o + 0x154) & 0xFFFF)


def tables():
    res = []
    tot = struct.unpack("<2I", p.read(0x000F1E00, 8))
    for who in (0, 1):
        ent = struct.unpack("<60I", p.read(0x000F1E10 + who * 0xF0, 240))
        parts = ["a%02X x%d (first f%d, HP %d)" % (ent[i], ent[i + 1], ent[i + 2] + 152, ent[i + 3])
                 for i in range(0, 60, 4) if ent[i + 1]]
        res.append("HURT P%d total %d: %s" % (who + 1, tot[who], ", ".join(parts) or "-"))
    return res


last = []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        tot = struct.unpack("<2I", p.read(0x000F1E00, 8))
        lines.append("f%d room %04X btl %d L%d P1 %s P2 %s msn %d go %d | hurt steps %d / %d" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r8(0x000F6F00), hero(p.r32(0x0034E948)),
            hero(p.r32(0x000F05CC)), 1 if p.r32(0x01D49320) else 0, 1 if p.r32(0x00350DF0) else 0, tot[0], tot[1]))
        last = tables()
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail" % fr)
pathlib.Path(out).write_text("\n".join(lines + last) + "\n", encoding="utf-8")
