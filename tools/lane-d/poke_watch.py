"""Lane D, ONE-copy experiments only (it WRITES game memory through PINE; never use on a linked pair).

Waits until the fight has both hero slots (slot 2 marked as the second hero's), then keeps writing the given
values for the rest of the run, and logs the two hero slots like slots.py.

  python -I tools/lane-d/poke_watch.py <port> <seconds> <outfile> [--after S] ADDR=VALUE|ADDR=@P1|ADDR=@P2 ...
@P1 / @P2 = the owner object of hero slot 1 / of the marked slot (read at run time).
SLOT1.HP=n / SLOT2.HP=n style is also accepted: S1+OFF=VALUE, S2+OFF=VALUE (offset hex, written once unless --hold).
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0] + "/../lane-b")
from pine import Pine  # noqa: E402

SLOT1, STEP = 0x01C6C750, 0x268


def main():
    port, secs, outp = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    args = sys.argv[4:]
    after = 2.0
    hold = "--hold" in args
    if "--after" in args:
        after = float(args[args.index("--after") + 1])
    pokes = [a for a in args if "=" in a]
    out = open(outp, "w")

    def say(s):
        print(s, flush=True)
        out.write(s + "\n")
        out.flush()

    p = Pine(port)
    t0, seen_at, done_once, last = time.time(), None, False, None
    while time.time() - t0 < secs:
        try:
            s1 = p.read(SLOT1, STEP)
            s2 = p.read(SLOT1 - STEP, STEP)
            f2, id2 = struct.unpack_from("<Ii", s2, 0x250)
            id1 = struct.unpack_from("<i", s1, 0x254)[0]
            o1 = struct.unpack_from("<I", s1, 0x25C)[0]
            o2 = struct.unpack_from("<I", s2, 0x25C)[0]
            both = id1 in (1, 14) and id2 in (1, 14) and (f2 & 0x80000000)
            if both and seen_at is None:
                seen_at = time.time()
                say(f"{time.time() - t0:7.2f}s both hero slots present: P1 object {o1:08X}, second hero object {o2:08X}")
            if both and time.time() - seen_at >= after and (hold or not done_once or True):
                for pk in pokes:
                    a, v = pk.split("=")
                    once = False
                    if a.startswith("S1+") or a.startswith("S2+"):
                        addr = (SLOT1 if a[1] == "1" else SLOT1 - STEP) + int(a[3:], 16)
                        once = not hold
                    else:
                        addr = int(a, 16)
                        once = not hold
                    val = o1 if v == "@P1" else o2 if v == "@P2" else int(v, 0)
                    if once and done_once:
                        continue
                    p.w32(addr, val)
                if not done_once:
                    say(f"{time.time() - t0:7.2f}s wrote: {' '.join(pokes)}")
                done_once = True
            hp1, mx1 = struct.unpack_from("<ii", s1, 0)
            hp2, mx2 = struct.unpack_from("<ii", s2, 0)
            st1 = struct.unpack_from("<4h", s1, 0x188)
            st2 = struct.unpack_from("<4h", s2, 0x188)
            mp1, mm1 = struct.unpack_from("<ii", s1, 0x180)
            mp2, mm2 = struct.unpack_from("<ii", s2, 0x180)
            rec = struct.unpack_from("<I", s1, 0x244)[0]
            lvl = p.read(rec + 0xF, 1)[0] if 0x00100000 <= rec < 0x02000000 else -1
            sv = p.read(0x0032D98E, 2)
            exp = p.r32(0x0032F210)
            room = p.r32(0x0032BAE0) & 0xFFFF
            state = (hp1, mx1, hp2, mx2, id1, id2, f2 >> 31, p.r32(0x01C6CAB8), st1, st2, mp1, mm1, mp2, mm2, lvl, sv[0], sv[1], exp, room)
        except Exception as e:  # noqa: BLE001
            say(f"{time.time() - t0:7.2f}s read error {e}")
            time.sleep(1)
            continue
        if state != last:
            last = state
            say(f"{time.time() - t0:7.2f}s room {room:04X} P1 id {id1} HP {hp1}/{mx1} MP {mp1}/{mm1} st {st1} | slot2 id {id2} mark {f2 >> 31} HP {hp2}/{mx2} MP {mp2}/{mm2} st {st2} | lvl {lvl} exp {exp} saveHP {sv[0]} saveMP1 {sv[1]} free {state[7]}")
        time.sleep(0.1)


if __name__ == "__main__":
    main()
