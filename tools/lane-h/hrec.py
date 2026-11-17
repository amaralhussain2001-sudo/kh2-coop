"""Lane H recorder: who do the enemies target, and who gets hit? Read-only (PINE).

Once per video frame (as far as PINE keeps up) it reads: each hero's HP and position, and for every unit slot in use
by a non-player object: its HP and the object its owner currently targets (owner object + 0x9F4, the battle target
record that the AI's target search fills).

  python -I tools/lane-h/hrec.py <test-out-dir> <pinePort> <scanFrame> <endFrame> [--windows "name:f0-f1,..."]

At <scanFrame> the heroes are looked up once (hero = the engine's player 0x0034E948, twin = lane E's pointer
0x000F05CC). Output: <test-out-dir>/hrec.csv and a summary per window:
  frames sampled; each hero's HP at start and end and the number of times it dropped (= hits taken);
  on average how many enemies target the hero / the twin / something else; enemy HP total at start and end;
  the distance between the heroes at start and end.
"""
import math
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

SLOT1, STEP, NSLOT = 0x01C6C750, 0x268, 24
G_PLAYER, V_TWIN = 0x0034E948, 0x000F05CC
TARGET_OFF = 0x9F4


def frame(p):
    return p.r32(0x0034D4BC) + 152


def pos(p, obj):
    b = p.read(obj + 0x70, 12)
    return struct.unpack("<3f", b)


def main():
    out = pathlib.Path(sys.argv[1])
    port, scan_f, end_f = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    windows = []
    if "--windows" in sys.argv:
        for item in sys.argv[sys.argv.index("--windows") + 1].split(","):
            name, _, rng = item.partition(":")
            a, b = rng.split("-")
            windows.append((name, int(a), int(b)))
    out.mkdir(parents=True, exist_ok=True)
    p = Pine(port, wait=120)
    t0 = time.time()
    while True:
        try:
            if frame(p) >= scan_f and p.r32(G_PLAYER):
                break
        except Exception:  # noqa: BLE001
            pass
        if time.time() - t0 > 600:
            sys.exit("timeout waiting for frame %d" % scan_f)
        time.sleep(0.02)
    hero, twin = p.r32(G_PLAYER), p.r32(V_TWIN)
    hs = p.r32(hero + 0x48C)
    ts = p.r32(twin + 0x48C) if twin else 0
    print("hero %07X slot %08X | twin %s slot %08X" % (hero, hs, ("%07X" % twin) if twin else "none", ts))
    rows, last = [], -1
    friends, last_tg, switches = {}, {}, []
    base = SLOT1 - STEP * (NSLOT - 1)
    while True:
        try:
            f = frame(p)
            if f >= end_f:
                break
            if f == last:
                continue
            last = f
            if p.r32(G_PLAYER) != hero:
                print("frame %d: the engine's player changed (room change or defeat); recording stops" % f)
                break
            pool = p.read(base, STEP * NSLOT)
            hhp = struct.unpack_from("<i", pool, hs - base)[0] if base <= hs < base + STEP * NSLOT else p.r32(hs)
            thp = (struct.unpack_from("<i", pool, ts - base)[0] if base <= ts < base + STEP * NSLOT else p.r32(ts)) if ts else 0
            hx, hy, hz = pos(p, hero)
            tx, ty, tz = pos(p, twin) if twin else (0.0, 0.0, 0.0)
            n_h = n_t = n_o = n_none = 0
            ehp = 0
            for k in range(NSLOT):
                b = pool[k * STEP:(k + 1) * STEP]
                hp = struct.unpack_from("<i", b, 0)[0]
                flags, sid, ref, owner = struct.unpack_from("<IiiI", b, 0x250)
                a = base + k * STEP
                if a in (hs, ts) or not owner:
                    continue
                if sid != -1:
                    # a party member (Donald, Goofy, a guest): where does it stand?
                    fx, fy, fz = pos(p, owner)
                    fr = friends.setdefault(sid, [0, 0.0, 0.0, 0])
                    fr[0] += 1
                    fr[1] += math.hypot(fx - hx, fz - hz)
                    fr[2] += math.hypot(fx - tx, fz - tz)
                    ftg = p.r32(owner + TARGET_OFF)
                    if ftg in (hero, twin) and ftg:
                        fr[3] += 1
                    continue
                if not (0 < hp < 100000):
                    continue
                ehp += hp
                tg = p.r32(owner + TARGET_OFF)
                if tg == hero:
                    n_h += 1
                    cur = "H"
                elif twin and tg == twin:
                    n_t += 1
                    cur = "T"
                elif tg == 0:
                    n_none += 1
                    cur = None
                else:
                    n_o += 1
                    cur = None
                if cur:
                    prev = last_tg.get(owner)
                    if prev and prev != cur:
                        switches.append((f, owner, prev, cur))
                    last_tg[owner] = cur
            rows.append((f, hhp, thp, hx, hz, tx, tz, n_h, n_t, n_o, n_none, ehp))
        except Exception as e:  # noqa: BLE001
            print("recording stopped:", e)
            break
    with open(out / "hrec.csv", "w") as fh:
        fh.write("frame,hero_hp,twin_hp,hero_x,hero_z,twin_x,twin_z,enemies_on_hero,enemies_on_twin,enemies_on_other,enemies_no_target,enemy_hp\n")
        for r in rows:
            fh.write("%d,%d,%d,%.0f,%.0f,%.0f,%.0f,%d,%d,%d,%d,%d\n" % r)
    print("recorded %d frames (%d..%d)" % (len(rows), rows[0][0] if rows else 0, rows[-1][0] if rows else 0))
    print("target switches between the heroes: %d in %d frames, by %d enemies" % (
        len(switches), len(rows), len({s[1] for s in switches})))
    for s in switches[:12]:
        print("   frame %d enemy %07X %s -> %s" % s)
    for sid, fr in sorted(friends.items()):
        print("party member (status id %d): %d samples, average distance to the hero %.0f, to the twin %.0f; frames with a hero as its target: %d" % (
            sid, fr[0], fr[1] / fr[0], fr[2] / fr[0], fr[3]))
    if not windows and rows:
        windows = [("all", rows[0][0], rows[-1][0] + 1)]
    for name, a, b in windows:
        w = [r for r in rows if a <= r[0] < b]
        if not w:
            print("window %-10s %d-%d: no samples" % (name, a, b))
            continue
        drops = lambda i: sum(1 for x, y in zip(w, w[1:]) if y[i] < x[i])  # noqa: E731
        avg = lambda i: sum(r[i] for r in w) / len(w)  # noqa: E731
        d0 = math.hypot(w[0][3] - w[0][5], w[0][4] - w[0][6])
        d1 = math.hypot(w[-1][3] - w[-1][5], w[-1][4] - w[-1][6])
        print("window %-10s %5d-%5d: %4d frames | hero HP %d->%d (%d hits) | twin HP %d->%d (%d hits) | "
              "enemies targeting hero %.1f / twin %.1f / other %.1f / none %.1f | enemy HP %d->%d | heroes apart %.0f->%.0f" % (
                  name, a, b, len(w), w[0][1], w[-1][1], drops(1), w[0][2], w[-1][2], drops(2),
                  avg(7), avg(8), avg(9), avg(10), w[0][11], w[-1][11], d0, d1))


if __name__ == "__main__":
    main()
