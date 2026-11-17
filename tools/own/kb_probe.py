"""Read-only probe (ninth round, plan row 39: player 2's own Keyblade). At each snapshot frame, one line:
  the Keyblade words (Sora's record + 0, the view T's + 0, player 2's Keyblade, player 1's as last seen, the mark),
  each hero's weapon objects (first hand / second hand) (its object number and model name, read from its object entry),
  the bag's count of the two test Keyblades (places 0x22, 0x23),
  and the file pool's entries with the numbers 2300 .. 2399 and 5000 .. 5099 (the hero's block, the Drive Forms') (number, size, place, state, name) and the pool's end.
  python -I tools/own/kb_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def weapon(hero, hand=0):
    if not ok(hero):
        return "no hero"
    w = p.r32(hero + 0xAF8 + 4 * hand)
    if not ok(w):
        return "no weapon"
    e = p.r32(w + 8)
    if not ok(e):
        return "weapon %08X no entry" % w
    return "%04X %s (number %d)" % (p.r32(e) & 0xFFFF, text_of(p.read(e + 8, 0x20)), p.r32(w + 2560))


def hp(hero):
    if not ok(hero):
        return "none"
    s = p.r32(hero + 0x48C)
    if not ok(s):
        return "noslot"
    return "%d/%d a%02X" % (p.r32(s), p.r32(s + 4), p.r32(hero + 0x154) & 0xFFFF)


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        h1, h2 = p.r32(0x0034E948), p.r32(0x000F05CC)
        kb, lw, m2, km = struct.unpack("<4H", p.read(0x0032E39C, 8))
        s = "f%d P1 %s P2 %s | record %04X view %04X P2's %04X last %04X mark %04X menu2 %d | P1 holds %s | P2 holds %s | bag %d %d" % (
            fr, hp(h1), hp(h2), p.r32(0x0032E020) & 0xFFFF, p.r32(0x000E7D00) & 0xFFFF, kb, lw, km, p.r32(0x000E7E24),
            weapon(h1) + " / " + weapon(h1, 1), weapon(h2) + " / " + weapon(h2, 1), p.read(0x0032F0D2, 1)[0], p.read(0x0032F0D3, 1)[0])
        head, limit = p.r32(0x0034DCA0), p.r32(0x0034DCB0)
        a, n, last, pool = head, 0, 0, []
        while ok(a) and n < 600:
            raw = p.read(a, 0x40)
            w = struct.unpack("<16I", raw)
            num = w[10]
            if num < 10000:
                last = max(last, w[12] + w[11])
            if 2300 <= num < 2400 or 5000 <= num < 5100:
                pool.append("%d %s %d@%d s%d" % (num, text_of(raw[2:0x24]).replace("obj/", ""), w[11], w[12], raw[1]))
            a = w[15]
            n += 1
        s += " | pool: " + ", ".join(pool) + " | kept files end %d of %d (free %d)" % (last, limit, limit - last)
        lines.append(s)
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
