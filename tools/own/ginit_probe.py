"""Read-only probe for tools/own/make_rec_ginit.py (ninth round, job 6): polls the ring of cannon shot start-ups in
the Gummi flight and writes each new one: ra, a0 .. a3, t0, t1, s0 .. s7 (each marked "S1+off" / "S2+off" when it
points into ship 1 (0x000F2600) or ship 2 (0x000F2604)), the place given at a3, the distances from that place to
both ships' places (ship + 0xA0, and the translation of the ship's matrix at ship + 0x70), and the caller's
stack: every word of sp + 0 .. sp + 0x17F that points into a ship or is a code address.
  python -I tools/own/ginit_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>          FROM / TO: session frames"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
out = sys.argv[4]
FROM, TO = int(os.environ.get("FROM", "6000")), int(os.environ.get("TO", "13900"))
MAXN = int(os.environ.get("GINIT_MAX", "120"))
p = Pine(port, wait=120)
lines, seen, n_out = [], None, 0
t0 = time.time()
SHIP = 0x1800


def ok(a):
    return 0x00080000 <= a < 0x02000000


def mark(w, s1, s2):
    if s1 and s1 <= w < s1 + SHIP:
        return "S1+%X" % (w - s1)
    if s2 and s2 <= w < s2 + SHIP:
        return "S2+%X" % (w - s2)
    return "%08X" % w


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


while time.time() - t0 < float(os.environ.get("SWEEP_PROBE_WAIT", "1500")):
    try:
        f = p.r32(0x0034D4BC) + 152
        if f < FROM:
            time.sleep(0.05)
            continue
        if f > TO:
            break
        if p.r16(0x01F18014) != 0x636A:
            time.sleep(0.05)
            continue
        s1, s2 = p.r32(0x000F2600), p.r32(0x000F2604)
        n = p.r32(0x000F1D00)
        if seen is None:
            seen = n
        if n != seen and n_out < MAXN:
            ring = p.read(0x000F1D10, 4 * 176)
            for k in range(max(seen, n - 4), n):
                e = struct.unpack_from("<20I", ring, (k & 3) * 176)
                if e[0] != k + 1:
                    continue
                n_out += 1
                names = ("ra", "a0", "a1", "a2", "a3", "t0", "t1", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7")
                regs = " ".join("%s %s" % (nm, mark(w, s1, s2)) for nm, w in zip(names, e[1:16]))
                place = struct.unpack_from("<3f", ring, (k & 3) * 176 + 64)
                row = "init %d f%d %s | place (%.0f, %.0f, %.0f)" % (e[0], f, regs, place[0], place[1], place[2])
                for nm, s in (("ship 1", s1), ("ship 2", s2)):
                    if ok(s):
                        a = struct.unpack("<3f", p.read(s + 0xA0, 12))
                        b = struct.unpack("<3f", p.read(s + 0x70, 12))
                        row += " | %s +A0 (%.0f, %.0f, %.0f) d %.0f, +70 (%.0f, %.0f, %.0f) d %.0f" % (
                            nm, a[0], a[1], a[2], dist(a, place), b[0], b[1], b[2], dist(b, place))
                lines.append(row)
                sp = e[19]
                if ok(sp):
                    st = struct.unpack("<96I", p.read(sp, 384))
                    hits = ["sp+%X=%s" % (4 * i, mark(w, s1, s2)) for i, w in enumerate(st)
                            if (s1 and s1 <= w < s1 + SHIP) or (s2 and s2 <= w < s2 + SHIP) or 0x01F18000 <= w < 0x01F80000]
                    lines.append("    stack: " + " ".join(hits[:40]))
            seen = n
        elif n != seen:
            seen = n
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
