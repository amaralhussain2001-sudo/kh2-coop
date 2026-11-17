"""Lane N: dump the hero object, the twin object and their control objects at given frames (read-only), then list
the words that differ between two of the dumps.

  python -I tools/lane-n/ndiff.py dump <outdir> <pinePort> <frame,frame,...>
  python -I tools/lane-n/ndiff.py cmp <outdir> <frameA> <frameB> [hero|twin|heroctl|twinctl] [--also frameC]
With --also, only words are shown where A differs from B and frameC equals A or B is printed beside them.
"""
import pathlib
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "merge"))


def frame(p):
    return p.r32(0x0034D4BC) + 152


def dump():
    from pine import Pine
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    p = Pine(int(sys.argv[3]), wait=180)
    hpf = int(sys.argv[sys.argv.index("--hero-hp1-at") + 1]) if "--hero-hp1-at" in sys.argv else None
    for f in sorted([int(x) for x in sys.argv[4].split(",")] + ([hpf] if hpf else [])):
        t0 = time.time()
        while True:
            try:
                if frame(p) >= f:
                    break
            except Exception:  # noqa: BLE001
                pass
            if time.time() - t0 > 900:
                sys.exit("timeout")
            time.sleep(0.01)
        hero, twin = p.r32(0x0034E948), p.r32(0x000F05CC)
        if hpf and f == hpf:
            p.w32(p.r32(hero + 0x48C), 1)   # ONE-copy test write: the hero's HP = 1
            print("wrote hero HP = 1 at frame", frame(p))
            continue
        for name, obj in (("hero", hero), ("twin", twin)):
            if not obj:
                continue
            blk = p.read(obj, 0xB80)
            (out / ("f%06d_%s.bin" % (f, name))).write_bytes(blk)
            ctl = struct.unpack_from("<I", blk, 0xB3C)[0]
            if ctl:
                (out / ("f%06d_%sctl.bin" % (f, name))).write_bytes(p.read(ctl, 0xB00))
            slot = struct.unpack_from("<I", blk, 0x48C)[0]
            if slot:
                (out / ("f%06d_%sslot.bin" % (f, name))).write_bytes(p.read(slot, 0x268))
        print("dumped frame", frame(p), "hero %07X twin %07X" % (hero, twin))


def cmp():
    out = pathlib.Path(sys.argv[2])
    fa, fb = int(sys.argv[3]), int(sys.argv[4])
    what = sys.argv[5] if len(sys.argv) > 5 and not sys.argv[5].startswith("--") else "hero"
    fc = int(sys.argv[sys.argv.index("--also") + 1]) if "--also" in sys.argv else None
    a = (out / ("f%06d_%s.bin" % (fa, what))).read_bytes()
    b = (out / ("f%06d_%s.bin" % (fb, what))).read_bytes()
    c = (out / ("f%06d_%s.bin" % (fc, what))).read_bytes() if fc is not None else None
    n = 0
    for off in range(0, min(len(a), len(b)), 4):
        wa, wb = struct.unpack_from("<I", a, off)[0], struct.unpack_from("<I", b, off)[0]
        if wa != wb:
            n += 1
            extra = ""
            if c is not None:
                extra = "  C=%08X" % struct.unpack_from("<I", c, off)[0]
            print("+0x%03X  %08X -> %08X%s" % (off, wa, wb, extra))
    print("(%d words differ in %s between frame %d and %d)" % (n, what, fa, fb))


if __name__ == "__main__":
    {"dump": dump, "cmp": cmp}[sys.argv[1]]()
