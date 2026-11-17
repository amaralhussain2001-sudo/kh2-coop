"""Lane S3: follow the world-map cursor ship and the game mode through PINE (read-only).

Waits for the world map (Now = world 0x0F), finds the cursor object by its start position, then prints a line
whenever the rounded position, the game mode (0x0032BA24), the loaded overlay (word at 0x01F18014) or the Gummi
battle task state (0x0032BA64) changes.

  python -I tools/lane-s3/wm_probe.py <port> <seconds> [x y z]      (start position, default 0 -400 -5000)
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

OVL = {0x087C636A: "gumibattle", 0x087C62B0: "gumimenu", 0x087C64B0: "other(64B0)"}
port, secs = int(sys.argv[1]), float(sys.argv[2])
sx, sy, sz = (float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0.0, -400.0, -5000.0)
p = Pine(port, wait=120)
t0 = time.time()


def now():
    return p.r32(0x0032BAE0) & 0xFFFF


while True:
    try:
        if now() == 0x000F:
            break
    except Exception:  # noqa: BLE001
        pass
    if time.time() - t0 > secs:
        sys.exit("world map not reached")
    time.sleep(0.2)
time.sleep(1.5)
cands = []
for base, size in ((0x00300000, 0x00D00000), (0x01000000, 0x01000000)):
    ram = p.read(base, size)
    n = len(ram) // 4
    fl = struct.unpack("<%df" % n, ram)
    for i in range(n - 2):
        if abs(fl[i] - sx) < 5.0 and abs(fl[i + 2] - sz) < 5.0 and -1200.0 < fl[i + 1] < 200.0 and fl[i + 1] != 0.0:
            cands.append(base + 4 * i)
print("%.1fs world map reached; position candidates:" % (time.time() - t0), ["%08X" % c for c in cands[:40]], flush=True)
first = {}
last = None
while time.time() - t0 < secs:
    try:
        mode = p.r32(0x0032BA24)
        ovl = p.r32(0x01F18014)
        gst = p.r32(0x0032BA64)
        nw = p.r32(0x0032BAE0)
        pos = []
        for c in cands[:40]:
            b = p.read(c, 12)
            x, y, z = struct.unpack("<3f", b)
            v = (round(x / 50) * 50, round(y / 50) * 50, round(z / 50) * 50)
            if c not in first:
                first[c] = v
            if v != first[c]:
                pos.append(("%08X" % c, v))
        pos = pos[:3]
    except Exception as e:  # noqa: BLE001
        print("%.1fs read failed: %s" % (time.time() - t0, e), flush=True)
        time.sleep(0.5)
        continue
    cur = (mode, ovl, gst, nw & 0xFFFFFF, tuple(pos))
    if cur != last:
        print("%.1fs mode %d ovl %s gumitask %d now %06X pos %s" % (time.time() - t0, mode, OVL.get(ovl, "%08X" % ovl), gst,
                                                               nw & 0xFFFFFF, pos), flush=True)
        last = cur
    time.sleep(0.1)
