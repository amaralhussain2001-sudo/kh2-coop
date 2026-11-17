"""TEST ONLY (Mail Delivery, disc test-v4-tt91): <base patch> + lines that hold a rider beside the next letter
recipient, chosen by the mission's counter (0x01D48EFC): the real hand-over code runs, the counter rises by the
game's own signal, and the fifth letter ends the job the game's own way. Same lines on both PCs.
  python -I tools/own/make_mailpins.py <basePatchDir> <outDir> [dx dz] [--order=2,4,3,1,5] [--who=1,2,1,2,1]
Hero objects of this disc and these scripts (probe k8-skate-tt91): player 1's 0x01AAE530, the twin 0x01A93D40.
Recipients (room data tt06, group b_50): the five spawn points.
"""
import pathlib
import struct
import sys

NAME = "SLPM-66675_F266B00B.pnach"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
COUNT = 0x01D48EFC
HERO = {1: 0x01AAE530, 2: 0x01A93D40}
REC = {1: (740.3, 550.0, -1458.5), 2: (-141.4, -407.9, 1760.5), 3: (115.6, 300.0, -872.2),
       4: (-906.2, -200.5, 232.6), 5: (2022.9, 26.0, -1114.6)}
args = [a for a in sys.argv[1:] if not a.startswith("--")]
base, out = ROOT / args[0], ROOT / args[1]
dx, dz = (float(args[2]), float(args[3])) if len(args) > 3 else (60.0, 0.0)
order = [2, 4, 3, 1, 5]
who = [1, 2, 1, 2, 1]
for a in sys.argv[1:]:
    if a.startswith("--order="):
        order = [int(x) for x in a[8:].split(",")]
    if a.startswith("--who="):
        who = [int(x) for x in a[6:].split(",")]


def f32(v):
    return struct.unpack("<I", struct.pack("<f", v))[0]


lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST PINS (tools/own/make_mailpins.py %s): for tests only." % " ".join(sys.argv[3:]))
# A rider's position is kept in several places of the hero object and of his board (probe d3-posfind:
# tools/own/posfind_probe.py); all of them are held.
BOARD = {1: 0x01AC8D20, 2: 0x01ACA730}
HERO_OFFS = (0x70, 0x540, 0x590, 0x5C0, 0x6E0, 0x720, 0x730, 0x840, 0xC40)
BOARD_OFFS = (0x70, 0x6E0, 0x720, 0x730, 0xBB0)
for k, (r, w) in enumerate(zip(order, who)):
    x, y, z = REC[r]
    places = [HERO[w] + o for o in HERO_OFFS] + [BOARD[w] + o for o in BOARD_OFFS]
    writes = []
    for a in places:
        for off, v in ((0, x + dx), (4, y), (8, z + dz)):
            writes.append("patch=1,EE,%08X,extended,%08X" % (0x20000000 | (a + off), f32(v)))
    lines.append("patch=1,EE,E0%02X%04X,extended,%08X" % (len(writes) + 1, k, COUNT))            # the counter says: this letter
    lines.append("patch=1,EE,E0%02X0001,extended,%08X" % (len(writes), HERO[w] + 0xB70))         # and the hero is on his board
    lines += writes
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, "order", order, "who", who, "offset", dx, dz)
