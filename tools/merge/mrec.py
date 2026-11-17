"""Merge lane: light recorder for fight / magic tests. Read-only (PINE).

Polls, once per video frame as far as PINE keeps up: each hero's action (object+0x154), each hero's HP and MP (its
unit slot), and the summed HP of the enemy slots. Frames are the session's frames, taken from the game's own
counter (0x0034D4BC + 152, lane G's finding), so no screenshots are needed.

  python -I tools/merge/mrec.py <test-out-dir> <pinePort> <scanFrame> <endFrame> --windows "name:f0-f1,name:f0-f1"

At <scanFrame> the player objects are looked up once (hero = the engine's player, twin = lane E's twin pointer).
Output: <test-out-dir>/rec.csv and a summary per window: sampled frames, frames each hero spent attacking /
casting / guarding, each hero's HP and MP at the start and end, enemy HP at the start and end.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402
from mprobe import find_players, SLOT1, STEP, POOL  # noqa: E402

ATTACK = set(range(0x97, 0x9B)) | set(range(0xB5, 0xB8))
CAST = {0x38, 0x3B, 0x3E}
GUARD = {0xAD, 0xD1}


def frame(p):
    return p.r32(0x0034D4BC) + 152


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
            if frame(p) >= scan_f and p.r32(0x0034E948):
                break
        except Exception:  # noqa: BLE001
            pass
        if time.time() - t0 > 600:
            sys.exit("timeout waiting for frame %d" % scan_f)
        time.sleep(0.02)
    gp, tw = p.r32(0x0034E948), p.r32(0x000F05CC)
    objs = {a: b for a, b in find_players(p)}
    hero = gp if gp in objs else None
    twin = tw if tw in objs else None
    if hero is None:
        sys.exit("no engine player object found")
    hs = struct.unpack_from("<I", objs[hero], 0x48C)[0]
    ts = struct.unpack_from("<I", objs[twin], 0x48C)[0] if twin else 0
    print("hero %07X slot %08X ctl %08X | twin %s slot %08X ctl %08X" % (
        hero, hs, struct.unpack_from("<I", objs[hero], 0xB3C)[0], ("%07X" % twin) if twin else "none", ts,
        struct.unpack_from("<I", objs[twin], 0xB3C)[0] if twin else 0))
    rows, last = [], -1
    while True:
        try:
            f = frame(p)
            if f >= end_f:
                break
            if f == last:
                continue
            last = f
            ha = p.r32(hero + 0x154)
            ta = p.r32(twin + 0x154) if twin else 0
            hhp, hmp = p.r32(hs), p.r32(hs + 0x180)
            thp, tmp = (p.r32(ts), p.r32(ts + 0x180)) if ts else (0, 0)
            pool = p.read(SLOT1 - STEP * 11, STEP * 12)
            en = 0
            for k in range(12):
                b = pool[k * STEP:(k + 1) * STEP]
                sid = struct.unpack_from("<i", b, 0x254)[0]
                owner = struct.unpack_from("<I", b, 0x25C)[0]
                hp = struct.unpack_from("<i", b, 0)[0]
                if sid == -1 and owner and 0 < hp < 100000:
                    en += hp
            rows.append((f, ha, ta, hhp, hmp, thp, tmp, en))
        except Exception:  # noqa: BLE001
            break
    with open(out / "rec.csv", "w") as fh:
        fh.write("frame,hero_action,twin_action,hero_hp,hero_mp,twin_hp,twin_mp,enemy_hp\n")
        for r in rows:
            fh.write("%d,%X,%X,%d,%d,%d,%d,%d\n" % r)
    print("recorded %d frames (%d..%d)" % (len(rows), rows[0][0] if rows else 0, rows[-1][0] if rows else 0))
    for name, a, b in windows:
        w = [r for r in rows if a <= r[0] < b]
        if not w:
            print("window %-10s %d-%d: no samples" % (name, a, b))
            continue
        cnt = lambda idx, s: sum(1 for r in w if r[idx] in s)  # noqa: E731
        print("window %-10s %5d-%5d: %3d frames | hero attack %3d cast %2d guard %2d | twin attack %3d cast %2d guard %2d | "
              "hero HP %d->%d MP %d->%d | twin HP %d->%d MP %d->%d | enemy HP %d->%d" % (
                  name, a, b, len(w), cnt(1, ATTACK), cnt(1, CAST), cnt(1, GUARD), cnt(2, ATTACK), cnt(2, CAST), cnt(2, GUARD),
                  w[0][3], w[-1][3], w[0][4], w[-1][4], w[0][5], w[-1][5], w[0][6], w[-1][6], w[0][7], w[-1][7]))


if __name__ == "__main__":
    main()
