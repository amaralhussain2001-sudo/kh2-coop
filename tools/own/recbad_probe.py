"""Read-only probe for tools/own/make_rec_bad.py: polls the recorder's count; when a bad call was noted (or at the
last snapshot frame) it writes the noted calls and the first one's stack (words that look like code addresses are
marked), plus the engine's player, the twin and their weapons' words for reading.
  python -I tools/own/recbad_probe.py <testDir> <pinePort> <frame,frame,...> <out.txt>"""
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
p = Pine(port, wait=120)
t0, lines = time.time(), []
WAIT = float(os.environ.get("SWEEP_PROBE_WAIT", "400"))
last = test_dir / ("p1_f%06d.png" % frames[-1])
n = 0
while time.time() - t0 < WAIT:
    try:
        n = p.r32(0x000F1D00)
    except Exception:  # noqa: BLE001
        time.sleep(0.2)
        continue
    if n or last.exists():
        break
    time.sleep(0.05)
time.sleep(0.3)
try:
    n = p.r32(0x000F1D00)
    lines.append("bad calls %d, the game's counter now %d (session frame %d), engine's player %08X, twin %08X, player 1's hero %08X"
                 % (n, p.r32(0x0034D4BC), p.r32(0x0034D4BC) + 152, p.r32(0x0034E948), p.r32(0x000F05CC), p.r32(0x000F05D4)))
    ring = struct.unpack("<64I", p.read(0x000F1D10, 256))
    for i in range(min(n, 8)):
        r = ring[8 * i:8 * i + 8]
        lines.append("  call %d: ra %08X a0 %08X s0 %08X s1 %08X s2 %08X s3 %08X at session frame %d, word at s0+8 %08X"
                     % (i, r[0], r[1], r[2], r[3], r[4], r[5], r[6] + 152, r[7]))
    if n:
        st = struct.unpack("<112I", p.read(0x000F1E10, 0x1C0))
        for i in range(0, 112, 2):
            mark = " <- code" if 0x00100000 <= st[i] < 0x00330000 and st[i + 1] == 0 else ""
            lines.append("   sp+%03X %08X %08X%s" % (4 * i, st[i], st[i + 1], mark))
        s0 = ring[2]
        if 0x00100000 <= s0 < 0x02000000:
            d = struct.unpack("<16I", p.read(s0, 64))
            lines.append("  the caller's object %08X: %s" % (s0, " ".join("%08X" % x for x in d)))
            e = d[2]
            if 0x00100000 <= e < 0x02000000:
                ent = p.read(e, 0x60)
                lines.append("  its entry %08X: %s | %r" % (e, ent[:16].hex(), ent[8:0x48].split(b"\0")[0]))
            lines.append("  its word + 0x570: %08X, + 0x160: %08X, + 0x588: %08X" % (p.r32(s0 + 0x570), p.r32(s0 + 0x160), p.r32(s0 + 0x588)))
except Exception as e:  # noqa: BLE001
    lines.append("read failed %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
