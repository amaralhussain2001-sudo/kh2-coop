"""Lane E: watch the memory used for the patch routines (0x000F0000-0x000F0FFF) in a running sandbox emulator.

  python -I tools/lane-e/cavecheck.py <test-out-dir> <pinePort> <frame,frame,...> [--pnach file] [--wide]

Without --pnach (run the game WITHOUT a patch): reports every non-zero word in the range at each frame, i.e. anything
the game or the PS2 system itself puts there.
With --pnach: reports words that differ from the patch file (variables 0x000F05C0-0x000F05FF are shown, not counted).
--wide also counts non-zero words in 0x00080000-0x000FFFFF in 4 KB blocks (to see what the system uses near it).
Read-only.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

LO, HI = 0x000F0000, 0x000F1000
VAR_LO, VAR_HI = 0x000F05C0, 0x000F0600


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    expect = {}
    if "--pnach" in sys.argv:
        for line in pathlib.Path(sys.argv[sys.argv.index("--pnach") + 1]).read_text().splitlines():
            if line.startswith("patch="):
                f = line.split(",")
                a = int(f[2], 16)
                if LO <= a < HI:
                    expect[a] = int(f[4], 16)
    wide = "--wide" in sys.argv
    p = None
    t0 = time.time()
    worst = 0
    for fr in frames:
        shot = outdir / ("p1_f%06d.png" % fr)
        while not shot.exists():
            if time.time() - t0 > 900:
                sys.exit("timeout waiting for " + shot.name)
            time.sleep(0.02)
        try:
            if p is None:
                p = Pine(port, wait=20)
            blob = p.read(LO, HI - LO)
            room = p.r32(0x0032BAE0) & 0xFFFF
        except Exception as e:  # noqa: BLE001
            print("f%06d read failed: %s" % (fr, e))
            p = None
            continue
        words = struct.unpack("<%dI" % ((HI - LO) // 4), blob)
        bad, var = [], []
        for i, w in enumerate(words):
            a = LO + 4 * i
            if VAR_LO <= a < VAR_HI and expect:
                if w:
                    var.append("%05X=%08X" % (a & 0xFFFFF, w))
                continue
            if w != expect.get(a, 0):
                bad.append("%08X: %08X (expected %08X)" % (a, w, expect.get(a, 0)))
        worst = max(worst, len(bad))
        line = "f%06d room %04X: %d unexpected word(s)" % (fr, room, len(bad))
        if var:
            line += " | variables " + " ".join(var)
        print(line)
        for b in bad[:12]:
            print("      " + b)
        if wide:
            big = p.read(0x00080000, 0x00080000)
            used = []
            for blk in range(0, len(big), 0x1000):
                n = sum(1 for k in range(blk, blk + 0x1000, 4) if big[k:k + 4] != b"\0\0\0\0")
                if n:
                    used.append("%05X:%d" % (0x80000 + blk, n))
            print("      4 KB blocks with data in 0x00080000-0x000FFFFF: " + (" ".join(used) if used else "none"))
        sys.stdout.flush()
    print("RESULT: worst case %d unexpected word(s)" % worst)


if __name__ == "__main__":
    main()
