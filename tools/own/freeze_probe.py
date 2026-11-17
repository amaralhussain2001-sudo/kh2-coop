"""Read-only probe (ninth round): WHERE IS THE GAME WHEN IT FREEZES. It polls the game's own counter (0x0034D4BC,
session frame - 152). When the counter stands still for 4 seconds (after FROM), it writes:
  * the sixty-fifth glue's state (0x000E7EA0 .. 0x000E7EDF), the hold note (0x000E7C0C .. 0x000E7C1F), both heroes'
    action / held bit / captor word / hooked script, the capture ring of make_rec_cap3.py (when that kit is in);
  * THE CALL CHAIN: the whole memory is searched for words that are return addresses into the patch's own
    routines (0x000E8000 .. 0x000F8000); around each place found above 0x00400000 (a stack, not code) the words
    that look like code addresses are listed, lowest address (deepest call) first.
Before the freeze it writes a line at each change of the pair, as cap_log_probe2.py.
  python -I tools/own/freeze_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>       FROM / TO: session frames"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
out = sys.argv[4]
FROM, TO = int(os.environ.get("FROM", "4700")), int(os.environ.get("TO", "19900"))
p = Pine(port, wait=120)
lines, prev_pair = [], None
t0 = time.time()


def ok(a):
    return 0x00080000 <= a < 0x02000000


def code(w):
    return 0x00100000 <= w < 0x00300000 or 0x000E8000 <= w < 0x000F8000 or 0x01F18000 <= w < 0x01F80000


def hero(o):
    if not ok(o):
        return "none"
    return "a%02X held %d captor word %08X hook %08X attach? at (%s)" % (
        p.r32(o + 0x154) & 0xFFFF, (p.r32(o + 0x160) >> 14) & 1, p.r32(o + 0x240), p.r32(o + 0xAEC),
        ", ".join("%.0f" % v for v in struct.unpack("<3f", p.read(o + 0x70, 12))))


last, since, done = None, time.time(), False
while time.time() - t0 < float(os.environ.get("SWEEP_PROBE_WAIT", "1500")):
    try:
        cnt = p.r32(0x0034D4BC)
        f = cnt + 152
        if f < FROM:
            time.sleep(0.05)
            continue
        if f > TO:
            break
        if cnt != last:
            last, since = cnt, time.time()
            pa, pb, pc = struct.unpack("<3I", p.read(0x000E7EA0, 12))
            if (pa, pb, pc) != prev_pair:
                lines.append("pair f%d %08X %08X captor %08X" % (f, pa, pb, pc))
                prev_pair = (pa, pb, pc)
            time.sleep(0.01)
            continue
        if time.time() - since < 4.0:
            time.sleep(0.05)
            continue
        # the counter stands still
        lines.append("FROZEN at f%d (counter %d)" % (f, cnt))
        h1, h2 = p.r32(0x00352400), p.r32(0x000F05CC)
        lines.append("  P1 %08X %s" % (h1, hero(h1)))
        lines.append("  P2 %08X %s" % (h2, hero(h2)))
        lines.append("  engine's player %08X running script %08X (its object %08X)" % (
            p.r32(0x0034E948), p.r32(0x0034D8A4), p.r32(p.r32(0x0034D8A4) + 56) if ok(p.r32(0x0034D8A4)) else 0))
        lines.append("  glue 65 state 7EA0..: " + " ".join("%08X" % w for w in struct.unpack("<16I", p.read(0x000E7EA0, 64))))
        lines.append("  hold note 7C0C..: " + " ".join("%08X" % w for w in struct.unpack("<5I", p.read(0x000E7C0C, 20))))
        n = p.r32(0x000F1D00)
        ring = p.read(0x000F1D10, 8 * 32)
        for k in range(max(0, n - 4), n):
            c, ra, part, vic, mv, snd, scr, pl = struct.unpack_from("<8I", ring, (k & 7) * 32)
            lines.append("  capture %d: f%d victim %08X move %X captor %08X sender %08X script %08X player %08X ra %08X" % (
                k, c + 152, vic, mv & 0xFFFF, (part - 320) & 0xFFFFFFFF, snd, scr, pl, ra))
        found = []
        for base in range(0x00400000, 0x02000000, 0x40000):
            raw = p.read(base, 0x40000)
            ws = struct.unpack("<%dI" % (len(raw) // 4), raw)
            for i, w in enumerate(ws):
                if 0x000E8000 <= w < 0x000F0000 and (w & 3) == 0:
                    found.append(base + 4 * i)
        lines.append("  %d words above 0x00400000 point into the patch's routines" % len(found))
        shown = 0
        groups = []
        for a in found:
            if groups and a - groups[-1][-1] < 0x400:
                groups[-1].append(a)
            else:
                groups.append([a])
        for g in groups:
            if shown >= 12:
                break
            lo, hi = g[0] - 0x500, g[-1] + 0x200
            raw = p.read(lo, hi - lo)
            ws = struct.unpack("<%dI" % (len(raw) // 4), raw)
            chain = ["%08X:%08X" % (lo + 4 * i, w) for i, w in enumerate(ws) if code(w) and (w & 3) == 0]
            lines.append("  stack near %08X .. %08X (deepest first): %s" % (g[0], g[-1], " ".join(chain[:120])))
            shown += 1
        done = True
        break
    except Exception as ex:  # noqa: BLE001
        lines.append("read failed: %s" % ex)
        time.sleep(0.1)
if not done:
    lines.append("no freeze seen (the last frame %s)" % (last + 152 if last is not None else "?"))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
