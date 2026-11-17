"""Lane S3 (Gummi Ship study): experiment patches = merged-v2 lines + this lane's lines. TESTS ONLY, not for play.

  python -I tools/lane-s3/make_s3.py <outDirName> <mode> [args]      -> patches/<outDirName>/SLPM-66675_F266B00B.pnach

Modes (several may be given, separated by spaces; each may take key=value arguments):
  count              count calls of the controller getter from the world-map code sites (counters at 0x000F5F00..)
  launch route=N [level=L] [delay=F]
                     on the world map, start Gummi route N (0..8) once, F calls after the map's cursor code first
                     runs (default 90). Uses the game's own routine 0x002C5418 (the one a route symbol calls).
  nobase             do not include the merged-v2 lines (default: include them)
  ovl:<name>         overlay experiments, written only while the Gummi battle module is loaded (see OVL below)

Code cave of this lane: 0x000F5000-0x000F5FFF (routines from 0x000F5000, variables from 0x000F5F00).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

GET_PAD = 0x00167F18
START_ROUTE = 0x002C5418      # world map: start the Gummi menu for route a0 (0..8); creates the menu task
VAR = 0x000F5F00              # counters / flags
SYM = {"GET_PAD": GET_PAD, "START_ROUTE": START_ROUTE, "VAR": VAR}

# controller-getter call sites inside the world-map code of the main program (from tools/lane-a callers list)
WM_SITES = [0x002C3668, 0x002C5F08, 0x002D0320, 0x002D035C, 0x002D0390, 0x002D053C]

# signature of the Gummi battle module: low 16 bits of the word at 0x01F18014 (its entry jump)
OVL_SIG_ADDR, OVL_SIG_BATTLE, OVL_SIG_MENU = 0x01F18014, 0x636A, 0x62B0


def jal(t):
    return (0x03 << 26) | ((t >> 2) & 0x3FFFFFF)


def base_lines():
    src = ROOT / "patches" / "merged-v2" / "SLPM-66675_F266B00B.pnach"
    return [l for l in src.read_text().splitlines() if l.startswith("patch=1,EE,")]


def words_to_lines(base, words):
    return ["patch=1,EE,%08X,word,%08X" % (base + 4 * i, w) for i, w in enumerate(words)]


def guarded(sig, pairs):
    """pnach lines that write 32-bit words only while the overlay with this signature is loaded."""
    out = []
    pairs = list(pairs)
    for i in range(0, len(pairs), 200):
        chunk = pairs[i:i + 200]
        out.append("patch=1,EE,E0%02X%04X,extended,%08X" % (len(chunk), sig, OVL_SIG_ADDR))
        for a, v in chunk:
            out.append("patch=1,EE,%08X,extended,%08X" % (0x20000000 | a, v))
    return out


def mode_count(pc, lines, notes, args):
    for i, site in enumerate(WM_SITES):
        src = """
        lui t7, %%hi(VAR)
        lw t6, %d(t7)
        addiu t6, t6, 1
        sw t6, %d(t7)
        j GET_PAD
        daddu a0, zero, zero
        """ % ((VAR & 0xFFFF) + 4 * i, (VAR & 0xFFFF) + 4 * i)
        w, _ = assemble(pc, src, SYM)
        lines += words_to_lines(pc, w)
        lines.append("patch=1,EE,%08X,word,%08X" % (site, jal(pc)))
        notes.append("count: site 0x%08X -> counter 0x%08X" % (site, VAR + 4 * i))
        pc += 4 * len(w)
    return pc


def mode_launch(pc, lines, notes, args):
    route = int(args.get("route", "0"))
    delay = int(args.get("delay", "90"))
    site = int(args.get("site", "002C5F08"), 16)
    # variables: VAR+0x40 call counter, VAR+0x44 latch
    src = """
        lui t7, %%hi(VAR)
        lw t6, %d(t7)            # call counter
        addiu t6, t6, 1
        sw t6, %d(t7)
        lw t5, %d(t7)            # latch
        bne t5, zero, done
        slti t5, t6, %d
        bne t5, zero, done
        addiu t5, zero, 1
        sw t5, %d(t7)            # latch = 1
        addiu sp, sp, -16
        sd ra, 0(sp)
        jal START_ROUTE
        addiu a0, zero, %d
        ld ra, 0(sp)
        addiu sp, sp, 16
    done:
        j GET_PAD
        daddu a0, zero, zero
    """ % ((VAR & 0xFFFF) + 0x40, (VAR & 0xFFFF) + 0x40, (VAR & 0xFFFF) + 0x44, delay, (VAR & 0xFFFF) + 0x44, route)
    w, _ = assemble(pc, src, SYM)
    lines += words_to_lines(pc, w)
    lines.append("patch=1,EE,%08X,word,%08X" % (site, jal(pc)))
    notes.append("launch: site 0x%08X -> routine 0x%08X, route %d after %d calls; counter 0x%08X latch 0x%08X"
                 % (site, pc, route, delay, VAR + 0x40, VAR + 0x44))
    return pc + 4 * len(w)


OVL = {}


def ovl(name):
    def deco(f):
        OVL[name] = f
        return f
    return deco


@ovl("pad1")
def ovl_pad1(args):
    """Every controller fetch of the Gummi battle module asks for logical controller 1 (pad 2) instead of 0."""
    sites = [0x01F1924C, 0x01F21C48, 0x01F62570, 0x01F630A4, 0x01F6DA70, 0x01F6E1E0]
    only = args.get("only")
    if only:
        keep = {int(x, 16) for x in only.split("+")}
        sites = [s for s in sites if s in keep]
    # each site: "jal GET_PAD" with "daddu a0,zero,zero" either in the delay slot or just before; make a0 = 1
    pairs = []
    for s in sites:
        pairs.append((s, jal(0x000F5E00)))
    return pairs, ["ovl pad1: sites %s call 0x000F5E00 (a0 = 1, then the getter)" % ", ".join("%08X" % s for s in sites)], \
        (0x000F5E00, "j GET_PAD\naddiu a0, zero, 1\n")


@ovl("mainpad1")
def ovl_mainpad1(args):
    """E0: the player's Gummi ship is built with logical controller 1 (pad 2) instead of 0. One word."""
    # 0x01F21C48 jal GET_PAD ; 0x01F21C4C daddu a0,zero,zero  ->  addiu a0,zero,1
    return [(0x01F21C4C, 0x24040001)], ["ovl mainpad1: 0x01F21C4C a0 = 1 (ship constructor gets pad 2)"], None


