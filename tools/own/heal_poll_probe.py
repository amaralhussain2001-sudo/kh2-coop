"""Read-only probe: hp_poll_probe.py plus the two helpers (the game's helper table 0x01C60528): a line whenever a
hero's HP / MP or a helper's ACTION WORD changes. For "who healed player 2" (a helper's item use shows as an
action of its own just before the HP rises).
  FROM=5900 TO=7000 WATCH=addr:len,... python -I tools/own/heal_poll_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>
Line: f<frame> P1 hp/most mp aXX | P2 ... | H1 <object entry word> aXX hp | H2 ... | <watch words>"""
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


def unit(o, mp=True):
    if not ok(o):
        return (None, "none")
    s = p.r32(o + 0x48C)
    act = p.r32(o + 0x154) & 0xFFFF
    if not ok(s):
        return ((act,), "a%02X noslot" % act)
    hp, mhp = struct.unpack("<2I", p.read(s, 8))
    if mp:
        m, mm = struct.unpack("<2I", p.read(s + 0x180, 8))
        return ((hp, m), "%d/%d mp %d/%d a%02X" % (hp, mhp, m, mm, act))
    ent = p.r32(o + 8)
    oid = p.r32(ent) & 0xFFFF if ok(ent) else 0
    return ((hp, act), "obj %04X %d/%d a%02X" % (oid, hp, mhp, act))


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
        k1, s1 = unit(p.r32(0x00352400))          # the hero built last = player 1's hero (steadier than 0x0034E948)
        k2, s2 = unit(p.r32(0x000F05CC))
        h1, t1 = unit(p.r32(0x01C60528), False)
        h2, t2 = unit(p.r32(0x01C6052C), False)
        w = tuple(p.read(a, n) for a, n in watch)
        if (k1, k2, h1, h2, w) != last:
            ws = " | ".join(" ".join("%08X" % x for x in struct.unpack("<%dI" % (len(b) // 4), b)) for b in w)
            lines.append("f%d P1 %s | P2 %s | H1 %s | H2 %s%s" % (fr, s1, s2, t1, t2, (" | " + ws) if ws else ""))
            last = (k1, k2, h1, h2, w)
            if len(lines) % 40 == 0:
                pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
