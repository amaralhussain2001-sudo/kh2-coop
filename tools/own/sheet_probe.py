"""Read-only probe: the command menu's picture sheet. At each snapshot frame: the display, both layout holders
(the game's 0x00348050 and player 2's 0x000F4508) and the first words of each holder's image object (holder+0x20:
+4 texture place, +8.. sizes, +32 colour table place, +48 flags, +56 / +60 data pointers, +400 byte), the frame
object's words (display+0x104) and the look words.
  python -I tools/own/sheet_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
t0 = time.time()
lines = []


def img(h):
    if not h:
        return "none"
    w = struct.unpack("<16I", p.read(h + 0x20, 64))
    return "%08X cls %08X fl %08X grp %d | img tbp %X w %d %d %d h? %d %d %d cbp %X (%d %d %d %d) flags %08X %08X pix %08X clut %08X b400 %d" % (
        h, p.r32(h), p.r32(h + 12), p.r32(h + 16), w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11], w[12], w[12], w[13], w[14], w[15],
        p.read(h + 0x20 + 400, 1)[0])


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < 900:
        time.sleep(0.05)
    try:
        d = p.r32(0x003484A0)
        lines.append("frame %d display %08X default sheet %08X default look %08X" % (fr, d, p.r32(0x00347FE0), p.r32(0x00347FE4)))
        lines.append("   holder1 " + img(p.r32(0x00348050)))
        lines.append("   holder2 " + img(p.r32(0x000F4508)))
        if d:
            f = struct.unpack("<8I", p.read(d + 0x104, 32))
            lines.append("   frame: %s | seq %d next %d b404 %d | look %08X %08X | b2A8 %s | f %.2f %.2f %.2f | FD %d" % (
                " ".join("%08X" % x for x in f), p.r32(d + 0x104 + 388), p.r32(d + 0x28C) & 0xFFFFFFFF, p.read(d + 0x298, 1)[0],
                p.r32(d + 0x2A0), p.r32(d + 0x2A4), p.read(d + 0x2A8, 2).hex(),
                *struct.unpack("<3f", p.read(d + 0x2AC, 12)), p.read(d + 0xFD, 1)[0]))
            sq = struct.unpack("<96I", p.read(d + 0x11C, 384))
            lines.append("   seq player: " + " ".join("%X" % x for x in sq))
        for lo, hi in ((0x000F3900, 0x000F3FF0), (0x000F7C00, 0x000F7F00), (0x000F1B00, 0x000F2000), (0x000F5B80, 0x000F5C00)):
            blob = p.read(lo, hi - lo)
            nz = [lo + i for i in range(0, hi - lo, 4) if blob[i:i + 4] != b"\0\0\0\0"]
            lines.append("   cave %08X-%08X: %d words not zero%s" % (lo, hi, len(nz), (" (first %08X, last %08X)" % (nz[0], nz[-1])) if nz else ""))
        for nm, c in (("S ", 0x01C5F530), ("S2", 0x000F1000)):
            menu = p.r32(c + 0x9E8)
            lines.append("   %s open menu id %d" % (nm, p.r32(menu) if menu else -1))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
