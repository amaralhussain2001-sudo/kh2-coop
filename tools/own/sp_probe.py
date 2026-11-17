"""Read-only probe for the special-mode tests (seventh round, part 7): at each snapshot frame the room, the battle
word, the view layout, and for both heroes (the engine's player 0x0034E948, the twin 0x000F05CC): the object's
address, the place (x, y, z), HP and the action word. Also the mission object and the Game Over word.
  python -I tools/own/sp_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=120)
t0, lines = time.time(), []


def ok(a):
    return 0x00100000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return "none"
    x, y, z = struct.unpack("<3f", p.read(o + 0x70, 12))
    s = p.r32(o + 0x48C)
    hp = "%d/%d" % (p.r32(s), p.r32(s + 4)) if ok(s) else "noslot"
    return "%08X (%.0f, %.0f, %.0f) hp %s a%02X" % (o, x, y, z, hp, p.r32(o + 0x154) & 0xFFFF)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 600:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        lines.append("f%d room %04X btl %d L%d | P1 %s | P2 %s | msn %d go %d" % (
            fr, p.r32(0x0032BAE0) & 0xFFFF, p.r32(0x01C61958) & 0xFF, p.r8(0x000F6F00), hero(p.r32(0x0034E948)),
            hero(p.r32(0x000F05CC)), 1 if p.r32(0x01D49320) else 0, 1 if p.r32(0x00350DF0) else 0))
    except Exception as e:  # noqa: BLE001
        lines.append("f%d readfail %s" % (fr, e))
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
