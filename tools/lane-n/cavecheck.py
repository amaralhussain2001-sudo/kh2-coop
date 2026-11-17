"""Lane N: read-only check that the routine area 0x000F2800-0x000F2FFF is all zero in a running emulator.
  python -I tools/lane-n/cavecheck.py <outfile> <pinePort> <frame,frame,...>
"""
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "merge"))
from pine import Pine  # noqa: E402

out = open(sys.argv[1], "w", encoding="utf-8")
p = Pine(int(sys.argv[2]), wait=180)
for f in [int(x) for x in sys.argv[3].split(",")]:
    t0 = time.time()
    while True:
        try:
            if p.r32(0x0034D4BC) + 152 >= f:
                break
        except Exception:  # noqa: BLE001
            pass
        if time.time() - t0 > 900:
            sys.exit("timeout")
        time.sleep(0.02)
    blk = p.read(0x000F2800, 0x800)
    nz = [i for i, b in enumerate(blk) if b]
    out.write("frame %d (asked %d) room %04X: %d of 2048 bytes are not zero%s" % (
        p.r32(0x0034D4BC) + 152, f, p.r16(0x0032BAE0), len(nz), (" first at 0x%08X" % (0x000F2800 + nz[0])) if nz else "") + chr(10))
    out.flush()
print("done")
