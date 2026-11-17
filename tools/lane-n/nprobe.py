"""Lane N probe: follow the heroes and friends (unit slots with status id 1..15) of a running sandbox emulator.

  python -I tools/lane-n/nprobe.py <outfile> <pinePort> <startFrame> <endFrame> [--every N]
         [--sethp WHO=HP@FRAME,...] [--setmp WHO=MP@FRAME,...] [--extra HEXADDR,...]

WHO = hero | twin | sid2 | sid3 (Donald, Goofy) | sidN.  --sethp / --setmp WRITE memory: ONE-copy tests only.
Frames are session frames (the game's counter 0x0034D4BC + 152).
A line is written whenever something other than a running timer changes. Columns per unit:
  role/sid  slot  HP/max  MP  object  flags(+0x7F8)  action(+0x154)  timer
The timer shown is the friend's own (+0xB40) for friends and lane N's variables for the heroes.
"""
import pathlib
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "merge"))
from pine import Pine  # noqa: E402

POOL, STEP, NSLOT = 0x01C62FB8, 0x268, 64
G_PLAYER, V_TWIN = 0x0034E948, 0x000F05CC
N_VARS = 0x000F2FC0   # lane N variables (see make_down.py)


def frame(p):
    return p.r32(0x0034D4BC) + 152


def parse_sets(arg):
    res = []
    if not arg:
        return res
    for item in arg.split(","):
        who, _, rest = item.partition("=")
        val, _, fr = rest.partition("@")
        res.append([who, int(val), int(fr), False])
    return res


def units(p):
    pool = p.read(POOL, STEP * NSLOT)
    gp, tw = p.r32(G_PLAYER), p.r32(V_TWIN)
    res = []
    for k in range(NSLOT):
        b = pool[k * STEP:(k + 1) * STEP]
        sid = struct.unpack_from("<i", b, 0x254)[0]
        owner = struct.unpack_from("<I", b, 0x25C)[0]
        refs = struct.unpack_from("<i", b, 0x258)[0]
        if not (1 <= sid <= 15) or not owner or refs <= 0:
            continue
        addr = POOL + k * STEP
        hp, mhp = struct.unpack_from("<ii", b, 0)
        mp = struct.unpack_from("<i", b, 0x180)[0]
        mark = struct.unpack_from("<I", b, 0x250)[0] >> 31
        role = "hero" if owner == gp else ("twin" if owner == tw else "sid%d" % sid)
        res.append(dict(role=role, sid=sid, slot=addr, hp=hp, mhp=mhp, mp=mp, owner=owner, mark=mark))
    return res


