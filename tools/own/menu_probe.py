"""Read-only probe: the two control objects' open menu (its id and cursor), the heroes' board-mode word, and the
display's look words, at each snapshot frame.
  python -I tools/own/menu_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=120)
t0 = time.time()
lines = []
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 600:
        time.sleep(0.05)
    try:
        disp = p.r32(0x003484A0)
        s = "frame %d display %08X" % (fr, disp)
        if disp:
            s += " ctl %08X look %08X %08X holder %08X holder2 %08X" % (p.r32(disp + 0x29C), p.r32(disp + 0x2A0), p.r32(disp + 0x2A4), p.r32(0x00348050), p.r32(0x000F4508))
        lines.append(s)
        for nm, c, hero in (("S ", 0x01C5F530, p.r32(0x0034E948)), ("S2", 0x000F1000, p.r32(0x000F05CC))):
            menu = p.r32(c + 0x9E8)
            lines.append("  %s player %08X attached %08X open menu %08X id %d | hero %08X board mode %d action %08X" % (
                nm, p.r32(c + 0x9E0), p.r32(c + 0xAF4), menu, p.r32(menu) if menu else -1, hero,
                p.r32(hero + 0xB70) if hero else -1, p.r32(hero + 0xB6C) if hero else 0)
                + (" B3C %08X B40 %08X B44 %08X" % (p.r32(hero + 0xB3C), p.r32(hero + 0xB40), p.r32(hero + 0xB44)) if hero else ""))
        import struct as _s
        ring = _s.unpack("<18I", p.read(0x000F5F00, 72))
        lines.append("  board-menu recorder: index %d | %s" % (ring[0], " ".join("%08X<-%08X" % (ring[2 + 2 * i], ring[3 + 2 * i]) for i in range(8) if ring[2 + 2 * i])))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
