"""Lane S1: follow an object that has no unit slot (a ball, a cart, a bag) by its position, read-only through PINE.

At the first frame it searches memory for three floats in a row (x, y, z) close to the object's spawn position
from the room data, then prints those places again at every later frame.
  python -I tools/lane-s1/s1track.py <test-out-dir> <pinePort> <frame0,frame1,...> <x> <y> <z> [tolerance]
Frames must be in the run's --snap list (the tool waits for the screenshot files). Appends to <dir>/track.txt.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    x, y, z = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
    tol = float(sys.argv[7]) if len(sys.argv) > 7 else 1.5
    log = open(outdir / "track.txt", "a", encoding="utf-8")

    def say(s):
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    p = None
    cands = []
    t0 = time.time()
    for k, f in enumerate(frames):
        shot = outdir / ("p1_f%06d.png" % f)
        while not shot.exists():
            if time.time() - t0 > 600:
                say("timeout waiting for frame %d" % f)
                return
            time.sleep(0.05)
        try:
            if p is None:
                p = Pine(port, wait=30)
            if k == 0:
                ram = p.read(0x01000000, 0x01000000)
                n = len(ram) // 4
                fl = struct.unpack("<%df" % n, ram)
                for i in range(n - 2):
                    a = fl[i]
                    if a == a and abs(a - x) <= tol and abs(fl[i + 2] - z) <= tol and abs(fl[i + 1] - y) <= max(tol, 60.0):
                        cands.append(0x01000000 + 4 * i)
                say("frame %d: %d places hold the start position (%.1f %.1f %.1f): %s" % (
                    f, len(cands), x, y, z, " ".join("%07X" % c for c in cands[:12])))
            else:
                parts = []
                for c in cands[:12]:
                    vx, vy, vz = struct.unpack("<3f", p.read(c, 12))
                    parts.append("%07X (%.1f %.1f %.1f)" % (c, vx, vy, vz))
                say("frame %d: %s" % (f, "; ".join(parts)))
        except Exception as e:  # noqa: BLE001
            say("frame %d: failed: %r" % (f, e))
            p = None


if __name__ == "__main__":
    main()
