"""Read-only probe (ninth round, job 3): THE WHOLE STATE OF A HOLD at each snapshot frame: the game's counter, the
story event and camera hold words, both heroes (action, held bit, captor word, hooked script, attach, place, HP),
the sixty-fifth glue's state (0x000E7EA0 ..), the hold note (0x000E7C0C ..), the last captures of the ring of
make_rec_cap3.py (when that kit is in), and every object of the room that has an HP record with its action.
  python -I tools/own/hold_state_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def ok(a):
    return 0x00080000 <= a < 0x02000000


def text_of(raw):
    best, cur = b"", b""
    for b in raw:
        if 0x20 <= b < 0x7F:
            cur += bytes([b])
        else:
            if len(cur) > len(best):
                best = cur
            cur = b""
    if len(cur) > len(best):
        best = cur
    return best.decode("ascii", "replace") if len(best) >= 4 else ""


def hero(o):
    if not ok(o):
        return "none"
    slot = p.r32(o + 0x48C)
    hp = "%d/%d" % struct.unpack("<2i", p.read(slot, 8)) if ok(slot) else "noslot"
    st = p.r32(o + 0x0C)
    more = " | attached to %08X script flags %08X %08X state object %08X: %s | motion part: %s | part+0x90: %s" % (
        p.r32(o + 0x570), p.r32(o + 0x108), p.r32(o + 0x10C), st,
        " ".join("%08X" % w for w in struct.unpack("<6I", p.read(st, 24))) if ok(st) else "-",
        " ".join("%08X" % w for w in struct.unpack("<8I", p.read(o + 0x140, 32))),
        " ".join("%08X" % w for w in struct.unpack("<4I", p.read(o + 0x1D0, 16))))
    return "%08X a%02X held %d captor word %08X hook %08X flags160 %08X HP %s at (%s)" % (
        o, p.r32(o + 0x154) & 0xFFFF, (p.r32(o + 0x160) >> 14) & 1, p.r32(o + 0x240), p.r32(o + 0xAEC), p.r32(o + 0x160), hp,
        ", ".join("%.0f" % v for v in struct.unpack("<3f", p.read(o + 0x70, 12)))) + more


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        scr = p.r32(0x0034D8A4)
        lines.append("f%d counter %d (+152 = %d) story event %08X camera hold %08X engine's player %08X running script %08X" % (
            fr, p.r32(0x0034D4BC), p.r32(0x0034D4BC) + 152, p.r32(0x0035037C), p.r32(0x0033CC38), p.r32(0x0034E948), scr))
        lines.append("  P1 " + hero(h1))
        lines.append("  P2 " + hero(h2))
        lines.append("  glue 65: " + " ".join("%08X" % w for w in struct.unpack("<16I", p.read(0x000E7EA0, 64))))
        lines.append("  hold note: " + " ".join("%08X" % w for w in struct.unpack("<5I", p.read(0x000E7C0C, 20))))
        n = p.r32(0x000F1D00)
        ring = p.read(0x000F1D10, 8 * 32)
        for k in range(max(0, n - 5), n):
            c, ra, part, vic, mv, snd, s2, pl = struct.unpack_from("<8I", ring, (k & 7) * 32)
            lines.append("  capture %d: f%d victim %08X move %X captor %08X sender %08X script %08X player %08X ra %08X" % (
                k, c + 152, vic, mv & 0xFFFF, (part - 320) & 0xFFFFFFFF, snd, s2, pl, ra))
        a, k = p.r32(0x01D48DA0), 0
        while ok(a) and k < 400:
            slot, e = p.r32(a + 0x48C), p.r32(a + 8)
            if ok(slot) and ok(e) and a not in (h1, h2):
                lines.append("  obj %08X %04X %-16s HP %d/%d act %04X word140 %08X flags160 %08X" % (
                    a, p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20)), p.r32(slot), p.r32(slot + 4), p.r32(a + 0x154) & 0xFFFF,
                    p.r32(a + 0x140), p.r32(a + 0x160)))
            a = p.r32(a + 2228)
            k += 1
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
