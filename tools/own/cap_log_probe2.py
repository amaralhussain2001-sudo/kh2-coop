"""Read-only probe for tools/own/make_rec_cap3.py (ninth round, jobs 3 and 4), second form of cap_log_probe.py:
polls the capture ring as fast as PINE answers and writes EVERY CAPTURE as a line, every change of a hero's
action word, and every change of the sixty-fifth glue's PAIR (0x000E7EA0 first hero, A4 second, A8 the captor).
Player 1's hero is taken from 0x00352400 (not from the engine's player word, which holds the twin at moments).
  cap c<counter> f<frame> victim P1|P2|other move FE captor <object> sender -|P1|P2 script <object> player P1|P2 ra <addr>
  act f<frame> P1 a<action> held <bit> hook <word> (place) | P2 ...
  pair f<frame> <first> <second> captor <object> named <hero>
  python -I tools/own/cap_log_probe2.py <testDir> <pinePort> <frames (not used)> <out.txt>      FROM / TO as act_poll_probe.py"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
out = sys.argv[4]
FROM, TO = int(os.environ.get("FROM", "4600")), int(os.environ.get("TO", "8950"))
p = Pine(port, wait=120)
lines, seen, prev, prev_pair = [], None, None, None
t0 = time.time()


def ok(a):
    return 0x00080000 <= a < 0x02000000


def who(o, h1, h2):
    return "P1" if o == h1 and o else "P2" if o == h2 and o else ("-" if not o else "%08X" % o)


def hero(o):
    if not ok(o):
        return "none"
    x, y, z = struct.unpack("<3f", p.read(o + 0x70, 12))
    return "a%02X held %d hook %d (%d, %d, %d)" % (p.r32(o + 0x154) & 0xFFFF, (p.r32(o + 0x160) >> 14) & 1,
                                                 1 if p.r32(o + 0xAEC) else 0, x, y, z)


while time.time() - t0 < float(os.environ.get("SWEEP_PROBE_WAIT", "1500")):
    try:
        cnt = p.r32(0x0034D4BC)
        f = cnt + 152
        if f < FROM:
            time.sleep(0.05)
            continue
        if f > TO:
            break
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        n = p.r32(0x000F1D00)
        if seen is None:
            seen = n
        if n != seen:
            ring = p.read(0x000F1D10, 8 * 32)
            for k in range(max(seen, n - 8), n):
                c, ra, part, vic, mv, snd, scr, pl = struct.unpack_from("<8I", ring, (k & 7) * 32)
                lines.append("cap c%d f%d victim %s move %02X captor %08X sender %s script %s player %s ra %08X" % (
                    c, c + 152, who(vic, h1, h2), mv & 0xFFFF, (part - 320) & 0xFFFFFFFF, who(snd, h1, h2), who(scr, h1, h2), who(pl, h1, h2), ra))
            seen = n
        pa, pb, pc, _t, _m, _i, _o, pn = struct.unpack("<8I", p.read(0x000E7EA0, 32))
        if (pa, pb, pc) != prev_pair:
            lines.append("pair f%d %s %s captor %s named %s" % (f, who(pa, h1, h2), who(pb, h1, h2), "-" if not pc else "%08X" % pc, who(pn, h1, h2)))
            prev_pair = (pa, pb, pc)
        if ok(h1) and ok(h2) and h1 != h2:
            a = (p.r32(h1 + 0x154) & 0xFFFF, p.r32(h2 + 0x154) & 0xFFFF)
            if a != prev:
                lines.append("act f%d P1 %s | P2 %s" % (f, hero(h1), hero(h2)))
                prev = a
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
