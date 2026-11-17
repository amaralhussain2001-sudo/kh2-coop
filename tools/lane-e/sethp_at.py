"""Lane E, ONE-copy tests only: when the session screenshot of <frame> exists, write <hp> to the shared HP word
(unit slot 1, 0x01C6C750) through PINE.  python -I sethp_at.py <test-out-dir> <pinePort> <frame> <hp>"""
import pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine
out, port, frame, hp = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
shot = out / ("p1_f%06d.png" % frame)
t0 = time.time()
while not shot.exists():
    if time.time() - t0 > 400:
        sys.exit("timeout")
    time.sleep(0.02)
p = Pine(port, wait=20)
print("hp before", p.r32(0x01C6C750)); p.w32(0x01C6C750, hp); print("hp set to", p.r32(0x01C6C750))
