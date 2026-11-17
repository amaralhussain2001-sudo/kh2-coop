"""Read-only probe for the recorder of tools/own/make_rec_at.py: at each snapshot frame the count of calls and the
ring (return address, a0, a1, frame counter); at the last frame also the stack of the first call (words that look
like code addresses are marked).
  python -I tools/own/rec_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []


def text(a):
    """The text an argument points to, if it looks like one (the recorder's strings option, REC_TEXT=1)."""
    if os.environ.get("REC_TEXT") != "1" or not 0x00100000 <= a < 0x02000000:
        return ""
    raw = p.read(a, 40).split(bytes(1))[0]
    return ' "%s"' % raw.decode("ascii", "replace") if raw and all(32 <= c < 127 for c in raw) else ""


for k, fr in enumerate(frames):
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < timeout:
        time.sleep(0.02)
    if not snap.exists():
        lines.append("frame %d: screenshot never appeared" % fr)
        break
    try:
        n = p.r32(0x000F1D00)
        ring = struct.unpack("<64I", p.read(0x000F1D10, 256))
        lines.append("frame %d counter %d calls %d state %X number %d" % (fr, p.r32(0x0034D4BC), n, p.r32(0x01D49968), p.r8(0x0032F055)))
        for i in range(min(n, 16)):
            j = (n - 1 - i) & 15
            lines.append("   call -%d: ra %08X a0 %08X a1 %08X counter %d%s" % (i, ring[4 * j], ring[4 * j + 1], ring[4 * j + 2], ring[4 * j + 3], text(ring[4 * j + 1]) + text(ring[4 * j + 2])))
        if k == len(frames) - 1 and n:
            st = struct.unpack("<112I", p.read(0x000F1E10, 0x1C0))
            for i in range(0, 112, 2):
                mark = " <- code" if 0x00100000 <= st[i] < 0x00330000 and st[i + 1] == 0 else ""
                lines.append("   sp+%03X %08X %08X%s" % (4 * i, st[i], st[i + 1], mark))
    except Exception as e:  # noqa: BLE001
        lines.append("frame %d: read failed %r" % (fr, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
