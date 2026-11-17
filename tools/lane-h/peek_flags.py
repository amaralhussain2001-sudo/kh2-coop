"""Lane H: read a few facts about the two heroes and the enemies once the fight runs. Read-only (PINE).

  python -I tools/lane-h/peek_flags.py <pinePort> <frame>
Prints: the "is the player" flag (object + 0x588, bit 0x80) the script call 'is this the player' tests, for the hero
and the twin; each hero's object type byte; and for every enemy in a unit slot its object type byte and target.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

SLOT1, STEP, NSLOT = 0x01C6C750, 0x268, 24
p = Pine(int(sys.argv[1]), wait=120)
want = int(sys.argv[2])
t0 = time.time()
while True:
    try:
        if p.r32(0x0034D4BC) + 152 >= want and p.r32(0x0034E948):
            break
    except Exception:  # noqa: BLE001
        pass
    if time.time() - t0 > 600:
        sys.exit("timeout")
    time.sleep(0.05)
hero, twin = p.r32(0x0034E948), p.r32(0x000F05CC)
for name, o in (("hero", hero), ("twin", twin)):
    if not o:
        print(name, "none")
        continue
    fl = p.r32(o + 0x588)
    ent = p.r32(o + 8)
    print("%s %07X: flags at +0x588 = %08X ('is the player' bit 0x80: %s), object id 0x%X, type byte %d" % (
        name, o, fl, "set" if fl & 0x80 else "clear", p.r32(ent), p.r8(ent + 4)))
base = SLOT1 - STEP * (NSLOT - 1)
pool = p.read(base, STEP * NSLOT)
for k in range(NSLOT):
    b = pool[k * STEP:(k + 1) * STEP]
    hp = struct.unpack_from("<i", b, 0)[0]
    flags, sid, ref, owner = struct.unpack_from("<IiiI", b, 0x250)
    if not owner or owner in (hero, twin):
        continue
    ent = p.r32(owner + 8)
    tg = p.r32(owner + 0x9F4)
    print("slot %2d owner %07X object id 0x%04X type byte %2d status id %d HP %d target %s mode %d" % (
        (SLOT1 - (base + k * STEP)) // STEP + 1, owner, p.r32(ent), p.r8(ent + 4), sid, hp,
        "hero" if tg == hero else "twin" if tg == twin else ("%07X" % tg), struct.unpack("<i", p.read(owner + 0xA00, 4))[0]))