SHIP2_CAVE = 0x000F5100


@ovl("ship2")
def ovl_ship2(args):
    """E1: after the game has built the player's ship (and escorts), build a SECOND player ship object with
    logical controller 1 (pad 2), then make the first ship the engine's 'player ship' again.
    args: keepglobal=0 leaves the second ship as the engine's player ship (control experiment)."""
    keep = args.get("keepglobal", "1") == "1"
    src = """
        addiu sp, sp, -32
        sd ra, 0(sp)
        sd s4, 8(sp)
        jal 0x01F20DD8            # the call this hook replaced (a0 = ship 1, set in the delay slot at the site)
        daddu a0, s0, zero
        jal 0x01F19160            # module allocator: new(0x1440)
        addiu a0, zero, 0x1440
        daddu s4, v0, zero
        jal GET_PAD
        addiu a0, zero, 1
        daddu a0, s4, zero
        daddu a1, v0, zero
        addiu a2, sp, 32          # the caller's position vector
        jal 0x01F1E4A8            # player ship constructor(obj, pad, pos, rot)
        daddu a3, s1, zero        # the caller's rotation vector
        lui t7, %hi(VAR)
        sw s4, {v2}(t7)           # remember ship 2
        sw s0, {v1}(t7)           # remember ship 1
    """
    if keep:
        src += """
        lui t7, 0x01F8
        sw s0, -8636(t7)          # 0x01F7DE44 'the player ship' = ship 1 again
        """
    src += """
        ld ra, 0(sp)
        ld s4, 8(sp)
        jr ra
        addiu sp, sp, 32
    """
    src = src.format(v1=(VAR & 0xFFFF) + 0x80, v2=(VAR & 0xFFFF) + 0x84)
    return [(0x01F21CD4, jal(SHIP2_CAVE))],         ["ovl ship2: hook 0x01F21CD4 (was jal 0x01F20DD8) -> 0x%08X; ship 1 ptr at 0x%08X, ship 2 ptr at 0x%08X; keepglobal=%d"
         % (SHIP2_CAVE, VAR + 0x80, VAR + 0x84, keep)], (SHIP2_CAVE, src)


