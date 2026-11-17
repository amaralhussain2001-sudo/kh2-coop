"""Read-only probe (tenth round, item 7: the boss scripts that stand in no room file): cap_log_probe3.py's lines (every capture with
its captor's object number and kind, every change of a hero's action word, every change of glue 65's PAIR) AND, every 120 game
frames, how many objects of the object numbers in ENTRIES (hex, comma separated) are in the object list (head 0x01D48DA0, next at
object + 2228); a line "ent f<frame> 07FB:n ..." when the counts change, and at the end "entmax 07FB:n ..." (the most seen at once).
(A fork's one-hero variant written later under this same name is now tools/own/cap_log_probe5.py.)
  python -I tools/own/cap_log_probe4.py <testDir> <pinePort> <frames (not used)> <out.txt>      FROM / TO as cap_log_probe3.py"""
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
ENTRIES = [int(x, 16) for x in os.environ.get("ENTRIES", "07FB,07FC,05FF,06FA,09FC,097E,062A,062B").split(",") if x]
p = Pine(port, wait=120)
lines, seen, prev, prev_pair = [], None, None, None
prev_ent, last_ent, most = None, -1000, {e: 0 for e in ENTRIES}
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


def count_entries():
    c = {e: 0 for e in ENTRIES}
    a, n = p.r32(0x01D48DA0), 0
    while ok(a) and n < 600:
        e = p.r32(a + 8)
        if ok(e):
            i = p.r32(e) & 0xFFFF
            if i in c:
                c[i] += 1
        a = p.r32(a + 2228)
        n += 1
    return c


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
        if f - last_ent >= 120:
            last_ent = f
            c = count_entries()
            for e in ENTRIES:
                most[e] = max(most[e], c[e])
            if c != prev_ent:
                lines.append("ent f%d %s" % (f, " ".join("%04X:%d" % (e, c[e]) for e in ENTRIES)))
                prev_ent = c
        n = p.r32(0x000F1D00)
        if seen is None:
            seen = n
        if n != seen:
            ring = p.read(0x000F1D10, 8 * 32)
            for k in range(max(seen, n - 8), n):
                c_, ra, part, vic, mv, snd, scr, pl = struct.unpack_from("<8I", ring, (k & 7) * 32)
                cap = (part - 320) & 0xFFFFFFFF
                kind = "?"
                try:
                    ent = p.r32(cap + 8) if ok(cap) else 0
                    if ok(ent):
                        kind = "obj %04X kind %d" % (p.r32(ent) & 0xFFFF, p.read(ent + 4, 1)[0])
                except Exception:  # noqa: BLE001
                    pass
                lines.append("cap c%d f%d victim %s move %02X captor %08X sender %s script %s player %s ra %08X | %s" % (
                    c_, c_ + 152, who(vic, h1, h2), mv & 0xFFFF, cap, who(snd, h1, h2), who(scr, h1, h2), who(pl, h1, h2), ra, kind))
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
lines.append("entmax %s" % " ".join("%04X:%d" % (e, most[e]) for e in ENTRIES))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
