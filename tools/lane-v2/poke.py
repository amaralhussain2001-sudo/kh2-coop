"""Lane V2 (ONE-copy tests only: it writes memory): write values at given frames, and/or print values.

  python -I tools/lane-v2/poke.py <test-out-dir> <port> <step> [<step> ...]
  step = <frame>:w:<hexaddr>=<value>[,<hexaddr>=<value>...]     32-bit writes when the screenshot of <frame> exists
       | <frame>:r:<hexaddr>[,<hexaddr>...]                      print 32-bit values
       | <frame>:hold<N>:<hexaddr>=<value>[,...]                 keep writing for N seconds
Values are decimal or 0x.. ; "twinslot+OFF" and "heroslot+OFF" may be used as addresses (the unit slots of the
twin and of player 1's hero, read from the objects: twin object at 0x000F05CC, engine player at 0x0034E948,
slot pointer at object+0x48C).
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

out_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
steps = sys.argv[3:]
p = None


def addr(tok):
    tok = tok.strip()
    for name, ptr in (("twinslot", 0x000F05CC), ("heroslot", 0x0034E948), ("twin", 0x000F05CC), ("hero", 0x0034E948)):
        if tok.startswith(name):
            obj = p.r32(ptr)
            base = p.r32(obj + 0x48C) if name.endswith("slot") else obj
            off = tok[len(name):]
            return base + (int(off, 0) if off else 0)
    if tok.startswith("@"):               # @HEXPTR+OFF : the address stored at HEXPTR, plus OFF
        ptr, _, off = tok[1:].partition("+")
        return p.r32(int(ptr, 16)) + (int(off, 0) if off else 0)
    return int(tok, 16)


for st in steps:
    frame, kind, body = st.split(":", 2)
    shot = out_dir / f"p1_f{int(frame):06d}.png"
    t0 = time.time()
    while not shot.exists():
        if time.time() - t0 > 1200:
            sys.exit("timeout waiting for " + shot.name)
        time.sleep(0.05)
    if p is None:
        p = Pine(port)
    if kind == "r":
        print(frame, " ".join("%s=%08X" % (a, p.r32(addr(a))) for a in body.split(",")))
        continue
    pairs = [(x.split("=")[0], int(x.split("=")[1], 0)) for x in body.split(",")]
    end = time.time() + (float(kind[4:]) if kind.startswith("hold") else 0)
    while True:
        for a, v in pairs:
            p.w32(addr(a), v)
        if time.time() >= end:
            break
        time.sleep(0.02)
    print(frame, "wrote", " ".join("%s(%08X)=%d" % (a, addr(a), v) for a, v in pairs))
