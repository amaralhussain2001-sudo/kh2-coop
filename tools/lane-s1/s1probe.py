"""Lane S1: at chosen frames of a running sandbox session, read through PINE (read-only):
who is who (lane M's probe), the unit slots, and the mission meters (community map: counters "Point" at
0x01D48EFC step 0x38, gauges at 0x01D48FA4 step 0x34, timer 0x00349DE8; HYPOTHESIS until matched with the picture).

Waits for the session screenshot of each frame, so the frames must be in the run's --snap list.
  python -I tools/lane-s1/s1probe.py <test-out-dir> <pinePort> <frame,frame,...> [--timeout 600] [--raw HEX:LEN,...]
Appends everything to <test-out-dir>/probe.txt.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402
import mprobe  # noqa: E402

POINT1, NXT_POINT = 0x01D48EFC, 0x38
GAUGE1, NXT_GAUGE = 0x01D48FA4, 0x34
TIMER = 0x00349DE8


def meters(p):
    out = []
    for k in range(4):
        b = p.read(POINT1 + NXT_POINT * k, NXT_POINT)
        w = struct.unpack("<14i", b)
        out.append("point%d " % (k + 1) + " ".join("%X" % (x & 0xFFFFFFFF) for x in w))
    for k in range(3):
        b = p.read(GAUGE1 + NXT_GAUGE * k, NXT_GAUGE)
        w = struct.unpack("<13i", b)
        f = struct.unpack("<13f", b)
        out.append("gauge%d " % (k + 1) + " ".join("%X" % (x & 0xFFFFFFFF) for x in w)
                   + " | floats " + " ".join("%.1f" % x for x in f if 0.01 < abs(x) < 1e7))
    b = p.read(TIMER - 8, 32)
    out.append("timer block " + " ".join("%X" % x for x in struct.unpack("<8I", b))
               + " | floats " + " ".join("%.2f" % x for x in struct.unpack("<8f", b) if 0.001 < abs(x) < 1e7))
    return out


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
    raws = []
    if "--raw" in sys.argv:
        for item in sys.argv[sys.argv.index("--raw") + 1].split(","):
            a, _, n = item.partition(":")
            raws.append((int(a, 16), int(n or "16")))
    outdir.mkdir(parents=True, exist_ok=True)
    log = open(outdir / "probe.txt", "a", encoding="utf-8")

    def say(s):
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    t0 = time.time()
    p = None
    for f in frames:
        shot = outdir / ("p1_f%06d.png" % f)
        while not shot.exists():
            if time.time() - t0 > timeout:
                say("timeout waiting for frame %d" % f)
                return
            time.sleep(0.05)
        try:
            if p is None:
                p = Pine(port, wait=30)
            g, objs, slots = mprobe.snapshot(p)
            mprobe.show("frame %d:" % f, g, objs, slots, say)
            for line in meters(p):
                say("     " + line)
            say("     now %08X events %08X %08X  mission ptr area %08X  cntrl %X  cutscene %d/%d" % (
                p.r32(0x0032BAE0), p.r32(0x0032BAE4), p.r32(0x0032BAE8), p.r32(0x004FA440), p.r32(0x01D48DB8),
                p.r32(0x0035DE20), p.r32(0x0035DE28)))
            for a, n in raws:
                b = p.read(a, n)
                say("     raw %08X: %s" % (a, b.hex()))
        except Exception as e:  # noqa: BLE001
            say("frame %d: probe failed: %r" % (f, e))
            p = None


if __name__ == "__main__":
    main()
