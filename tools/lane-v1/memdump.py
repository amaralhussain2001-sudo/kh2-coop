"""Lane V1: wait until a frame, then dump memory ranges of a running sandbox emulator (PINE, read-only) as hex words.

  python -I tools/lane-v1/memdump.py <port> <frame> <outFile> <addrHex:lenHex> [<addrHex:lenHex> ...]
Each range is printed as 64-bit words (address: low32 high32 = the way GS packets are read), four words per qword line.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

port, at, out = int(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
ranges = [(int(a.split(":")[0], 16), int(a.split(":")[1], 16)) for a in sys.argv[4:]]
p = Pine(port, wait=120)
t0 = time.time()
while True:
    try:
        f = p.r32(0x0034D4BC) + 152
    except Exception:  # noqa: BLE001
        time.sleep(0.05)
        if time.time() - t0 > 900:
            sys.exit("no emulator")
        continue
    if f >= at:
        break
    time.sleep(0.01)
lines = ["frame %d" % f]
for addr, ln in ranges:
    data = p.read(addr, ln)
    lines.append("== %08X + %X" % (addr, ln))
    for o in range(0, ln, 16):
        w = struct.unpack_from("<4I", data.ljust(o + 16, b"\0"), o)
        lines.append("%08X: %08X %08X  %08X %08X" % ((addr + o,) + w))
out.write_text("\n".join(lines) + "\n")
print("dumped at frame %d -> %s" % (f, out))
