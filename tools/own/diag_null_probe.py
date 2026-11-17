"""Read-only probe for tools/own/make_diag_null.py: poll the recorder and print each new record with context.
  python -I tools/own/diag_null_probe.py <pinePort> <out.txt> <seconds>
"""
import pathlib
import struct
import sys
import time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

port, out, secs = int(sys.argv[1]), sys.argv[2], float(sys.argv[3])
p = Pine(port, wait=120)
lines, last, t0 = [], 0, time.time()
while time.time() - t0 < secs:
    try:
        n = p.r32(0x000F4A00)
        if n != last:
            last = n
            obj = p.r32(0x000F4A04)
            a = struct.unpack("<24I", p.read(0x000F4A10, 96))
            b = struct.unpack("<24I", p.read(0x000F4A70, 96))
            hero, twin = p.r32(0x00348638), p.r32(0x000F05CC)
            lines.append("count %d  object %08X  (hero %08X twin %08X engine player %08X)  room %04X" % (n, obj, hero, twin, p.r32(0x0034E948), p.r32(0x0032BAE0) & 0xFFFF))
            lines.append("  object: " + " ".join("%08X" % x for x in a))
            lines.append("  record: " + " ".join("%08X" % x for x in b))
            for nm, c in (("S ", 0x01C5F530), ("S2", 0x000F1000)):
                lines.append("  %s +20 %08X page %08X top %08X act-request %08X %08X" % (nm, p.r32(c + 0x20), p.r32(c + 0xAA4), p.r32(c + 0x8C0), p.r32(c + 4), p.r32(c + 8)))
            for nm, o in (("hero", hero), ("twin", twin)):
                if o:
                    lines.append("  %s action %08X  +1C %08X" % (nm, p.r32(o + 0xB50) if False else p.r32(o + 0x1C), p.r32(o + 0x1C)))
    except Exception:  # noqa: BLE001  (not ready yet, or closing: try again)
        time.sleep(0.5)
        try:
            p = Pine(port, wait=5)
        except Exception:  # noqa: BLE001
            pass
    time.sleep(0.05)
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines[:60]))
