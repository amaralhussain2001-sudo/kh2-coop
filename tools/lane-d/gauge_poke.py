"""Lane D stretch experiment, ONE copy only (writes memory through PINE).

Waits for the screenshot of <frame> to appear in <test dir>, then keeps writing <value> to <addr> for <seconds>,
printing the hero slots' HP so the screenshots can be compared with the numbers.

  python -I tools/lane-d/gauge_poke.py <port> <testdir> <frame> <addrHex> <valueHex> <seconds>
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0] + "/../lane-b")
from pine import Pine  # noqa: E402

port, tdir, frame = int(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
addr, val, secs = int(sys.argv[4], 16), int(sys.argv[5], 16), float(sys.argv[6])
shot = tdir / f"p1_f{frame:06d}.png"
t0 = time.time()
while not shot.exists():
    if time.time() - t0 > 300:
        sys.exit("timeout waiting for " + shot.name)
    time.sleep(0.05)
p = Pine(port)
before = p.r32(addr)
print(f"frame {frame} reached; {addr:08X} was {before:08X}, writing {val:08X}", flush=True)
t1, last = time.time(), None
while time.time() - t1 < secs:
    try:
        p.w32(addr, val)
        hp = [p.r32(0x01C6C750 - 0x268 * k) for k in range(4)]
        if hp != last:
            last = hp
            print(f"{time.time() - t1:6.2f}s HP slots 1-4: {hp}", flush=True)
    except Exception as e:  # noqa: BLE001
        print("stop:", e)
        break
    time.sleep(0.05)
