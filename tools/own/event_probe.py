"""Read-only probe: what is different between a story scene and a boss's scripted move? At every change of the
camera-hold word: the story event word, the battle byte, the first 0x80 bytes of the event object, a few flag
words of both heroes.

  python -I tools/own/event_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 900]
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 900.0
p = Pine(port, wait=120)
t0 = time.time()
lines = []
final = test_dir / ("p1_f%06d.png" % frames[-1])
last = None


def hx(a, n):
    return " ".join("%08X" % w for w in struct.unpack("<%dI" % (n // 4), p.read(a, n)))


while not final.exists() and time.time() - t0 < timeout:
    try:
        hold, ev = p.r32(0x0033CC38), p.r32(0x0035037C)
        if (hold, ev) != last:
            last = (hold, ev)
            pl, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
            s = "%7.2fs hold %d event %08X battle %02X pause? %s" % (
                time.time() - t0, hold, ev, p.r32(0x01C61958) & 0xFF, hx(0x0034C770, 8))
            for name, o in (("P1", pl), ("TW", tw)):
                if o:
                    s += " | %s +160 %08X +7F8 %08X +10C %08X" % (name, p.r32(o + 0x160), p.r32(o + 0x7F8), p.r32(o + 0x10C))
            lines.append(s)
            if ev:
                lines.append("        event object: " + hx(ev, 0x80))
    except Exception:  # noqa: BLE001
        time.sleep(0.02)
        continue
    time.sleep(0.004)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