def main():
    out = pathlib.Path(sys.argv[1])
    port, f0, f1 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 4
    sethp = parse_sets(sys.argv[sys.argv.index("--sethp") + 1]) if "--sethp" in sys.argv else []
    setmp = parse_sets(sys.argv[sys.argv.index("--setmp") + 1]) if "--setmp" in sys.argv else []
    extra = [int(x, 16) for x in sys.argv[sys.argv.index("--extra") + 1].split(",")] if "--extra" in sys.argv else []
    p = Pine(port, wait=180)
    t0 = time.time()
    while True:
        try:
            if frame(p) >= f0:
                break
        except Exception:  # noqa: BLE001
            pass
        if time.time() - t0 > 900:
            sys.exit("timeout")
        time.sleep(0.02)
    posq = float(sys.argv[sys.argv.index("--pos") + 1]) if "--pos" in sys.argv else 0.0
    tps = []   # --tp WHO>TARGET@FRAME[+N[:DX]]: for N samples write WHO's position = TARGET's + DX units in x (default 60)
    if "--tp" in sys.argv:
        for item in sys.argv[sys.argv.index("--tp") + 1].split(","):
            pair, _, fr = item.partition("@")
            who, _, tgt = pair.partition(">")
            fr, _, n = fr.partition("+")
            n, _, dx = n.partition(":")
            tps.append([who, tgt, int(fr), int(n) if n else 12, False, float(dx) if dx else 60.0])
    lines, lastkey, lastf = [], None, -1
    want_att, seen_att = "--attacks" in sys.argv, set()
    seen_thr = {}
    with open(out, "w", encoding="utf-8") as fh:
        try:
            bt = p.r32(0x00352130)
            fh.write("battle table %08X: +54 %.3f +58 %.3f +5C %.3f | dt %.5f\n" % (bt, p.rf(bt + 0x54), p.rf(bt + 0x58), p.rf(bt + 0x5C), p.rf(0x00349E10)))
            for u in units(p):
                o = u["owner"]
                pp = p.r32(o + 0x12C)
                fh.write("params %s obj %07X class %08X +12C %08X [+18] %.3f [+1C] %.3f slot+228 %.3f slot+1DC %08X flags588 %08X\n" % (
                    u["role"], o, p.r32(o), pp, p.rf(pp + 0x18) if pp else -1, p.rf(pp + 0x1C) if pp else -1,
                    p.rf(u["slot"] + 0x228), p.r32(u["slot"] + 0x1DC), p.r32(o + 0x588)))
        except Exception as e:  # noqa: BLE001
            fh.write("(params read error %s)\n" % e)
        while True:
            try:
                f = frame(p)
            except Exception:  # noqa: BLE001
                break
            if f >= f1:
                break
            if f == lastf or f % every:
                continue
            lastf = f
            try:
                us = units(p)
                for group, off in ((sethp, 0), (setmp, 0x180)):
                    for s in group:
                        if not s[3] and f >= s[2]:
                            for u in us:
                                if u["role"] == s[0] or ("sid%d" % u["sid"] == s[0] and u["role"].startswith("sid")):
                                    p.w32(u["slot"] + off, s[1])
                                    s[3] = True
                                    fh.write("%6d  WRITE %s %s = %d (slot %08X)\n" % (f, "HP" if off == 0 else "MP", s[0], s[1], u["slot"]))
                for t in tps:   # ONE-copy test write: put WHO beside TARGET for a few samples
                    if t[2] <= f < t[2] + t[3]:
                        byrole = {u["role"]: u["owner"] for u in us}
                        byrole.update({"sid%d" % u["sid"]: u["owner"] for u in us if u["role"].startswith("sid")})
                        if t[0] in byrole and t[1] in byrole:
                            x, y, z = struct.unpack("<3f", p.read(byrole[t[1]] + 0x70, 12))
                            for off in (0x70, 0x540, 0x590, 0x5C0, 0x6E0, 0x720, 0x730, 0x840):
                                p.wf(byrole[t[0]] + off, x + t[5])
                                p.wf(byrole[t[0]] + off + 4, y)
                                p.wf(byrole[t[0]] + off + 8, z)
                            if not t[4]:
                                t[4] = True
                                fh.write("%6d  WRITE position of %s = beside %s (%.0f, %.0f, %.0f)\n" % (f, t[0], t[1], x + t[5], y, z))
                if want_att:   # read-only: attack objects (list head 0x01C60CD8, next at +0xC0) seen for the first time
                    a, n, now = p.r32(0x01C60CD8), 0, set()
                    while a and n < 64:
                        blk = p.read(a, 0xC4)
                        own, own2, grp, num, data = struct.unpack_from("<IIIII", blk, 8)[0], struct.unpack_from("<I", blk, 0xC)[0], struct.unpack_from("<I", blk, 0x14)[0], struct.unpack_from("<I", blk, 0x18)[0], struct.unpack_from("<I", blk, 0x28)[0]
                        now.add(a)
                        if a not in seen_att:
                            typ = p.r8(data + 4) if data else -1
                            names = {u["owner"]: u["role"] for u in us}
                            fh.write("%6d  ATTACK %07X owner %s group %X number %X type %d" % (f, a, names.get(own2, "%07X" % own2), grp, num, typ) + chr(10))
                        a = struct.unpack_from("<I", blk, 0xC0)[0]
                        n += 1
                    for gone in sorted(seen_att - now):
                        fh.write("%6d  ATTACK %07X gone" % (f, gone) + chr(10))
                    seen_att.clear()
                    seen_att.update(now)
                room = p.r16(0x0032BAE0)
                btl = p.r32(0x01C61958)
                go = p.r32(0x00350DF0)
                nv = p.read(N_VARS, 0x20)
                key, txt = [room, btl, go != 0], []
                for u in us:
                    o = u["owner"]
                    flags = p.r32(o + 0x7F8)
                    act = p.r32(o + 0x154)
                    cls = p.r32(o)
                    tm = p.rf(o + 0xB40) if cls != 0x00352410 else None
                    px, py, pz = struct.unpack("<3f", p.read(o + 0x70, 12))
                    key.append((u["role"], u["slot"], u["hp"], u["mhp"], u["mp"], o, flags, act,
                                (round(px / posq), round(pz / posq)) if posq else 0))
                    txt.append("%s[%08X%s] %d/%d mp %d obj %07X fl %08X act %02X%s @%d,%d,%d" % (
                        u["role"], u["slot"], "*" if u["mark"] else "", u["hp"], u["mhp"], u["mp"], o, flags, act,
                        (" t %.2f" % tm) if tm is not None else "", px, py, pz))
                ex = " ".join("%08X=%08X" % (a, p.r32(a)) for a in extra)
                if "--thread" in sys.argv:   # read-only: dump the script thread the debug patch saw last (0x000F2FB4, 0x000F2FB8)
                    for ta in (0x000F2FB4, 0x000F2FB8):
                        tv = p.r32(ta)
                        if tv and tv != seen_thr.get(ta):
                            seen_thr[ta] = tv
                            fh.write("%6d  THREAD at %08X = %08X: %s" % (f, ta, tv, " ".join("%08X" % w for w in struct.unpack("<24I", p.read(tv, 96)))) + chr(10))
                if key != lastkey:
                    lastkey = key
                    nvw = struct.unpack("<8I", nv)
                    fh.write("%6d room %04X btl %d go %d nvars %s | %s %s\n" % (
                        f, room, btl, 1 if go else 0, " ".join("%08X" % w for w in nvw[:8]), " | ".join(txt), ex))
                    fh.flush()
            except Exception as e:  # noqa: BLE001
                fh.write("%6d (read error %s)\n" % (f, e))
                time.sleep(0.05)
    print("probe done ->", out)


if __name__ == "__main__":
    main()
