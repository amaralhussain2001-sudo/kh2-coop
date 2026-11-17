"""Compare character objects found in a memory dump: which unit slot (HP record) does each one point to?

  python -I tools/lane-b/obj_compare.py <ram.bin> name:hexaddr_of_first_position_copy ...
Prints, for every object, the words near it that point into the unit-slot table (Slot1 0x01C6C750, step -0x268),
and the slots' HP / max HP.
"""
import struct
import sys

ram = open(sys.argv[1], "rb").read()
SLOT1, STEP = 0x01C6C750, 0x268


def u32(a):
    return struct.unpack_from("<I", ram, a)[0]


def slot_of(v):
    d = SLOT1 - v
    if 0 <= d < STEP * 40 and d % STEP == 0:
        return d // STEP + 1
    return None


print("unit slots (HP / max HP at +0 / +4):")
for k in range(1, 16):
    a = SLOT1 - STEP * (k - 1)
    print(f"  slot {k:2d} @0x{a:08X}: {u32(a)} / {u32(a + 4)}   +8..: {u32(a + 8):08X} {u32(a + 12):08X}")

for item in sys.argv[2:]:
    name, addr = item.split(":")
    pos = int(addr, 16)
    print(f"{name}: first position copy at 0x{pos:08X}")
    for off in range(-0x800, 0x1800, 4):
        v = u32(pos + off)
        s = slot_of(v)
        if s:
            print(f"   pos{off:+#07x} -> slot {s} (0x{v:08X})")
