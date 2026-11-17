"""Read-only probe for the recorder of tools/own/make_rec_at.py that does NOT wait for screenshots: it polls
the call count and, each time it grows, prints the new ring entries (return address, reg1, reg2, frame counter)
and the four place records 0x0032BAE0-0x0032BB1F. Works also when the game stops right after the call.

  python -I tools/own/poll_rec_probe.py <testDir> <pinePort> <frames (ignored)> <out.txt>
  POLL_SECONDS=150 (default): how long it polls.
"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = pathlib.Path(sys.argv[4])
p = Pine(int(sys.argv[2]), wait=120)
t0 = time.time()
limit = float(os.environ.get("POLL_SECONDS", "150"))
lines = []
last = 0
while time.time() - t0 < limit:
    try:
        n = p.r32(0x000F1D00)
        if n != last and n < 100000:
            ring = struct.unpack("<64I", p.read(0x000F1D10, 256))
            rec = p.read(0x0032BAE0, 64)
            for k in range(max(last, n - 16), n):
                e = ring[(k & 15) * 4:(k & 15) * 4 + 4]
                lines.append("call %d: ra %08X reg1 %08X reg2 %08X frame %d" % (k + 1, e[0], e[1], e[2], e[3] + 152))
            lines.append("   now %s | next %s | back %s | last %s" % tuple(
                rec[i:i + 10].hex(" ") for i in (0, 16, 32, 48)))
            last = n
            out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        lines.append("read failed: %r" % (e,))
        time.sleep(0.5)
    time.sleep(0.015)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