@ovl("ship2live")
def ovl_ship2live(args):
    """E2 (use together with ovl:ship2): (1) every time a ship's update runs for ship 2, copy ship 1's flight state
    (object + 0x50C) into it and count the call; (2) after the fire handler has served the engine's player ship,
    run the same two fire routines for ship 2."""
    v1, v2, vc = (VAR & 0xFFFF) + 0x80, (VAR & 0xFFFF) + 0x84, (VAR & 0xFFFF) + 0x88
    mirror = args.get("mirror", "1") == "1"
    fire = args.get("fire", "1") == "1"
    src = """
    upd:                            # replaces 'jal 0x01F21990' at the top of the ship update (a0 = s0 = this)
        lui t7, %hi(VAR)
        lw t6, {v2}(t7)
        bne a0, t6, upd_go
        lw t5, {v1}(t7)
        lw t4, {vc}(t7)
        addiu t4, t4, 1
        sw t4, {vc}(t7)             # count updates of ship 2
        beq t5, zero, upd_go
        nop
        lw t4, 0x50C(t5)
        sw t4, 0x50C(a0)            # ship 2 state = ship 1 state
    upd_go:
        j 0x01F21990
        nop
    fire:                           # replaces 'j 0x01F1EE00' at the end of the fire handler (a0 = player ship)
        addiu sp, sp, -16
        sd ra, 0(sp)
        jal 0x01F1EE00
        nop
        lui t7, %hi(VAR)
        lw a0, {v2}(t7)
        beq a0, zero, fire_out
        nop
        lw t6, 0x50C(a0)
        addiu t5, zero, 2
        bne t6, t5, fire_out
        nop
        jal 0x01F1ED28
        nop
        lui t7, %hi(VAR)
        jal 0x01F1EE00
        lw a0, {v2}(t7)
    fire_out:
        ld ra, 0(sp)
        jr ra
        addiu sp, sp, 16
    """.format(v1=v1, v2=v2, vc=vc)
    base = 0x000F5200
    words, syms = assemble(base, src, SYM)
    pairs = []
    if mirror:
        pairs.append((0x01F219B4, jal(syms["upd"])))
    if fire:
        pairs.append((0x01F2191C, (0x02 << 26) | ((syms["fire"] >> 2) & 0x3FFFFFF)))
    return pairs, ["ovl ship2live: update hook 0x01F219B4 -> 0x%08X (mirror=%d), fire hook 0x01F2191C -> 0x%08X (fire=%d); "
                   "ship 2 update counter 0x%08X" % (syms["upd"], mirror, syms["fire"], fire, VAR + 0x88)], (base, src)


RAIL_OFF = 0x01F7DEE0      # shared flight-controller object 0x01F7DE60 + 0x80: the player's offset on the rail (x, y, z, w)


