"""Read-only probe: where does memory keep positions that player 1's hero (and the twin) walked through?
Polls both heroes' positions all through the run. At each snapshot frame the program's data, the cave and the
object heap are read and searched for (x, ?, z) float triples that equal a position one of the heroes had at
least half a second before (and that is at least 30 units from where he is now). One line per hit.

  python -I tools/own/trail_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]
"""
import array
import pathlib
import struct
import sys
import threading
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
RANGES = ((0x000F0000, 0x000F8000), (0x00300000, 0x00A00000), (0x01A00000, 0x01D80000))
hist = {"player": [], "twin": []}       # (time, x, y, z)


def pos(o):
    return struct.unpack("<3f", p.read(o + 0x70, 12)) if o else None


def poll():
    for name, cell in (("player", 0x0034E948), ("twin", 0x000F05CC)):
        q = pos(p.r32(cell))
        if q and (not hist[name] or max(abs(a - b) for a, b in zip(q, hist[name][-1][1:])) > 2.0):
            hist[name].append((time.time() - t0,) + q)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        try:
            poll()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.01)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        now = time.time() - t0
        pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
        party = struct.unpack("<3I", p.read(0x00348638, 12))
        cur = {"player": pos(pl), "twin": pos(tw)}
        lines.append("frame %d | player %08X at %s (%d past spots) | twin %08X at %s (%d past spots) | helpers %08X %08X" % (
            fr, pl, " ".join("%.0f" % v for v in cur["player"]), len(hist["player"]),
            tw, " ".join("%.0f" % v for v in cur["twin"]) if cur["twin"] else "-", len(hist["twin"]), party[1], party[2]))
        table = {}
        for name in ("player", "twin"):
            for i, (t, x, y, z) in enumerate(hist[name]):
                if now - t < 0.5 or not cur[name]:
                    continue
                if abs(x - cur[name][0]) + abs(z - cur[name][2]) < 30:
                    continue
                table.setdefault(round(x), []).append((name, i, x, z))
        objs = [("player", pl), ("twin", tw), ("helper1", party[1]), ("helper2", party[2])]
        hits = {}
        for a, b in RANGES:
            blob = p.read(a, b - a)
            fl = array.array("f")
            fl.frombytes(blob)
            for k in range(len(fl) - 2):
                x = fl[k]
                if x != x or abs(x) < 5 or abs(x) > 1e5:
                    continue
                for cand in (table.get(round(x)), ):
                    if not cand:
                        continue
                    z = fl[k + 2]
                    for name, i, hx, hz in cand:
                        if abs(hx - x) < 0.6 and abs(hz - z) < 0.6:
                            addr = a + 4 * k
                            where = ""
                            for on, o in objs:
                                if o and o <= addr < o + 0x1400:
                                    where = " (%s + 0x%X)" % (on, addr - o)
                            hits.setdefault(addr, "  %08X = spot %d of the %s's path (%.0f, %.0f)%s" % (addr, i, name, hx, hz, where))
        for addr in sorted(hits):
            lines.append(hits[addr])
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed: %s" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
