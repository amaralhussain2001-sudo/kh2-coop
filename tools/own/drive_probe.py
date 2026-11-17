"""Read-only probe: the Drive values of both heroes' unit slots and of the save data, at given snapshot frames.

  python -I tools/own/drive_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]

Per frame: for player 1's hero (HUD party table 0x00348638) and the twin (0x000F05CC): object, unit slot,
slot+0x1B0 gauge, +0x1B1 bars, +0x1B2 max bars, +0x1B3, +0x1B4 / +0x1B8 (two floats), HP, MP;
the save data's Drive bytes (0x0032F058..0x0032F063); the own-Drive glue's variables if present.
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


def drive(addr):
    b = p.read(addr, 12)
    f1, f2 = struct.unpack_from("<ff", b, 4)
    return "gauge %3d bars %d max %d (+3: %d) timers %.2f %.2f" % (b[0], b[1], b[2], b[3], f1, f2)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        lines.append("=== frame %d  room %04X" % (fr, p.r32(0x0032BAE0) & 0xFFFF))
        for name, ptr in (("hero", 0x00348638), ("twin", 0x000F05CC)):
            obj = p.r32(ptr)
            if not obj:
                lines.append("  %s: no object" % name)
                continue
            slot = p.r32(obj + 0x48C)
            if not slot:
                lines.append("  %s: object %08X, no slot" % (name, obj))
                continue
            lines.append("  %s: object %08X slot %08X flags %08X  HP %d/%d MP %d/%d  %s" % (
                name, obj, slot, p.r32(slot + 0x250), p.r32(slot), p.r32(slot + 4), p.r32(slot + 0x180), p.r32(slot + 0x184),
                drive(slot + 0x1B0)))
        lines.append("  save data: %s   munny %d" % (drive(0x0032F058), p.r32(0x0032DF70)))
        lines.append("  glue: valid %08X  shadow: %s  own: %s" % (p.r32(0x000F47C0), drive(0x000F47C4), drive(0x000F47D0)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
