"""Read-only probe (ninth round, the seventy-first glue: player 2's own bag). At each snapshot frame: the mark (King Mickey's
record + 0x4E), "his bag is in" (0x000E7FAC), "his menu things are in" (0x000E7E24), whose shop (0x000E7FA8), both wallets,
and the 158 counts (60 materials, 31 Keyblades, 34 armours, 33 accessories) in the GAME'S BAG (save + 0x3580) and in
PLAYER 2'S BAG (King Mickey's ability places 16 .. 79, decoded), shown as "number:count" where not 0, and where they
differ; King Mickey's ability places 0 .. 15 (they must stay the game's) and any place 16 .. 79 without the 0x4000 bit.
  python -I tools/own/bag_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
import os
import pathlib
import struct
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from pine import Pine  # noqa: E402


def table():
    d = (ROOT / "local" / "extract" / "kh2" / "03system.bin").read_bytes()
    cnt = struct.unpack_from("<I", d, 4)[0]
    for i in range(cnt):
        _t, name, off, _s = struct.unpack_from("<I4sII", d, 16 + 16 * i)
        if name.rstrip(b"\0") == b"item":
            break
    _v, n = struct.unpack_from("<II", d, off)
    by = {}
    for k in range(n):
        e = struct.unpack_from("<HBBBBHHHHHHHHBB", d, off + 8 + 24 * k)
        by.setdefault(e[1], []).append((e[0], e[11]))
    return [pl for t in (16, 2, 14, 15) for _i, pl in sorted(by[t])]


PLACES = table()
test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))


def p2_counts(raw):
    hw = struct.unpack("<64H", raw)
    c = []
    for s in range(158):
        if s < 60:
            c.append(hw[s] & 0xFF)
        else:
            g = s - 60
            hi = hw[g >> 1] >> 8
            c.append((hi >> 3) & 7 if g % 2 == 0 else hi & 7)
    bad = [k for k, v in enumerate(hw) if (v & 0xC000) != 0x4000]
    return c, bad


def show(c):
    return " ".join("%d:%d" % (k, v) for k, v in enumerate(c) if v) or "-"


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        bag = p.read(0x0032F0B0, 0x138)
        game = [bag[pl] for pl in PLACES]
        mk = p.r16(0x0032E3AA)
        c2, bad = p2_counts(p.read(0x0032E3D0, 128))
        abil = struct.unpack("<16H", p.read(0x0032E3B0, 32))
        diff = [k for k in range(158) if game[k] != c2[k]]
        lines.append("f%d mark %04X in %d menu2 %d shop %d | wallet P1 %d P2 %d | GAME'S BAG %s | P2'S BAG %s | differ at %s | bad places %s | Mickey's abilities 0-15 %s" % (
            fr, mk, p.r32(0x000E7FAC), p.r32(0x000E7E24), p.r32(0x000E7FA8), p.r32(0x0032DF70), p.r32(0x0032E3A4),
            show(game), show(c2) if mk == 0x5036 else "(no mark)", diff[:20] if mk == 0x5036 else "-", bad[:8] if mk == 0x5036 else "-",
            " ".join("%04X" % a for a in abil if a) or "-"))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
