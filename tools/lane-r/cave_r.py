"""Lane R: watch this lane's code cave 0x000F3000-0x000F37FF in a running sandbox emulator (read-only).

  python -I tools/lane-r/cave_r.py <test-out-dir> <pinePort> <frame,frame,...> [--pnach file]

Waits for the screenshot of each frame, then:
  without --pnach (game WITHOUT a patch): counts non-zero words in the cave, and lists the 4 KB blocks of
      0x00080000-0x000FFFFF that hold any data (what the game or the PS2 system uses near it);
  with --pnach: counts cave words that differ from the patch file.
Appends the lines to <test-out-dir>/cave.txt.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

LO, HI = 0x000F3000, 0x000F3800


def main():
    outdir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    expect = None
    if "--pnach" in sys.argv:
        expect = {}
        for line in pathlib.Path(sys.argv[sys.argv.index("--pnach") + 1]).read_text().splitlines():
            if line.startswith("patch=1,EE,"):
                p = line.split(",")
                a = int(p[2], 16)
                if LO <= a < HI:
                    expect[a] = int(p[4], 16)
    p = None
    t0 = time.time()
    log = open(outdir / "cave.txt", "a")
    for f in frames:
        shot = outdir / ("p1_f%06d.png" % f)
        while not shot.exists():
            if time.time() - t0 > 900:
                sys.exit("timeout waiting for " + shot.name)
            time.sleep(0.05)
        if p is None:
            p = Pine(port)
        cave = p.read(LO, HI - LO)
        words = struct.unpack("<%dI" % (len(cave) // 4), cave)
        if expect is None:
            nz = sum(1 for w in words if w)
            wide = p.read(0x00080000, 0x00080000)
            blocks = [0x00080000 + i for i in range(0, len(wide), 0x1000) if any(wide[i:i + 0x1000])]
            line = "frame %d: non-zero words in 0x%08X-0x%08X: %d; 4 KB blocks with data in 0x00080000-0x000FFFFF: %s" % (
                f, LO, HI - 1, nz, ", ".join("%05X" % b for b in blocks) or "none")
        else:
            bad = [a for a in range(LO, HI, 4) if words[(a - LO) // 4] != expect.get(a, 0)]
            line = "frame %d: cave words different from the patch file: %d of %d%s" % (
                f, len(bad), (HI - LO) // 4, (" first %08X" % bad[0]) if bad else "")
        print(line)
        log.write(line + "\n")
        log.flush()


if __name__ == "__main__":
    main()
