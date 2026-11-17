"""Lane V2 experiment (ONE-copy tests only: it writes memory): put the twin into party slot <n> of the HUD's
party table (0x00348638) and raise that slot's "changed" flag, to see what a friend gauge shows for it.

  python -I tools/lane-v2/poke_party.py <test-out-dir> <port> <frame> <slot> [<out.txt>]
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

out_dir, port, frame, slot = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
outfile = sys.argv[5] if len(sys.argv) > 5 else None
shot = out_dir / f"p1_f{frame:06d}.png"
t0 = time.time()
while not shot.exists():
    if time.time() - t0 > 900:
        sys.exit("timeout")
    time.sleep(0.05)
p = Pine(port)
T = 0x00348638
twin = p.r32(0x000F05CC)
L = ["twin object 0x%08X" % twin]
L.append("party table before: " + " ".join("%08X" % p.r32(T + 4 * i) for i in range(6)))
L.append("gauge pointers 3485E8.. " + " ".join("%08X" % p.r32(0x003485E8 + 4 * i) for i in range(6)))
if twin:
    p.w32(T + 4 * slot, twin)
    p.w32(T + 0xC + 4 * slot, p.r32(T + 0xC + 4 * slot) | 1)
time.sleep(1.0)
L.append("party table after:  " + " ".join("%08X" % p.r32(T + 4 * i) for i in range(6)))
for name, g in (("friend A", p.r32(0x003485F0)), ("friend B", p.r32(0x003485F4)), ("player", p.r32(0x003485EC))):
    if g:
        L.append("%s gauge 0x%08X: +0C %08X +10 %X +18 %X +1C %X +20 %08X +24 %d +28 %d +2C %d +30 %d +34 %08X" % (
            name, g, p.r32(g + 0xC), p.r32(g + 0x10), p.r32(g + 0x18), p.r32(g + 0x1C), p.r32(g + 0x20),
            p.r32(g + 0x24), p.r32(g + 0x28), p.r32(g + 0x2C), p.r32(g + 0x30), p.r32(g + 0x34)))
text = "\n".join(L)
if outfile:
    pathlib.Path(outfile).write_text(text + "\n")
print(text)
