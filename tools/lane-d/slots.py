"""Lane D: watch the unit slots (HP/MP records) of a running sandbox emulator through PINE. Read-only.

  python -I tools/lane-d/slots.py <port> <seconds> [--n 12] [--interval 0.25] [--out file]

Prints one block whenever anything in the first N slots changes: slot number (1 = 0x01C6C750, going down by
0x268), status id, HP/max, MP/max, flag word, reference count, owner object, record pointer.
Also prints the room (0x0032BAE0) and the battle flag (0x01C61958).
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0] + "/../lane-b")
from pine import Pine  # noqa: E402

SLOT1, STEP = 0x01C6C750, 0x268
FREE_CNT, FREE_LIST, POOL = 0x01C6CAB8, 0x01C6C9B8, 0x01C62FB8


def main():
    port, secs = int(sys.argv[1]), float(sys.argv[2])
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 12
    interval = float(sys.argv[sys.argv.index("--interval") + 1]) if "--interval" in sys.argv else 0.25
    out = open(sys.argv[sys.argv.index("--out") + 1], "w") if "--out" in sys.argv else None

    def say(s):
        print(s, flush=True)
        if out:
            out.write(s + "\n")
            out.flush()

    p = Pine(port)
    t0, last = time.time(), None
    while time.time() - t0 < secs:
        try:
            now = p.r32(0x0032BAE0) & 0xFFFF
            btl = p.r32(0x01C61958) & 0xFF
            cnt = p.r32(FREE_CNT)
            free = set()
            if 0 <= cnt <= 64:
                fl = p.read(FREE_LIST, 4 * 64)
                free = set(struct.unpack("<64i", fl)[:cnt])
            rows = []
            for k in range(n):
                a = SLOT1 - STEP * k
                idx = (a - POOL) // STEP
                if idx in free:
                    continue
                b = p.read(a, STEP)
                hp, mx = struct.unpack_from("<ii", b, 0)
                mp, mmx = struct.unpack_from("<ii", b, 0x180)
                rec, form = struct.unpack_from("<II", b, 0x244)
                flags, sid, ref, owner, sv = struct.unpack_from("<IiiII", b, 0x250)
                st = struct.unpack_from("<4h", b, 0x188)
                lvl = rhp = -1
                if 0x00100000 <= rec < 0x02000000 or 0x000F0000 <= rec < 0x00100000:
                    rb = p.read(rec, 0x10)
                    lvl, rhp = rb[0xF], rb[4]
                rows.append((k + 1, sid, hp, mx, mp, mmx, flags, ref, owner, rec, st, lvl, rhp))
            state = (now, btl, tuple(rows))
        except Exception as e:  # noqa: BLE001
            say(f"{time.time() - t0:7.2f}s read error {e}")
            time.sleep(1)
            continue
        if state != last:
            last = state
            say(f"{time.time() - t0:7.2f}s room {now:04X} battle {btl} free {cnt}")
            for k, sid, hp, mx, mp, mmx, flags, ref, owner, rec, st, lvl, rhp in rows:
                say(f"      slot {k:2d} id {sid:5d} HP {hp:4d}/{mx:<4d} MP {mp:3d}/{mmx:<3d} flags {flags:08X} ref {ref} owner {owner:08X} rec {rec:08X} stats {st[0]},{st[1]},{st[2]},{st[3]} lvl {lvl} recHP {rhp}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
