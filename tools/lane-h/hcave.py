"""Lane H: watch this lane's code-cave memory 0x000F2000-0x000F27FF in a running sandbox emulator. Read-only (PINE).

  python -I tools/lane-h/hcave.py <pinePort> <frame,frame,...> [--pnach file]

Without --pnach (run WITHOUT the lane H lines): prints the number of non-zero words in the range at each frame,
i.e. anything the game or the PS2 system puts there.
With --pnach: prints the number of words that differ from the patch file (the variables 0x000F27C0-0x000F27FF are
shown, not counted). Frames are the session's frames, taken from the game's own counter.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

LO, HI, VARS = 0x000F2000, 0x000F2800, 0x000F27C0


def frame(p):
    return p.r32(0x0034D4BC) + 152


def main():
    port = int(sys.argv[1])
    frames = [int(x) for x in sys.argv[2].split(",") if x]
    expect = {}
    if "--pnach" in sys.argv:
        for line in pathlib.Path(sys.argv[sys.argv.index("--pnach") + 1]).read_text().splitlines():
            if line.startswith("patch=1,EE,"):
                q = line.split(",")
                a = int(q[2], 16)
                if LO <= a < HI:
                    expect[a] = int(q[4], 16)
    p = Pine(port, wait=120)
    t0 = time.time()
    for f in frames:
        while True:
            try:
                if frame(p) >= f:
                    break
            except Exception:  # noqa: BLE001
                pass
            if time.time() - t0 > 900:
                sys.exit("timeout waiting for frame %d" % f)
            time.sleep(0.02)
        data = p.read(LO, HI - LO)
        words = struct.unpack("<%dI" % (len(data) // 4), data)
        room = p.r32(0x0032BAE0) & 0xFFFF
        btl = p.r32(0x01C61958) & 0xFF
        if expect:
            bad = [(LO + 4 * i, w) for i, w in enumerate(words) if LO + 4 * i < VARS and w != expect.get(LO + 4 * i, 0)]
            var = [(LO + 4 * i, w) for i, w in enumerate(words) if LO + 4 * i >= VARS and w]
            print("frame %6d room %04X battle %d: %d words differ from the patch file%s; variables: %s" % (
                f, room, btl, len(bad), (" " + ", ".join("%08X=%08X" % x for x in bad[:6])) if bad else "",
                ", ".join("%08X=%08X" % x for x in var) or "all zero"), flush=True)
        else:
            nz = [(LO + 4 * i, w) for i, w in enumerate(words) if w]
            print("frame %6d room %04X battle %d: %d non-zero words in 0x%08X-0x%08X%s" % (
                f, room, btl, len(nz), LO, HI - 1, (" " + ", ".join("%08X=%08X" % x for x in nz[:6])) if nz else ""), flush=True)


if __name__ == "__main__":
    main()
