"""Lane S3: follow a whole Gummi mission through PINE (read-only): game mode, loaded module, Gummi task state,
both ships' state and hull HP, score, kills, medal value, and whether the unused part of this lane's code cave
(0x000F5410-0x000F5EFF) is still all zero.

  python -I tools/lane-s3/s3_flow.py <port> <seconds>
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

OVL = {0x636A: "gumibattle", 0x62B0: "gumimenu", 0x64B0: "other", 0x0000: "none"}
port, secs = int(sys.argv[1]), float(sys.argv[2])
p = Pine(port, wait=180)
t0 = time.time()
last = None
cave_bad = 0
checks = 0
while time.time() - t0 < secs:
    try:
        mode = p.r32(0x0032BA24)
        sig = p.r32(0x01F18014) & 0xFFFF
        gst = p.r32(0x0032BA64)
        now = p.r32(0x0032BAE0) & 0xFFFF
        cave = p.read(0x000F5410, 0xAF0)
        checks += 1
        if any(cave):
            cave_bad += 1
        info = ""
        if sig == 0x636A:
            s1, s2 = p.r32(0x000F5F80), p.r32(0x000F5F84)
            g = p.r32(0x01F7DE44)
            parts = []
            for nm, s in (("s1", s1), ("s2", s2)):
                if 0x00100000 <= s < 0x02000000 and g != 0:
                    hp = struct.unpack("<f", p.read(s + 0x4AC, 4))[0]
                    parts.append("%s st%d hp%d" % (nm, p.r32(s + 0x50C), int(hp)))
            info = " ".join(parts) + " score %d kills %d medal %d global=%s" % (
                p.r32(0x01F8039C) // 500 * 500, p.r16(0x01F80856) // 5 * 5, p.r32(0x01F803C0),
                "s1" if g == s1 else ("s2" if g == s2 else "%08X" % g))
        cur = (mode, OVL.get(sig, "%04X" % sig), gst, now, info)
    except Exception as e:  # noqa: BLE001
        cur = ("read failed",)
        time.sleep(0.5)
    if cur != last:
        print("%.1fs %s" % (time.time() - t0, " | ".join(str(c) for c in cur)), flush=True)
        last = cur
    time.sleep(0.25)
print("cave 0x000F5410-0x000F5EFF: %d checks, %d with a non-zero byte" % (checks, cave_bad))
