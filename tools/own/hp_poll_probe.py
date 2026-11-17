"""Read-only probe: a timeline of both heroes' HP and MP (and their action words), polled as fast as PINE answers.
A line is written whenever HP or MP of a hero changes, with the session frame. Optional WATCH=addr:len,... (hex)
adds memory words to every line and writes a line when one of them changes (item places, stock bytes).
  FROM=6000 TO=9000 WATCH=0032F0B0:8 python -I tools/own/hp_poll_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>
Line: f<frame> P1 hp/most mp/most aXX | P2 ... | <watch words>"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
start, end = int(os.environ.get("FROM", "4600")), int(os.environ.get("TO", "8950"))
watch = [tuple(int(v, 16) for v in r.split(":")) for r in os.environ.get("WATCH", "").split(",") if r]
p = Pine(int(sys.argv[2]), wait=120)
lines, last, t0 = [], None, time.time()
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "600"))


def ok(a):
    return 0x00100000 <= a < 0x02000000


def hero(o):
    if not ok(o):
        return (None, "none")
    s = p.r32(o + 0x48C)
    if not ok(s):
        return (None, "noslot")
    hp, mhp = struct.unpack("<2I", p.read(s, 8))
    mp, mmp = struct.unpack("<2I", p.read(s + 0x180, 8))
    act = p.r32(o + 0x154) & 0xFFFF
    return ((hp, mp), "%d/%d mp %d/%d a%02X" % (hp, mhp, mp, mmp, act))


try:
    while time.time() - t0 < WAIT:
        try:
            fr = p.r32(0x0034D4BC) + 152
        except RuntimeError:
            time.sleep(0.3)
            continue
        if fr < start:
            time.sleep(0.05)
            continue
        if fr > end:
            break
        k1, s1 = hero(p.r32(0x0034E948))
        k2, s2 = hero(p.r32(0x000F05CC))
        w = tuple(p.read(a, n) for a, n in watch)
        if (k1, k2, w) != last:
            ws = " | ".join(" ".join("%08X" % x for x in struct.unpack("<%dI" % (len(b) // 4), b)) for b in w)
            lines.append("f%d P1 %s | P2 %s%s" % (fr, s1, s2, (" | " + ws) if ws else ""))
            last = (k1, k2, w)
            if len(lines) % 40 == 0:
                pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
