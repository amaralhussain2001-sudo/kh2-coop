"""ONE-copy test helper: when the fight in the given room has started, set the shared HP (unit slot 1) to a value,
then print HP / battle state / room changes for a while. Uses a PINE memory WRITE: never use on a linked pair.

  python -I tools/lane-b/sethp.py <port> <roomhex e.g. 0904> <hp> <seconds> [--wait S] [--hold]
--wait S  seconds to wait after the battle flag turns on before writing (default 1.0)
--hold    keep rewriting the value every poll (makes the next hit lethal no matter what heals happen)
"""
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from pine import Pine  # noqa: E402

port, room, hp, secs = int(sys.argv[1]), int(sys.argv[2], 16), int(sys.argv[3]), float(sys.argv[4])
wait = float(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 1.0
SLOT1, BTL, NOW = 0x01C6C750, 0x01C61958, 0x0032BAE0
p = Pine(port)
t0 = time.time()
armed_at, written, last = None, False, None
while time.time() - t0 < secs:
    try:
        now, btl, cur = p.r16(NOW), p.r8(BTL), p.r32(SLOT1)
        if not written and now == room and btl != 0 and cur != 0:
            if armed_at is None:
                armed_at = time.time()
            elif time.time() - armed_at >= wait:
                p.w32(SLOT1, hp)
                written = True
                print(f"{time.time() - t0:6.2f}s wrote HP {hp} (was {cur})", flush=True)
        state = (now, btl, cur, p.r16(NOW + 4))
        if state != last:
            print(f"{time.time() - t0:6.2f}s room {now:04X} prog {state[3]:02X} battle {btl} hp {cur}", flush=True)
            last = state
    except Exception:  # noqa: BLE001
        time.sleep(0.1)
    time.sleep(0.02)
