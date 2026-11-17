"""Wait until the fight room is loaded, dump memory once, and look for objects standing at known spawn positions.

  python -I tools/lane-b/find_objs.py <port> <outfile.bin> "<name>:x:z" ["<name>:x:z" ...]
Looks for three consecutive floats (x, y, z) with x and z within 1.0 of the given values.
"""
import struct
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

port = int(sys.argv[1])
out = sys.argv[2]
targets = []
for t in sys.argv[3:]:
    if t.count(":") != 2:
        continue
    n, x, z = t.split(":")
    targets.append((n, float(x), float(z)))

p = Pine(port)
t0 = time.time()
while True:
    try:
        if p.r16(0x0032BAE0) == 0x0904 and p.r32(0x01C6C750) != 0:
            break
    except Exception:  # noqa: BLE001
        pass
    if time.time() - t0 > 180:
        sys.exit("fight room not reached")
    time.sleep(0.02)
time.sleep(float(sys.argv[sys.argv.index("--delay") + 1]) if "--delay" in sys.argv else 0.3)
ram = p.read(0, 0x02000000)
open(out, "wb").write(ram)
print(f"dumped at {time.time() - t0:.1f}s")
floats = struct.unpack("<%df" % (len(ram) // 4), ram)
for name, x, z in targets:
    hits = []
    for i in range(len(floats) - 2):
        fx = floats[i]
        if abs(fx - x) < 1.0 and abs(floats[i + 2] - z) < 1.0:
            hits.append(i * 4)
    print(name, "candidates:", " ".join(f"0x{h:08X}(y={floats[h // 4 + 1]:.1f})" for h in hits[:40]), f"[{len(hits)}]")
