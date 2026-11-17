"""Read-only probe: who is who. At each snapshot frame: the engine's player, the twin, their unit slots (mark, HP,
Drive bytes, share count), controllers, control objects, the party table, camera target, trigger owner, layout.

  python -I tools/own/who_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import pathlib
import struct
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


def obj(name, o):
    if not o:
        return "  %s: none" % name
    slot = p.r32(o + 0x48C)
    s = "  %s %08X class %08X pad %08X ctl %08X pos %s" % (
        name, o, p.r32(o), p.r32(o + 0xB38), p.r32(o + 0xB3C),
        " ".join("%.0f" % v for v in struct.unpack("<3f", p.read(o + 0x10, 12))))
    if slot:
        d = p.read(slot + 0x1B0, 12)
        s += " | slot %08X mark %d id %d share %d HP %d/%d drive %s back %08X" % (
            slot, p.r32(slot + 0x250) >> 31, p.r32(slot + 0x254), p.r32(slot + 0x258), p.r32(slot), p.r32(slot + 4),
            " ".join("%02X" % b for b in d), p.r32(slot + 0x25C))
    return s


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        lines.append("frame %d room %04X layout %d | last %08X cam %08X trig %08X party %s | save form %02X drive %s" % (
            fr, struct.unpack("<H", p.read(0x0032BAE0, 2))[0], p.read(0x000F6F00, 1)[0], p.r32(0x00352400),
            p.r32(0x00348754), p.r32(0x0034ED04), " ".join("%08X" % x for x in struct.unpack("<3I", p.read(0x00348638, 12))),
            p.read(0x0032F054, 1)[0], " ".join("%02X" % b for b in p.read(0x0032F058, 4))))
        lines.append(obj("player", pl))
        lines.append(obj("twin  ", tw))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
