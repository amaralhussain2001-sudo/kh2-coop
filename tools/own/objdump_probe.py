"""Read-only probe: at every snapshot frame save the objects that the words in OBJS point to (hex, comma
separated; default: the two summon friend pointers) and the unit slot each of them uses (object + 0x48C).

  python -I tools/own/objdump_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt> [--timeout 600]

Files: <testDir>/obj_<pointer word>_f<frame>.bin (0xD00 bytes) and slot_<pointer word>_f<frame>.bin (0x268 bytes).
"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

test_dir, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",")]
out = sys.argv[4]
timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 900.0
words = [int(x, 16) for x in os.environ.get("OBJS", "01D49960,01D49964").split(",")]
size = int(os.environ.get("OBJLEN", "D00"), 16)
p = Pine(port, wait=120)
t0 = time.time()
lines = []
seen = 0
while seen < len(frames) and time.time() - t0 < timeout:
    f = frames[seen]
    if not (test_dir / ("p1_f%06d.png" % f)).exists():
        time.sleep(0.02)
        continue
    seen += 1
    for w in words:
        try:
            o = p.r32(w)
            line = "f%d [%08X] = %08X" % (f, w, o)
            if 0x00100000 <= o < 0x02000000:
                data = p.read(o, size)
                (test_dir / ("obj_%08X_f%06d.bin" % (w, f))).write_bytes(data)
                s = p.r32(o + 0x48C)
                line += " class %08X slot %08X" % (int.from_bytes(data[0:4], "little"), s)
                if 0x00100000 <= s < 0x02000000:
                    (test_dir / ("slot_%08X_f%06d.bin" % (w, f))).write_bytes(p.read(s, 0x268))
            lines.append(line)
        except Exception as e:  # noqa: BLE001
            lines.append("f%d [%08X] read failed: %r" % (f, w, e))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
