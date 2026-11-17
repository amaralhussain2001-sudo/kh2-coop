"""Read-only probe for tools/own/make_rec_fin.py: at the last snapshot frame it writes the noted "finish" calls
for an effect file without a place (return address, entry, number, the word + 0x38, counter, name) and the first
call's stack (words that look like code addresses are marked).
  python -I tools/own/recfin_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
p = Pine(port, wait=90)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "300"))
for fr in frames:
    snap = test_dir / ("p1_f%06d.png" % fr)
    while not snap.exists() and time.time() - t0 < WAIT:
        time.sleep(0.05)
    if not snap.exists():
        lines.append("f%d nopic" % fr)
        break
    try:
        n = p.r32(0x000F1D00)
        lines.append("f%d: %d finish calls for an effect file without a place" % (fr, n))
        if fr == frames[-1]:
            for i in range(min(n, 6)):
                raw = p.read(0x000F1D10 + 0x40 * i, 0x40)
                ra, ent, num, w38, cnt = struct.unpack_from("<5I", raw, 0)
                name = raw[0x20:0x40].split(b"\0")[0].decode("ascii", "replace")
                lines.append("   call %d: ra %08X entry %08X number %d word+38 %08X counter %d (session frame %d) name %s" % (i, ra, ent, num, w38, cnt, cnt + 152, name))
            if n:
                st = struct.unpack("<88I", p.read(0x000F1E90, 0x160))
                for i, w in enumerate(st):
                    if 0x00100000 <= w < 0x00340000 or 0x000E8000 <= w < 0x000F8000:
                        lines.append("   sp+%03X %08X <- code" % (4 * i, w))
    except Exception as ex:  # noqa: BLE001
        lines.append("f%d read failed: %s" % (fr, ex))
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
