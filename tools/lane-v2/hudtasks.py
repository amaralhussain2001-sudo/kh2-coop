"""Lane V2: list the 2D layer managers of a running sandbox emulator (read-only, through PINE).

Manager n at 0x00347EA0 + n*0x70: +0x00 inner scheduler, +0x04 first 2D object (next at object+4),
+0x14 owner, +0x20 a 4x4 matrix. Prints the inner task list (function, priority, argument) and the object list
(class table, flags, a few words).
  python -I tools/lane-v2/hudtasks.py <test-out-dir> <port> <frame> [<outfile>]
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

out_dir = pathlib.Path(sys.argv[1])
port = int(sys.argv[2])
frame = int(sys.argv[3])
outfile = sys.argv[4] if len(sys.argv) > 4 else None
shot = out_dir / f"p1_f{frame:06d}.png"
t0 = time.time()
while not shot.exists():
    if time.time() - t0 > 900:
        sys.exit("timeout waiting for " + shot.name)
    time.sleep(0.05)
p = Pine(port)
L = []
L.append("current manager pointer 0x00347F80 = 0x%08X, saved 0x00347F84 = 0x%08X" % (p.r32(0x00347F80), p.r32(0x00347F84)))
L.append("command menu display pointer 0x003484A0 = 0x%08X" % p.r32(0x003484A0))
for n in range(2):
    m = 0x00347EA0 + n * 0x70
    sched = p.r32(m)
    L.append("manager %d at 0x%08X: scheduler 0x%08X first object 0x%08X +8 0x%08X +C 0x%08X +10 0x%08X owner 0x%08X" % (
        n, m, sched, p.r32(m + 4), p.r32(m + 8), p.r32(m + 0xC), p.r32(m + 0x10), p.r32(m + 0x14)))
    t = p.r32(sched + 8) if sched else 0
    k = 0
    while t and k < 300:
        func, arg, flags, prio, f30, nxt = p.r32(t), p.r32(t + 4), p.r32(t + 0x28), p.r32(t + 0x2C), p.r32(t + 0x30), p.r32(t + 0x38)
        L.append("    task 0x%08X prio %8d func 0x%08X arg 0x%08X flags 0x%X end-func 0x%08X" % (t, prio, func, arg, flags, f30))
        t = nxt
        k += 1
    L.append("    %d tasks" % k)
    o = p.r32(m + 4)
    k = 0
    while o and k < 300:
        words = [p.r32(o + 4 * i) for i in range(12)]
        L.append("    object 0x%08X class 0x%08X next 0x%08X  +8.. %s" % (o, words[0], words[1], " ".join("%08X" % w for w in words[2:])))
        o = words[1]
        k += 1
    L.append("    %d objects" % k)
text = "\n".join(L)
if outfile:
    pathlib.Path(outfile).write_text(text + "\n")
print(text)
