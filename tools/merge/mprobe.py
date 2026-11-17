"""Merge lane: read "who is who" and the unit slots from a running sandbox emulator through PINE.

Waits for the session screenshot of each frame (so the frames must be in the run's --snap list), then prints and
appends to <test-out-dir>/probe.txt:
  room, battle flag, engine player / camera target / party slot 0 / command controller owner, lane E's twin
  pointer, the glue flag, the twin's two save bytes, player 1's record HP / MP;
  every player object: address, position, controller, unit slot (number, HP, MP, mark bit, status id), roles;
  the unit slots in use (first 10).

  python -I tools/merge/mprobe.py <test-out-dir> <pinePort> <frame,frame,...> [--timeout 600]
         [--set F:hero.hp=7;twin.hp=13;hero.mp=60;twin.mp=40]   ONE-copy tests only: write these after frame F
         [--redirect F0:F1]   ONE-copy tests only: between the two frames keep telling the engine that the twin
                              is its player (0x00352400 and 0x0034E948), so enemies go for the twin
Reads are harmless. Writes change the game and must never be used on one PC of a linked pair.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

PADS = {0x0034D6C0: "pad1", 0x0034D720: "pad2", 0: "none"}
SLOT1, STEP, POOL = 0x01C6C750, 0x268, 0x01C62FB8
FREE_CNT, FREE_LIST = 0x01C6CAB8, 0x01C6C9B8
S = 0x01C5F530
S2 = 0x000F1000      # lane G: second control object (merged build v2)


def find_players(p):
    ram = p.read(0x01000000, 0x01000000)
    res, pos, key = [], 0, struct.pack("<I", 0x00352410)
    while True:
        i = ram.find(key, pos)
        if i < 0:
            break
        pos = i + 4
        if i % 4 or i + 0xB80 > len(ram):
            continue
        if struct.unpack_from("<I", ram, i + 0xB44)[0] not in (S, S2):
            continue
        res.append((0x01000000 + i, ram[i:i + 0xB80]))
    return res


def slot_info(p, a):
    if not (POOL <= a < POOL + 64 * STEP):
        return None
    b = p.read(a, STEP)
    hp, mx = struct.unpack_from("<ii", b, 0)
    mp, mmx = struct.unpack_from("<ii", b, 0x180)
    flags, sid, ref, owner = struct.unpack_from("<IiiI", b, 0x250)
    return {"addr": a, "n": (SLOT1 - a) // STEP + 1, "hp": hp, "max": mx, "mp": mp, "mmax": mmx,
            "flags": flags, "id": sid, "ref": ref, "owner": owner, "stats": struct.unpack_from("<4h", b, 0x188)}


def snapshot(p):
    g = {
        "room": p.r32(0x0032BAE0), "btl": p.r32(0x01C61958) & 0xFF,
        "player": p.r32(0x0034E948), "last": p.r32(0x00352400), "cam": p.r32(0x00348754),
        "party0": p.r32(0x00348638), "S.player": p.r32(S + 0x9E0), "S.pad": p.r32(S + 0x9E4),
        "twin": p.r32(0x000F05CC), "build": p.r32(0x000F0DF0), "busy": p.r32(0x000F02F0),
        "save_hp": p.r8(0x0032D98E), "save_mp": p.r8(0x0032D98F),
        "rec_hp": p.r8(0x0032E024), "rec_mp": p.r8(0x0032E026), "level": p.r8(0x0032E02F),
        "S2.vt": p.r32(S2), "S2.player": p.r32(S2 + 0x9E0), "S2.pad": p.r32(S2 + 0x9E4), "cur": p.r32(0x003527E0),
        "S.cursor": p.r32(S + 0x90), "S2.cursor": p.r32(S2 + 0x90),
    }
    disp = p.r32(0x003484A0)
    g["disp.ctl"] = p.r32(disp + 0x29C) if 0x00100000 <= disp < 0x02000000 else 0
    objs = []
    for addr, blob in find_players(p):
        x, y, z = struct.unpack_from("<3f", blob, 0x70)
        pad = struct.unpack_from("<I", blob, 0xB38)[0]
        slot = struct.unpack_from("<I", blob, 0x48C)[0]
        objs.append({"addr": addr, "pos": (x, y, z), "pad": pad, "slot": slot_info(p, slot), "slotaddr": slot,
                     "ctl": struct.unpack_from("<I", blob, 0xB3C)[0], "action": struct.unpack_from("<I", blob, 0x154)[0]})
    cnt = p.r32(FREE_CNT)
    free = set()
    if 0 <= cnt <= 64:
        free = set(struct.unpack("<64i", p.read(FREE_LIST, 256))[:cnt])
    slots = []
    for k in range(12):
        a = SLOT1 - STEP * k
        if (a - POOL) // STEP in free:
            continue
        slots.append(slot_info(p, a))
    return g, objs, slots


def role(g, o):
    marks = []
    if o["addr"] == g["player"]:
        marks.append("ENGINE-PLAYER")
    if o["addr"] == g["cam"]:
        marks.append("CAMERA")
    if o["addr"] == g["party0"]:
        marks.append("HUD")
    if o["addr"] == g["twin"]:
        marks.append("twin")
    return " ".join(marks) or "-"


def show(tag, g, objs, slots, say):
    a7 = lambda a: "0" if a == 0 else "%07X" % a  # noqa: E731
    say("%s room %04X battle %d | engine player %s last %s camera %s hud %s S.player %s S.pad %s | twin %s | factory flag %d | "
        "twin save bytes HP %d MP+1 %d | record HP %d MP %d level %d" % (
            tag, g["room"] & 0xFFFF, g["btl"], a7(g["player"]), a7(g["last"]), a7(g["cam"]), a7(g["party0"]),
            a7(g["S.player"]), PADS.get(g["S.pad"], hex(g["S.pad"])), a7(g["twin"]), g["build"],
            g["save_hp"], g["save_mp"], g["rec_hp"], g["rec_mp"], g["level"]))
    ctl = lambda a: {S: "S", S2: "S2", 0: "none"}.get(a, "%07X" % a)  # noqa: E731
    say("     control objects: S2 built %s, S2.player %s, S2.pad %s, menu on screen shows %s, 'current' %s, cursors S %d S2 %d" % (
        "yes" if g["S2.vt"] else "no", a7(g["S2.player"]), PADS.get(g["S2.pad"], hex(g["S2.pad"])), ctl(g["disp.ctl"]),
        ctl(g["cur"]), g["S.cursor"], g["S2.cursor"]))
    for o in objs:
        o["ctlname"] = ctl(o["ctl"])
        s = o["slot"]
        st = ("slot %d HP %d/%d MP %d/%d %s id %d" % (s["n"], s["hp"], s["max"], s["mp"], s["mmax"],
              "MARKED" if s["flags"] & 0x80000000 else "plain", s["id"])) if s else "slot ? (%08X)" % o["slotaddr"]
        say("     hero %07X pos (%8.1f %7.1f %8.1f) %s  %s  [%s] ctl %s act %X" % (
            o["addr"], o["pos"][0], o["pos"][1], o["pos"][2], PADS.get(o["pad"], hex(o["pad"])), st, role(g, o),
            o["ctlname"], o["action"]))
    say("     slots: " + "; ".join("%d: id %d HP %d/%d MP %d%s owner %07X" % (
        s["n"], s["id"], s["hp"], s["max"], s["mp"], " MARKED" if s["flags"] & 0x80000000 else "", s["owner"]) for s in slots))


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
    sets = {}
    for i, a in enumerate(sys.argv):
        if a == "--set":
            f, _, rest = sys.argv[i + 1].partition(":")
            sets[int(f)] = [x.split("=") for x in rest.split(";") if x]
    redirect = None
    if "--redirect" in sys.argv:
        f0, f1 = sys.argv[sys.argv.index("--redirect") + 1].split(":")
        redirect = (int(f0), int(f1))
    outdir.mkdir(parents=True, exist_ok=True)
    log = open(outdir / "probe.txt", "a", encoding="utf-8")

    def say(s):
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    t0 = time.time()
    p = None
    for idx, f in enumerate(frames):
        shot = outdir / ("p1_f%06d.png" % f)
        while not shot.exists():
            if time.time() - t0 > timeout:
                say("timeout waiting for " + shot.name)
                return
            time.sleep(0.01)
        try:
            if p is None:
                p = Pine(port, wait=20)
            g, objs, slots = snapshot(p)
            show("f%06d" % f, g, objs, slots, say)
            if f in sets:
                hero = next((o for o in objs if o["addr"] == g["player"]), None)
                twin = next((o for o in objs if o["addr"] == g["twin"]), None)
                for name, value in sets[f]:
                    who, field = name.split(".")
                    o = hero if who == "hero" else twin
                    if o is None or o["slot"] is None:
                        say("     SET %s skipped (no such hero)" % name)
                        continue
                    p.w32(o["slot"]["addr"] + (0 if field == "hp" else 0x180), int(value))
                    say("     SET %s = %s (slot %d, test write)" % (name, value, o["slot"]["n"]))
            if redirect and f == redirect[0] and g["twin"]:
                stop = outdir / ("p1_f%06d.png" % redirect[1])
                n = 0
                while not stop.exists() and time.time() - t0 < timeout:
                    p.w32(0x00352400, g["twin"])
                    p.w32(0x0034E948, g["twin"])
                    n += 1
                    time.sleep(0.002)
                say("     REDIRECT: wrote the twin into 0x00352400 and 0x0034E948 %d times (test write)" % n)
        except Exception as e:  # noqa: BLE001
            say("f%06d read failed: %s" % (f, e))
            p = None


if __name__ == "__main__":
    main()
