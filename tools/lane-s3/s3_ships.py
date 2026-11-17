"""Lane S3: follow the Gummi ships of a running sandbox emulator through PINE (read-only).

Waits for the Gummi battle module, then prints, whenever something changes: the engine's 'player ship' pointer
(0x01F7DE44), this lane's ship pointers (0x000F5F80 ship 1, 0x000F5F84 ship 2), each ship's controller pointer
(object + 0x4A4), a position-like vector of each ship, the score (0x01F8039C) and the kill count (0x01F80856).

  python -I tools/lane-s3/s3_ships.py <port> <seconds> [--raw N]     --raw N: also dump the first N bytes of each ship once
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

port, secs = int(sys.argv[1]), float(sys.argv[2])
raw = int(sys.argv[sys.argv.index("--raw") + 1]) if "--raw" in sys.argv else 0
POS = int(sys.argv[sys.argv.index("--pos") + 1], 16) if "--pos" in sys.argv else 0x10
p = Pine(port, wait=180)
t0 = time.time()


def ok_ptr(v):
    return 0x00100000 <= v < 0x02000000


def vec(a):
    return struct.unpack("<4f", p.read(a, 16))


last = None
dumped = False
while time.time() - t0 < secs:
    try:
        sig = p.r32(0x01F18014) & 0xFFFF
        if sig != 0x636A:
            cur = ("no gummi battle module",)
        else:
            g = p.r32(0x01F7DE44)
            s1, s2 = p.r32(0x000F5F80), p.r32(0x000F5F84)
            ships = []
            for name, s in (("player", g), ("ship1", s1), ("ship2", s2)):
                if ok_ptr(s):
                    x, y, z, w = vec(s + POS)
                    wx, wy, wz, ww = vec(s + 0xA0)
                    ships.append("%s@%08X pad=%04X st=%d off(%d,%d,%d) w(%d,%d,%d)" % (
                        name, s, p.r32(s + 0x4A4) & 0xFFFF, p.r32(s + 0x50C), round(x / 10) * 10, round(y / 10) * 10,
                        round(z / 10) * 10, round(wx / 200) * 200, round(wy / 200) * 200, round(wz / 200) * 200))
                else:
                    ships.append("%s=%08X" % (name, s))
            ro = vec(0x01F7DEE0)
            o2 = vec(0x000F5FA0)
            cur = (tuple(ships), p.r32(0x01F8039C), p.r16(0x01F80856), "upd2=%d" % (p.r32(0x000F5F88) // 60),
                   "railoff(%d,%d) own2(%d,%d)" % (round(ro[0] / 10) * 10, round(ro[1] / 10) * 10, round(o2[0] / 10) * 10, round(o2[1] / 10) * 10))
            if raw and not dumped and ok_ptr(g):
                dumped = True
                for name, s in (("player", g), ("ship2", s2)):
                    if ok_ptr(s):
                        b = p.read(s, raw)
                        fl = struct.unpack("<%df" % (raw // 4), b)
                        wd = struct.unpack("<%dI" % (raw // 4), b)
                        print("RAW %s @%08X" % (name, s))
                        for i in range(0, raw // 4, 4):
                            print("  +%03X: %s | %s" % (i * 4, " ".join("%08X" % x for x in wd[i:i + 4]),
                                                      " ".join("%10.2f" % x if abs(x) < 1e7 else "         -" for x in fl[i:i + 4])))
    except Exception as e:  # noqa: BLE001
        cur = ("read failed: %s" % e,)
        time.sleep(0.3)
    if cur != last:
        print("%.1fs %s" % (time.time() - t0, " | ".join(str(c) for c in cur)), flush=True)
        last = cur
    time.sleep(0.1)
