"""Read-only probe for the "command menu rows per player" glue: at each snapshot frame, print the command menu
display's list state, player 2's copy of it, both control objects' Reaction Command fields and the row pool.

  python -I tools/own/rows_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
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


def words(addr, n):
    return struct.unpack("<%dI" % n, p.read(addr, 4 * n))


def state(name, w):          # w = 59 words = display+0x18..+0x103
    rows = w[:36]
    lines.append("  %s rows: %s" % (name, " | ".join(" ".join("%08X" % x if x else "-" for x in rows[i:i + 9]) for i in range(0, 36, 9))))
    lines.append("  %s +CC %s  +DC %s  +EC %08X +F0 %08X +F4 %08X +F8 %08X +FC %08X +100 %08X"
                 % (name, " ".join("%X" % x for x in w[45:49]), " ".join("%X" % x for x in w[49:53]), w[53], w[54], w[55], w[56], w[57], w[58]))
    return [x for x in rows if x]


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        disp = p.r32(0x003484A0)
        lines.append("=== frame %d: display %08X  V_CSD %08X V_CSW %08X" % (fr, disp, p.r32(0x000F4400), p.r32(0x000F4404)))
        if disp:
            ctl = p.r32(disp + 0x29C)
            lines.append("  display control %08X  shown %02X  flags %08X" % (ctl, p.read(disp + 0x2A8, 1)[0], p.r32(disp + 12)))
            live = state("P1", words(disp + 0x18, 59))
            live2 = state("P2", words(0x000F4410, 59))
            for who, rws in (("P1", live), ("P2", live2)):
                for r in rws:
                    lines.append("    %s row %08X class %08X flags %08X group %X text %08X" % (who, r, p.r32(r), p.r32(r + 12), p.r32(r + 16), p.r32(r + 0x198)))
        for nm, c in (("S ", 0x01C5F530), ("S2", 0x000F1000)):
            w = words(c + 0xA1C, 3)
            lines.append("  %s class %08X +20 %08X  +A1C %08X %08X %08X  open %08X top %08X" % (nm, p.r32(c), p.r32(c + 0x20), w[0], w[1], w[2], p.r32(c + 0x9E8), p.r32(c + 0x8C0)))
        pool = p.r32(0x00348058)
        pool2 = p.r32(0x000F4500)
        if pool2:
            lines.append("  player 2 pool %08X rows left %d" % (pool2, p.r32(pool2 + 0x6ED0)))
        if pool:
            lines.append("  pool %08X rows left %d" % (pool, p.r32(pool + 0x6ED0)))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
