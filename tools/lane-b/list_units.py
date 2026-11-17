"""List the character objects in a memory dump by the unit slot (HP record) they point to.

An object keeps a pointer to its unit slot 0x41C bytes after its first position copy (found in test b-twin04).
  python -I tools/lane-b/list_units.py <ram.bin>            offline
  python -I tools/lane-b/list_units.py --live <port> [seconds] [interval]   poll a running emulator (read-only)
"""
import struct
import sys
import time

SLOT1, STEP, LINK = 0x01C6C750, 0x268, 0x41C


def scan(ram):
    res = []
    n = len(ram) // 4
    words = struct.unpack("<%dI" % n, ram[:n * 4])
    slots = {SLOT1 - STEP * k: k + 1 for k in range(20)}
    for i, w in enumerate(words):
        k = slots.get(w)
        if k is None:
            continue
        pos = i * 4 - LINK
        if pos < 0x00100000:
            continue
        x, y, z, wv = struct.unpack_from("<4f", ram, pos)
        if all(abs(v) < 20000 for v in (x, y, z)) and abs(wv - 1.0) < 0.01:
            res.append((k, pos, x, y, z))
    return res


def show(ram, tag=""):
    for k, pos, x, y, z in sorted(scan(ram)):
        hp, mx = struct.unpack_from("<II", ram, SLOT1 - STEP * (k - 1))
        print(f"{tag}slot {k:2d} hp {hp:3d}/{mx:3d}  obj-pos @0x{pos:08X}  ({x:8.1f}, {y:7.1f}, {z:8.1f})")


if sys.argv[1] == "--live":
    sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
    from pine import Pine
    p = Pine(int(sys.argv[2]))
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 30
    every = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
    t0 = time.time()
    objs = None
    while time.time() - t0 < secs:
        try:
            if p.r16(0x0032BAE0) in (0, 0xFFFF) or p.r32(SLOT1) == 0:
                time.sleep(0.1)
                continue
            if objs is None or "--rescan" in sys.argv:
                objs = scan(p.read(0, 0x02000000))
            line = []
            for k, pos, *_ in sorted(objs):
                x, y, z = (p.rf(pos + 4 * j) for j in range(3))
                hp = p.r32(SLOT1 - STEP * (k - 1))
                line.append(f"s{k}@{pos:07X} hp{hp} ({x:.0f},{y:.0f},{z:.0f})")
            print(f"{time.time() - t0:6.1f}s " + " | ".join(line), flush=True)
        except Exception as e:  # noqa: BLE001
            print("err", e)
            time.sleep(0.2)
        time.sleep(every)
else:
    show(open(sys.argv[1], "rb").read())