@ovl("ship2own")
def ovl_ship2own(args):
    """E3 (use together with ovl:ship2; includes the fire part of ship2live with fire=1): ship 2 gets its OWN offset
    on the rail. The ship update is wrapped through the player-ship class table: for ship 2 the shared offset vector
    is exchanged with ship 2's own copy before its update and exchanged back after it; ship 2's flight state is
    copied from ship 1 as in E2."""
    v1, v2, vc = (VAR & 0xFFFF) + 0x80, (VAR & 0xFFFF) + 0x84, (VAR & 0xFFFF) + 0x88
    own, sav = (VAR & 0xFFFF) + 0xA0, (VAR & 0xFFFF) + 0xB0
    startx = int(args.get("startx", "0"))
    src = """
    wrap:                           # new entry of the player-ship update in the class table (a0 = this)
        lui t7, %hi(VAR)
        lw t6, {v2}(t7)
        beq a0, t6, wrap2
        nop
        j 0x01F219A8                # any other ship: the game's update, untouched
        nop
    wrap2:
        addiu sp, sp, -32
        sd ra, 0(sp)
        sd s0, 8(sp)
        daddu s0, a0, zero
        lw t4, {vc}(t7)
        addiu t4, t4, 1
        sw t4, {vc}(t7)             # count updates of ship 2
        lw t5, {v1}(t7)
        beq t5, zero, w_in
        nop
        lw t4, 0x50C(t5)
        sw t4, 0x50C(s0)            # ship 2 state = ship 1 state
    w_in:
        lui t6, %hi(RAIL_OFF)
        addiu t6, t6, %lo(RAIL_OFF)
        ld t0, 0(t6)
        ld t1, 8(t6)
        sd t0, {sav}(t7)            # keep player 1's offset
        sd t1, {sav8}(t7)
        ld t2, {own}(t7)
        ld t3, {own8}(t7)
        sd t2, 0(t6)                # shared offset = ship 2's own
        sd t3, 8(t6)
        jal 0x01F219A8
        daddu a0, s0, zero
        lui t7, %hi(VAR)
        lui t6, %hi(RAIL_OFF)
        addiu t6, t6, %lo(RAIL_OFF)
        ld t0, 0(t6)
        ld t1, 8(t6)
        sd t0, {own}(t7)            # ship 2's own offset = result
        sd t1, {own8}(t7)
        ld t2, {sav}(t7)
        ld t3, {sav8}(t7)
        sd t2, 0(t6)                # shared offset = player 1's again
        sd t3, 8(t6)
        ld ra, 0(sp)
        ld s0, 8(sp)
        jr ra
        addiu sp, sp, 32
    fire:                           # replaces 'j 0x01F1EE00' at the end of the fire handler (a0 = player ship)
        addiu sp, sp, -16
        sd ra, 0(sp)
        jal 0x01F1EE00
        nop
        lui t7, %hi(VAR)
        lw a0, {v2}(t7)
        beq a0, zero, fire_out
        nop
        lw t6, 0x50C(a0)
        addiu t5, zero, 2
        bne t6, t5, fire_out
        nop
        jal 0x01F1ED28
        nop
        lui t7, %hi(VAR)
        jal 0x01F1EE00
        lw a0, {v2}(t7)
    fire_out:
        ld ra, 0(sp)
        jr ra
        addiu sp, sp, 16
    """.format(v1=v1, v2=v2, vc=vc, own=own, own8=own + 8, sav=sav, sav8=sav + 8)
    base = 0x000F5300
    sym = dict(SYM)
    sym["RAIL_OFF"] = RAIL_OFF
    words, syms = assemble(base, src, sym)
    pairs = [(0x01F81068, syms["wrap"])]
    if args.get("fire", "1") == "1":
        pairs.append((0x01F2191C, (0x02 << 26) | ((syms["fire"] >> 2) & 0x3FFFFFF)))
    return pairs, ["ovl ship2own: class-table entry 0x01F81068 (update) -> 0x%08X; fire hook 0x01F2191C -> 0x%08X; "
                   "ship 2 own offset at 0x%08X, saved player-1 offset at 0x%08X" % (syms["wrap"], syms["fire"], VAR + 0xA0, VAR + 0xB0)],         (base, src, sym)


def main():
    out = ROOT / "patches" / sys.argv[1]
    out.mkdir(parents=True, exist_ok=True)
    toks = sys.argv[2:]
    use_base = "nobase" not in toks
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Lane S3 Gummi Ship study, TEST ONLY: " + " ".join(toks)]
    if use_base:
        lines += base_lines()
    notes = []
    pc = 0x000F5000
    i = 0
    while i < len(toks):
        t = toks[i]
        args = {}
        j = i + 1
        while j < len(toks) and "=" in toks[j]:
            k, v = toks[j].split("=", 1)
            args[k] = v
            j += 1
        if t == "count":
            pc = mode_count(pc, lines, notes, args)
        elif t == "launch":
            pc = mode_launch(pc, lines, notes, args)
        elif t.startswith("ovl:"):
            pairs, n, extra = OVL[t[4:]](args)
            notes += n
            if extra:
                w, _ = assemble(extra[0], extra[1], extra[2] if len(extra) > 2 else SYM)
                lines += words_to_lines(extra[0], w)
            lines += guarded(OVL_SIG_BATTLE, pairs)
        elif t == "nobase":
            pass
        else:
            sys.exit("unknown mode " + t)
        i = j
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    (out / "notes.txt").write_text("\n".join(notes) + "\n")
    print("%d lines -> %s" % (len(lines), out / "SLPM-66675_F266B00B.pnach"))
    for n in notes:
        print("  " + n)


if __name__ == "__main__":
    main()
