"""Read-only probe (ninth round, job 5): THE TWO CAMERAS at each snapshot frame: the game's camera object
(0x00348710) and player 2's stored camera (0x000F6E00, while it is not in the game's camera memory): the kind
(+ 0x40), the target (+ 0x44), the aim point (+ 0), the eye (+ 0x10), the wished eye / aim (+ 0x60, + 0x80); the
own-screen state (two views on 0x000F6F04, "player 2's camera is in" 0x000F6F0C), the cannon camera's object
(0x004F35A0), the engine's player and the twin with their object numbers, places and turns.
  python -I tools/own/cam_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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


def vec(a):
    return "(%s)" % ", ".join("%.0f" % v for v in struct.unpack("<3f", p.read(a, 12)))


def cam(a):
    return "kind %d target %08X aim %s eye %s wished eye %s wished aim %s" % (
        p.r32(a + 0x40), p.r32(a + 0x44), vec(a), vec(a + 0x10), vec(a + 0x60), vec(a + 0x80))


def obj(o):
    if not ok(o):
        return "none"
    e = p.r32(o + 8)
    m = struct.unpack("<16f", p.read(o + 0x40, 64))
    return "%08X number %04X at %s matrix row0 (%.2f, %.2f, %.2f) row2 (%.2f, %.2f, %.2f) offsets %s %s" % (
        o, p.r32(e) & 0xFFFF if ok(e) else 0, vec(o + 0x70), m[0], m[1], m[2], m[8], m[9], m[10], vec(o + 0xB70), vec(o + 0xB80))


for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        for _try in range(50):                      # wait for a moment in which player 2's camera is not swapped in
            if p.r32(0x000F6F0C) == 0:
                break
        lines.append("f%d two views %d, player 2's camera in %d, cannon camera object %08X" % (
            fr, p.r32(0x000F6F04), p.r32(0x000F6F0C), p.r32(0x004F35A0)))
        lines.append("  camera 1: " + cam(0x00348710))
        lines.append("  camera 2: " + cam(0x000F6E00))
        lines.append("  engine's player " + obj(p.r32(0x0034E948)))
        lines.append("  twin " + obj(p.r32(0x000F05CC)))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
