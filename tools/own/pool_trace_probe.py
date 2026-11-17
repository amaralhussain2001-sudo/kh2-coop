"""Read-only probe: a timeline of the game's pool of prompt objects (manager at [0x003486A4], 9 objects of 896
bytes, free count at +8100). It polls as fast as PINE answers (no waiting for pictures) and writes a line whenever
an object's state changes: flag word (+12; 0x1 remove, 0x100 = not updated), sequence number (+388), the next
sequence (+392), the flag word of its second part (+448+12), the layout id (+436) and the two HUD positions.
Also the free count and both control objects' prompt records (control object + 0x9F8: kind +4, object +8).

  python -I tools/own/pool_trace_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>
FROM=<frame> starts the log there (default 5000). POOL_N=18 for a patch with the twenty-first glue.
The last line is the lowest free count seen.
"""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
start = int(os.environ.get("FROM", "5000"))
N = int(os.environ.get("POOL_N", "9"))      # 18 with the twenty-first glue
STACK, COUNT = 896 * N, 896 * N + 4 * N
low = [N, 0]
p = Pine(int(sys.argv[2]), wait=120)
lines = []
last = {}
t0 = time.time()
n = 0


def w(data, o):
    return struct.unpack_from("<I", data, o)[0]


def rec(obj):
    if not 0x000F0000 <= obj < 0x02000000:
        return (0, 0, 0)
    c = p.r32(obj + 0xB44)
    if not 0x000F0000 <= c < 0x02000000:
        return (c, 0, 0)
    d = p.read(c + 0x9F8, 12)
    return (c + 0x9F8, w(d, 4), w(d, 8))


try:
    while time.time() - t0 < 900:
        try:
            fr = p.r32(0x0034D4BC)
        except RuntimeError:              # the game has not started yet
            time.sleep(0.3)
            continue
        if fr < start:
            time.sleep(0.2)
            continue
        m = p.r32(0x003486A4)
        if not 0x00100000 <= m < 0x02000000:
            time.sleep(0.05)
            continue
        data = p.read(m, COUNT + 4)
        fr2 = p.r32(0x0034D4BC)
        state = {"free": struct.unpack_from("<i", data, COUNT)[0]}
        if state["free"] < low[0]:
            low = [state["free"], fr]
        for i in range(N):
            o = 896 * i
            state["obj%d" % i] = "fl %04X seq %d next %d b404 %d part2 %04X id %d pos %d,%d" % (
                w(data, o + 12), struct.unpack_from("<i", data, o + 388)[0], struct.unpack_from("<i", data, o + 392)[0],
                data[o + 404], w(data, o + 448 + 12), w(data, o + 436),
                struct.unpack_from("<i", data, o + 368)[0], struct.unpack_from("<i", data, o + 372)[0])
        r1 = rec(p.r32(0x0034E948))
        r2 = rec(p.r32(0x000F05CC))
        state["rec1"] = "%08X kind %d obj %s" % (r1[0], r1[1], ("#%d" % ((r1[2] - m) // 896)) if r1[2] else "-")
        state["rec2"] = "%08X kind %d obj %s" % (r2[0], r2[1], ("#%d" % ((r2[2] - m) // 896)) if r2[2] else "-")
        for k, v in state.items():
            if last.get(k) != v:
                lines.append("f%d%s %s: %s" % (fr, "" if fr2 == fr else "+", k, v))
                last[k] = v
        n += 1
        if n % 200 == 0:
            pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r after %d samples" % (e, n))
lines.append("LOWEST free count %d at frame %d (pool of %d)" % (low[0], low[1], N))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
