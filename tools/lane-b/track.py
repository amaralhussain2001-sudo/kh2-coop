"""Follow the player-type objects (those pointing to unit slot 1) of a running sandbox emulator, read-only.

Prints a line whenever the room, the shared HP or a rounded position changes.
  python -I tools/lane-b/track.py <port> <seconds> [--all] [--step N]
--all   also follow the objects of the other unit slots (friends, enemies), rescanned every 3 s
--step  position rounding in game units (default 20)
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

SLOT1, STEP, LINK = 0x01C6C750, 0x268, 0x41C
port, secs = int(sys.argv[1]), float(sys.argv[2])
follow_all = "--all" in sys.argv
rnd = float(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 20.0
p = Pine(port)


def scan():
    ram = p.read(0x01000000, 0x01000000)
    n = len(ram) // 4
    words = struct.unpack("<%dI" % n, ram)
    slots = {SLOT1 - STEP * k: k + 1 for k in range(20)}
    res = []
    for i, w in enumerate(words):
        k = slots.get(w)
        if k is None or (k != 1 and not follow_all):
            continue
        off = i * 4 - LINK
        if off < 0:
            continue
        x, y, z, wv = struct.unpack_from("<4f", ram, off)
        if all(abs(v) < 30000 for v in (x, y, z)) and abs(wv - 1.0) < 0.01:
            res.append((k, 0x01000000 + off))
    return sorted(res)


t0 = time.time()
objs, room, last, last_scan = [], None, None, 0.0
while time.time() - t0 < secs:
    try:
        now = p.r16(0x0032BAE0)
        prog = p.r16(0x0032BAE6)
        hp = p.r32(SLOT1)
        if now in (0, 0xFFFF) or hp == 0:
            time.sleep(0.05)
            continue
        if now != room or not objs or time.time() - last_scan > 2.0:
            time.sleep(0.05 if now == room else 0.5)
            objs = scan()
            room, last_scan = now, time.time()
        parts = []
        for k, a in objs:
            x, y, z = p.rf(a), p.rf(a + 4), p.rf(a + 8)
            parts.append((k, a, round(x / rnd) * rnd, round(y / rnd) * rnd, round(z / rnd) * rnd))
        state = (now, hp, tuple(parts))
        if state != last:
            txt = " | ".join(f"s{k}@{a:07X} ({x:.0f},{y:.0f},{z:.0f})" for k, a, x, y, z in parts)
            print(f"{time.time() - t0:6.2f}s room {now:04X} btl {prog:02X} hp {hp:2d}  {txt}", flush=True)
            last = state
    except Exception as e:  # noqa: BLE001
        time.sleep(0.1)
    time.sleep(0.03)
