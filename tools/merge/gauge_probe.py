"""Read-only probe: dump the HUD gauge objects and the two heroes' unit slots when given screenshots appear.

  python -I tools/merge/gauge_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]

For each frame it waits for <testDir>/p1_f<frame>.png, then writes: HUD party table, gauge root pointers,
the player gauge (flags, state, kind), the twin gauge of lane V2, both heroes and their unit slots.
Only reads memory (allowed with linked copies).
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

test_dir, port, frames, out = pathlib.Path(sys.argv[1]), int(sys.argv[2]), [int(x) for x in sys.argv[3].split(",")], sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []


def hexrow(base, data, width=16):
    rows = []
    for i in range(0, len(data), width):
        rows.append("    %08X  %s" % (base + i, " ".join("%02X" % b for b in data[i:i + width])))
    return rows


def obj2d(name, a):
    """A 2D layer object: class, flags, group, and the words the gauges use."""
    if not (0x00100000 <= a < 0x02000000):
        return ["  %s: none (%08X)" % (name, a)]
    w = struct.unpack("<16I", p.read(a, 64))
    return ["  %s at %08X: class %08X flags %08X group %X | +18 %08X +2C %08X +30 %08X +34 (character) %08X"
            % (name, a, w[0], w[3], w[4], w[6], w[11], w[12], w[13])]


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        lines.append("=== frame %d, room %04X" % (fr, p.r16(0x0032BAE0)))
        party = struct.unpack("<6I", p.read(0x00348638, 24))
        lines.append("  HUD party table: " + " ".join("%08X" % x for x in party))
        roots = struct.unpack("<8I", p.read(0x003485E0, 32))
        lines.append("  gauge root pointers 0x003485E0..: " + " ".join("%08X" % x for x in roots))
        twin = p.r32(0x000F05CC)
        hero = party[0]
        engine = p.r32(0x0034E948)
        lines.append("  hero (party slot 0) %08X, engine's player %08X, twin %08X" % (hero, engine, twin))
        for name, o in (("hero", hero), ("twin", twin)):
            if not (0x00100000 <= o < 0x02000000):
                continue
            slot = p.r32(o + 0x48C)
            lines.append("  %s slot %08X: HP %d/%d MP %d/%d" % (name, slot, p.r32(slot), p.r32(slot + 4), p.r32(slot + 0x180), p.r32(slot + 0x184)))
            lines += hexrow(slot + 0x180, p.read(slot + 0x180, 0x80))
            lines.append("    %s slot +0x240..: " % name + " ".join("%08X" % x for x in struct.unpack("<10I", p.read(slot + 0x240, 40))))
            lines.append("    %s object +0x7F0..: " % name + " ".join("%08X" % x for x in struct.unpack("<4I", p.read(o + 0x7F0, 16))))
        # the gauges: every 2D object of the field HUD layer (manager 0), with group and flags
        mgr = 0x00347EA0
        o = p.r32(mgr + 4)
        n = 0
        while 0x00100000 <= o < 0x02000000 and n < 80:
            w = struct.unpack("<16I", p.read(o, 64))
            extra = ""
            if w[0] == 0x0034A920:          # player gauge class
                extra = " PLAYER GAUGE kind(+3CF0) %X" % p.r32(o + 0x3CF0)
            lines.append("  2D object %08X class %08X flags %08X group %2X +18 %08X char %08X%s" % (o, w[0], w[3], w[4], w[6], w[13], extra))
            o = w[1]
            n += 1
        lines += obj2d("twin gauge (lane V2)", p.r32(0x000F7F00))
    except Exception as ex:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
