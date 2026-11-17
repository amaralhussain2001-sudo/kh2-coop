"""Lane V2: watch this lane's memory range 0x000F7000-0x000F7FFF in a running sandbox emulator (read-only).

  python -I tools/lane-v2/cave_v2.py <test-out-dir> <pinePort> <frame,frame,...> [<pnach file>]

Without a pnach file (run WITHOUT a patch): reports every non-zero word in the range at each frame.
With a pnach file: reports every word of the range that differs from what the patch file writes there
(the lane's variables at 0x000F7F00-0x000F7FFF are printed, not counted).
A check is made when the screenshot of the frame exists, so every frame must be in the run's --snap list.
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

LO, HI, VAR = 0x000F7000, 0x000F8000, 0x000F7F00


def main():
    outdir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",")]
    want = {}
    if len(sys.argv) > 4:
        for line in pathlib.Path(sys.argv[4]).read_text().splitlines():
            if line.startswith("patch=1,EE,"):
                f = line.split(",")
                a = int(f[2], 16)
                if LO <= a < HI:
                    want[a] = int(f[4], 16)
        print("patch file writes %d words inside %08X-%08X" % (len(want), LO, HI - 1))
    p = None
    for fr in frames:
        shot = outdir / ("p1_f%06d.png" % fr)
        t0 = time.time()
        while not shot.exists():
            if time.time() - t0 > 1500:
                sys.exit("timeout waiting for " + shot.name)
            time.sleep(0.05)
        if p is None:
            p = Pine(port)
        bad, nonzero, var = [], 0, []
        for a in range(LO, HI, 4):
            v = p.r32(a)
            if a >= VAR and want:
                if v:
                    var.append("%08X=%08X" % (a, v))
                continue
            if v != want.get(a, 0):
                bad.append("%08X=%08X(want %08X)" % (a, v, want.get(a, 0)))
            if v:
                nonzero += 1
        if want:
            print("frame %d: %d words differ from the patch file%s; variables: %s" % (
                fr, len(bad), (" " + " ".join(bad[:8])) if bad else "", " ".join(var) or "all zero"))
        else:
            print("frame %d: %d non-zero words in the range%s" % (fr, nonzero, (" " + " ".join(bad[:8])) if bad else ""))


if __name__ == "__main__":
    main()
