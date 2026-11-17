"""Lane K: list the game's per-frame task lists of a running sandbox emulator (read-only, through PINE).

Waits for the screenshot of <frame> in <test-out-dir>, then walks the main scheduler's linked list and the
schedulers of the running "scene" objects (the nested lists where the game's own update and draw tasks live).
  python -I tools/lane-k/tasks.py <test-out-dir> <port> <frame> [<outfile>]
Task record (0x48 bytes): +0x00 function, +0x24 scheduler, +0x28 flags, +0x2C priority, +0x34 coroutine block,
+0x38 next, +0x3C previous.  Scheduler: +0x08 first task, +0x0C last task.  Main scheduler pointer: 0x0032B91C.
Scene list: head 0x0038AA40, next at +0x0C, scheduler at +0x04, state at +0x1C.
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
    if time.time() - t0 > 600:
        sys.exit("timeout waiting for " + shot.name)
    time.sleep(0.05)
p = Pine(port)
lines = []


def walk(sched, indent):
    t = p.r32(sched + 8) if sched else 0
    n = 0
    while t and n < 400:
        func, flags, prio, co, nxt = p.r32(t), p.r32(t + 0x28), p.r32(t + 0x2C), p.r32(t + 0x34), p.r32(t + 0x38)
        lines.append(f"{indent}task 0x{t:08X}  prio {prio:>10d} (0x{prio:08X})  flags 0x{flags:08X}  func 0x{func:08X}  co 0x{co:08X}")
        t = nxt
        n += 1
    lines.append(f"{indent}{n} tasks")


sched = p.r32(0x0032B91C)
lines.append(f"main scheduler: pointer at 0x0032B91C -> 0x{sched:08X}")
walk(sched, "  ")
scene = p.r32(0x0038AA40)
k = 0
while scene and k < 20:
    sc, nxt, state, vt = p.r32(scene + 4), p.r32(scene + 0xC), p.r32(scene + 0x1C), p.r32(scene)
    lines.append(f"scene 0x{scene:08X}  class table 0x{vt:08X}  state {state}  scheduler 0x{sc:08X}")
    walk(sc, "    ")
    scene = nxt
    k += 1
text = chr(10).join(lines)
print(text)
if outfile:
    pathlib.Path(outfile).write_text(text + chr(10))
