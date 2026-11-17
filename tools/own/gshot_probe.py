"""Read-only probe for tools/own/make_rec_gshot.py (ninth round, job 6): polls the ring of "an enemy takes a hit"
calls in the Gummi flight and writes each new call as lines: the caller, the enemy, the hit record, the caller's
s0 .. s3, and the 36 words from (hit record - 72). Every word that points INTO ship 1 (0x000F2600) or ship 2
(0x000F2604) is marked "S1+off" / "S2+off"; for each of s0 .. s3 that is an address in the flight's memory the
first 64 words are searched for such pointers too. Beside it, at each change: the score, the kills, both hulls.
  python -I tools/own/gshot_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>         FROM / TO: session frames"""
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
MAXLINES = int(os.environ.get("GSHOT_MAX", "400"))
p = Pine(port, wait=120)
lines, seen, prev = [], None, None
t0 = time.time()
SHIP = 0x1800


def ok(a):
    return 0x00080000 <= a < 0x02000000


def mark(w, s1, s2):
    if s1 and s1 <= w < s1 + SHIP:
        return "S1+%X" % (w - s1)
    if s2 and s2 <= w < s2 + SHIP:
        return "S2+%X" % (w - s2)
    return None


def ptrs(words, s1, s2):
    got = ["+%X=%s" % (4 * i, mark(w, s1, s2)) for i, w in enumerate(words) if mark(w, s1, s2)]
    return " ".join(got) if got else "none"


calls = 0
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
        if n != seen and calls < MAXLINES:
            ring = p.read(0x000F1D10, 4 * 176)
            for k in range(max(seen, n - 4), n):
                e = struct.unpack_from("<44I", ring, (k & 3) * 176)
                num, ra, a0, a1, r0, r1, r2, r3 = e[:8]
                if num != k + 1:
                    continue
                calls += 1
                lines.append("hit %d f%d ra %08X enemy %08X record %08X s0 %08X s1 %08X s2 %08X s3 %08X | ship 1 %08X ship 2 %08X" % (
                    num, f, ra, a0, a1, r0, r1, r2, r3, s1, s2))
                lines.append("    record-72: " + " ".join("%08X" % w for w in e[8:]))
                lines.append("    ship pointers in record-72: " + ptrs(e[8:], s1, s2))
                for name, r in (("s0", r0), ("s1", r1), ("s2", r2), ("s3", r3)):
                    if 0x01000000 <= r < 0x02000000:
                        w = struct.unpack("<64I", p.read(r, 256))
                        lines.append("    ship pointers in %s (%08X): %s" % (name, r, ptrs(w, s1, s2)))
            seen = n
        elif n != seen:
            seen = n
        st = (p.r32(0x01F8039C), p.r16(0x01F80856))
        if st != prev:
            h1 = p.rf(s1 + 0x4AC) if ok(s1) else -1
            h2 = p.rf(s2 + 0x4AC) if ok(s2) else -1
            lines.append("score f%d %d kills %d | hull 1 %.0f hull 2 %.0f | calls %d" % (f, st[0], st[1], h1, h2, n))
            prev = st
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
