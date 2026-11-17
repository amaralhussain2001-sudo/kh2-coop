"""How often does the game update a moving character's position? (30 or 60 times per second at normal speed)

Polls one float as fast as PINE allows and prints the time gaps between value changes while it is moving.
Run the emulator at speed 1.  python -I tools/lane-b/pollrate.py <port> <hexaddr> <seconds>
"""
import statistics
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

p = Pine(int(sys.argv[1]), wait=120)
addr = int(sys.argv[2], 16)
secs = float(sys.argv[3])
t0 = time.perf_counter()
last, last_t, gaps, polls = None, None, [], 0
while time.perf_counter() - t0 < secs:
    try:
        v = p.r32(addr)
    except Exception:  # noqa: BLE001
        time.sleep(0.05)
        continue
    polls += 1
    now = time.perf_counter()
    if last is not None and v != last:
        if last_t is not None and now - last_t < 0.2:
            gaps.append((now - last_t) * 1000)
        last_t = now
    last = v
print(f"polls {polls} ({polls / secs:.0f} per second), value changes with a gap under 200 ms: {len(gaps)}")
if gaps:
    gaps.sort()
    print(f"gap between changes: median {statistics.median(gaps):.1f} ms, 10% {gaps[len(gaps) // 10]:.1f} ms, 90% {gaps[len(gaps) * 9 // 10]:.1f} ms")
    b16 = sum(1 for g in gaps if g < 25)
    b33 = sum(1 for g in gaps if 25 <= g < 50)
    print(f"gaps near 16.7 ms: {b16}, near 33.3 ms: {b33}, longer: {len(gaps) - b16 - b33}")
