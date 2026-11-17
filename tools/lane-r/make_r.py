"""Lane R: the exit rule for two heroes, version 3 ("at the exit together"), on top of merged build v2.

  python -I tools/lane-r/make_r.py [outDir] [--dist N] [--no-sign] [--no-either-walk] [--no-second-offer]
                                   [--text "..."] [--either-spawn]

Default outDir: patches/lane-r-x3. Writes SLPM-66675_F266B00B.pnach and listing.txt.

What it is: merged-v2 (tools/merge/make_all.py --v2) with lane E's section "exits" taken out and this lane's
section "exits-r" put in its place. Every other word of merged-v2 is unchanged (checked at the end).

The rule (kinds of the engine's area events: 1 = room exit, 3 = start an event):
  * A room exit's JUMP volume (volume option 0) and an event trigger count as entered when one hero is inside AND
    the other hero is inside the same volume OR within DIST game units of the first (3-D distance; default 300).
  * A room exit's APPROACH volumes (option 1 / 2: they only show the destination's name, or the game's own
    "cannot go" message) work for each hero alone, as in the one-player game.
  * Either hero may be the one inside (second offer of the area event with the twin's position, lane E's idea).
  * Doors that want the hero to WALK INTO them accept that from either hero once both are at the exit.
  * The room jump and the event start always run with player 1's hero as the engine's player.
  * While one hero is in a usable exit or trigger and the other is too far, the game's own "wall message"
    window shows "Waiting for the other player." (text kept in the patch, no disc change).
If there is no twin in the room nothing changes. Other area-event kinds still follow player 1's hero only
(--either-spawn is an experiment: kind 2, spawn groups, also reacts to the twin).
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "merge"))
import make_all as M  # noqa: E402
import mips  # noqa: E402

AT = 0x000F3000          # this lane's code cave: 0x000F3000-0x000F37FF
END = 0x000F37FF

# "Waiting for the other player." in the game's international text table (tools/lane-r/LaneR msg-encode)
TEXT_DEFAULT = "449AA2ADA2A7A0019FA8AB01ADA19E01A8ADA19EAB01A9A59AB29EAB4F00"

INSIDE = """
r_inside:                         # hook 0x0019A168 (was: jalr v0). s0 = volume, s1 = area event, s5 = a1 = position of the offered hero, v0 = the volume's own "is this point inside" method
    addiu sp,sp,-48
    sd ra,0(sp)
    sd v0,8(sp)
    jalr v0                       # is the offered hero inside?
    nop
    beq v0,zero,NOT_INSIDE
    nop
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)        # 1 during the second offer (the twin is the offered hero)
    lw t3,8(s1)
    lbu t6,0(t3)                  # kind of area event
    addiu t5,t6,-1
    beq t5,zero,ri_exit           # 1 = room exit
    addiu t5,t6,-3
    beq t5,zero,ri_both           # 3 = start an event
    nop
    beq t4,zero,ri_out            # other kinds: first offer as the game does ...
    nop
    b ri_out                      # ... and never on the second offer
    move v0,zero
SPAWN_EITHER
ri_exit:
    lw t5,108(s0)
    lhu t5,2(t5)                  # volume option: 0 = jump volume, 1 / 2 = approach volume
    bne t5,zero,ri_out            # approach volumes: as the game does, for whichever hero is offered
    nop
ri_both:
    lw a0,%lo(V_TWIN)(t7)         # the other hero: the twin on the first offer ...
    beq t4,zero,ri_other
    nop
    lw a0,%lo(V_P1)(t7)           # ... player 1's hero on the second
ri_other:
    beq a0,zero,ri_out            # no twin in this room: as the game does
    nop
    jal POS_OF                    # game: pointer to an object's position
    nop
    sd v0,16(sp)
    move a1,v0
    ld t9,8(sp)
    jalr t9                       # is the other hero inside the same volume?
    move a0,s0
    bne v0,zero,ri_yes
    nop
    ld t1,16(sp)                  # no: how far apart are the two heroes?
    lwc1 f0,0(s5)
    lwc1 f1,0(t1)
    sub.s f0,f0,f1
    mul.s f0,f0,f0
    lwc1 f2,4(s5)
    lwc1 f3,4(t1)
    sub.s f2,f2,f3
    mul.s f2,f2,f2
    add.s f0,f0,f2
    lwc1 f2,8(s5)
    lwc1 f3,8(t1)
    sub.s f2,f2,f3
    mul.s f2,f2,f2
    add.s f0,f0,f2                # squared distance
    lui t2,%hi(R_D2)
    lwc1 f1,%lo(R_D2)(t2)
    c.le.s f0,f1
    nop
    bc1t ri_yes                   # within DIST: both heroes are at the exit
    nop
SIGN_CALL
    b ri_out                      # too far: the volume does not count
    move v0,zero
ri_yes:
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)
    beq t4,zero,ri_one            # first offer: the engine's player is player 1's hero already
    lw t3,8(s1)
    lbu t6,0(t3)
    addiu t5,t6,-3
    bne t5,zero,ri_one            # a room exit puts the engine's player back at the jump itself (r_jump)
    nop
    lw t5,%lo(V_P1)(t7)           # an event starts with player 1's hero as the engine's player
    lui t6,%hi(G_PLAYER)
    sw t5,%lo(G_PLAYER)(t6)
ri_one:
    li v0,1
ri_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""

SPAWN_EITHER = """
ri_notin:                         # OPTION --either-spawn: player 1's hero is not inside. Spawn zones (kind 2) also count the twin.
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)
    bne t4,zero,ri_out            # (only on the game's own offer; v0 = 0)
    lw t3,8(s1)
    lbu t6,0(t3)
    addiu t5,t6,-2
    bne t5,zero,ri_out            # only kind 2 = spawn objects when a hero enters the zone
    lw a0,%lo(V_TWIN)(t7)
    beq a0,zero,ri_out            # no twin
    nop
    jal POS_OF
    nop
    move a1,v0
    ld t9,8(sp)
    jalr t9                       # is the twin inside the zone?
    move a0,s0
    b ri_out
    nop
"""

SIGN_CALL = """
    lw a0,8(s1)
    jal r_sign                    # show "Waiting for the other player."
    lbu a1,0(a0)
"""

SIGN = """
r_sign:                           # a0 = the area event's data, a1 = its kind
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    addiu t0,a1,-1
    bne t0,zero,rs_show           # event trigger: no door conditions
    nop
    jal BATTLE_MODE               # room exit: would the game use this door now?
    nop
    ld a0,8(sp)
    xori v0,v0,2
    bne v0,zero,rs_dest
    nop
    lbu t0,30(a0)
    bne t0,zero,rs_done           # forced battle: the game ignores doors that must be walked into
    nop
rs_dest:
    lbu t6,28(a0)                 # destination room, as the game works it out (0x0019A4F4-0x0019A528)
    addiu t0,t6,-100
    beq t0,zero,rs_d
    addiu t0,t6,-101
    beq t0,zero,rs_e
    lui t1,%hi(NOW_WORLD)
    lbu a0,%lo(NOW_WORLD)(t1)
    b rs_q
    move a1,t6
rs_d:
    li a0,18
    b rs_q
    li a1,1
rs_e:
    li a0,2
    li a1,40
rs_q:
    jal DOOR_CLOSED               # closed by the story? then the game shows its own message
    nop
    bne v0,zero,rs_done
    nop
rs_show:
    lui t0,%hi(MSG_TIME)
    lwc1 f12,%lo(MSG_TIME)(t0)    # the game's own display time for wall messages
    lui a0,%hi(R_TEXT)
    jal WALL_MSG                  # the game's wall-message window (same call the game makes at 0x0019A7F4)
    addiu a0,a0,%lo(R_TEXT)
rs_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""

WALK = """
r_walk:                           # hook 0x0019A57C (was: jal 0x001DB198). a0 = jump volume, a1 = door type. "Is the hero walking into this door?"
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal WALKING_IN                # the hero that stands in the jump volume (the engine's player during this offer)
    nop
    bne v0,zero,rw_done
    nop
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)
    lw t6,%lo(V_TWIN)(t7)         # the other hero: the twin on the first offer ...
    beq t4,zero,rw_o
    nop
    lw t6,%lo(V_P1)(t7)           # ... player 1's hero on the second
rw_o:
    beq t6,zero,rw_done           # no twin: the game's answer stands
    nop
    lui t5,%hi(G_PLAYER)
    lw t3,%lo(G_PLAYER)(t5)
    sd t3,24(sp)
    sw t6,%lo(G_PLAYER)(t5)       # ask the same question for the other hero (a query only) ...
    ld a0,8(sp)
    jal WALKING_IN
    ld a1,16(sp)
    ld t3,24(sp)
    lui t5,%hi(G_PLAYER)
    sw t3,%lo(G_PLAYER)(t5)       # ... and put the engine's player back
rw_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""

JUMP = """
r_jump:                           # hook 0x0019A590 (was: jal 0x0019A610). The room jump always runs with player 1's hero as the engine's player.
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)
    beq t4,zero,rj_go
    nop
    lw t5,%lo(V_P1)(t7)
    lui t6,%hi(G_PLAYER)
    sw t5,%lo(G_PLAYER)(t6)
rj_go:
    j ROOM_JUMP
    nop
"""

SECOND_OFFER = """
r_offer:                          # hook 0x00182D04 (was: jal 0x00182980). a0 = area event table entry, a1 = point. Lane E's second offer, unchanged in what it does.
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal AREA_OFFER                # first offer: player 1's hero, as the game does
    nop
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    beq t6,zero,ro_done           # no twin
    nop
    ld a0,8(sp)
    lw t5,4(a0)
    andi t5,t5,1
    bne t5,zero,ro_done           # this entry is switched off
    nop
    lw t0,8(a0)                   # the area event
    beq t0,zero,ro_done
    nop
    lw t1,8(t0)
    lbu t2,0(t1)                  # its kind
    addiu t3,t2,-1
    beq t3,zero,ro_go
    addiu t3,t2,-3
SPAWN_KIND
    bne t3,zero,ro_done           # only these kinds get the second offer
    nop
ro_go:
    lui t5,%hi(G_PLAYER)
    lw t4,%lo(G_PLAYER)(t5)
    beq t4,zero,ro_done
    nop
    beq t4,t6,ro_done             # the twin is the engine's player (should not happen): leave it
    nop
    sw t4,%lo(V_P1)(t7)
    sw t6,%lo(G_PLAYER)(t5)       # the engine's player = the twin, for the queries of the second offer
    li t3,1
    sw t3,%lo(V_PASS2)(t7)
    lw t3,4(t0)
    andi t3,t3,0x18               # what the first offer found (inside / approach flags)
    sd t3,16(sp)
    sd t0,24(sp)
    jal POS_OF
    move a0,t6
    move a1,v0
    jal AREA_OFFER                # second offer: the twin as the offered hero
    ld a0,8(sp)
    lui t7,%hi(V_TWIN)
    sw zero,%lo(V_PASS2)(t7)
    lw t4,%lo(V_P1)(t7)
    lui t5,%hi(G_PLAYER)
    sw t4,%lo(G_PLAYER)(t5)       # put the engine's player back (r_jump / r_inside may have done it already)
    ld t0,24(sp)
    ld t3,16(sp)
    lw t2,4(t0)
    or t2,t2,t3
    sw t2,4(t0)                   # keep the first offer's flags
ro_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""


def text_words(hexstr):
    data = bytes.fromhex(hexstr)
    if not data.endswith(b"\0"):
        data += b"\0"
    data += b"\0" * (-len(data) % 4)
    return [struct.unpack_from("<I", data, i)[0] for i in range(0, len(data), 4)]


def main():
    args = sys.argv[1:]

    def opt(name, takes=False, default=None):
        if name in args:
            i = args.index(name)
            v = args[i + 1] if takes else True
            del args[i:i + (2 if takes else 1)]
            return v
        return default

    dist = float(opt("--dist", True, "300"))
    no_sign = opt("--no-sign")
    no_walk = opt("--no-either-walk")
    no_second = opt("--no-second-offer")
    either_spawn = opt("--either-spawn")
    text_hex = opt("--text-hex", True, TEXT_DEFAULT)
    out = pathlib.Path(args[0]) if args else ROOT / "patches" / "lane-r-x3"

    # merged-v2 without lane E's exit section (and without lane A's base, as in v2)
    sections, hooks = M.build({"base", "exits"}, True)
    sym = dict(M.SYM)
    sym.update({
        "BATTLE_MODE": 0x001917B0,   # game: 0 = no battle, 1 = battle, 2 = forced battle
        "DOOR_CLOSED": 0x00196768,   # game: non-zero if the story keeps this door closed (world, room)
        "WALL_MSG": 0x0015B268,      # game: show a text in the wall-message window (f12 = time, a0 = text)
        "MSG_TIME": 0x0036D340,      # game: the float the game passes as time (6.0)
        "NOW_WORLD": 0x0032BAE0,     # current world
        "WALKING_IN": 0x001DB198,    # game: is the engine's player walking into this door volume
        "ROOM_JUMP": 0x0019A610,     # game: start the jump to the next room
    })
    src = INSIDE.replace("NOT_INSIDE", "ri_notin" if either_spawn else "ri_out")
    src = src.replace("SPAWN_EITHER", SPAWN_EITHER if either_spawn else "")
    src = src.replace("SIGN_CALL", "" if no_sign else SIGN_CALL)
    if not no_sign:
        src += SIGN
    if not no_walk:
        src += WALK
    src += JUMP
    if not no_second:
        src += SECOND_OFFER.replace("SPAWN_KIND\n", "")
    d2 = struct.unpack("<I", struct.pack("<f", dist * dist))[0]
    src += "\nR_D2:\n    .word 0x%08X          # DIST * DIST as a float (DIST = %g)\n" % (d2, dist)
    if not no_sign:
        src += "R_TEXT:\n" + "".join("    .word 0x%08X\n" % w for w in text_words(text_hex))
    rows, syms = M.asm_lines(AT, src, sym)
    if rows[-1][0] + 3 > END:
        sys.exit("routines do not fit in the cave")
    title = ("lane R exits: both heroes at the exit (one inside, the other inside or within %g units), sign, "
             "either hero may walk in" % dist)
    sections.append(("exits-r", title, rows))
    hooks.append((0x0019A168, M.jal(syms["r_inside"]), 0x0040F809, "exits-r",
                  "volume test: the two-hero rule for exits (jump volume) and event triggers"))
    if not no_second:
        hooks.append((0x00182D04, M.jal(syms["r_offer"]), M.jal(0x00182980), "exits-r",
                      "area-event loop: second offer with the twin as the offered hero"))
    if not no_walk:
        hooks.append((0x0019A57C, M.jal(syms["r_walk"]), M.jal(0x001DB198), "exits-r",
                      "door: 'is the hero walking into it' may be answered by either hero"))
    hooks.append((0x0019A590, M.jal(syms["r_jump"]), M.jal(0x0019A610), "exits-r",
                  "door: the room jump runs with player 1's hero as the engine's player"))

    word = M.load_elf_words()
    code, hook_words, problems = {}, {}, []
    for name, _, rws in sections:
        for addr, w, _, _, _ in rws:
            if addr in code:
                sys.exit("CLASH: code address %08X used by two sections" % addr)
            code[addr] = w
    for addr, w, orig, name, _ in hooks:
        if addr in hook_words or addr in code:
            sys.exit("CLASH: hook address %08X used twice" % addr)
        hook_words[addr] = w
        have = word(addr)
        if have is None:
            problems.append("hook %08X is outside the program file" % addr)
        elif orig is not None and have != orig:
            problems.append("hook %08X: program has %08X, expected %08X" % (addr, have, orig))
    for a in code:
        if word(a) is not None:
            problems.append("code address %08X is inside the program file" % a)
    if problems:
        sys.exit("PROBLEMS:\n  " + "\n  ".join(problems))

    out.mkdir(parents=True, exist_ok=True)
    names = [n for n, _, _ in sections]
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project, lane R on merged build v2: " + " + ".join(names) + " (tools/lane-r/make_r.py).",
             "comment=Every PC in an online game must have this same file (it changes game code)."]
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hook_words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hook_words[a]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")

    lst = ["Lane R patch (merged-v2 with the exit section replaced) for CRC F266B00B. Every word the file writes.", ""]
    for name, title, rws in sections:
        lst.append("=" * 100)
        lst.append("SECTION %s: %s" % (name, title))
        lst.append("  cave 0x%08X-0x%08X (%d words)" % (rws[0][0], rws[-1][0] + 3, len(rws)))
        for addr, w, labels, s, comment in rws:
            for lab, lc in labels:
                lst.append("%s:%s" % (lab, ("    # " + lc) if lc else ""))
            lst.append("  %08X  %08X  %-34s%s" % (addr, w, mips.dis(w, addr), ("# " + comment) if comment else ""))
        lst.append("")
    lst.append("=" * 100)
    lst.append("HOOKS (words changed inside the game program)")
    for addr, w, orig, name, meaning in sorted(hooks):
        have = word(addr)
        lst.append("  %08X  %08X  %-26s was %08X %-28s [%s] %s" % (
            addr, w, mips.dis(w, addr), have, mips.dis(have, addr), name, meaning))
    lst.append("")
    lst.append("VARIABLES (not written by the patch file; they rely on that memory being zero at boot)")
    for k in ("V_FLAG", "V_ISP1", "V_OLD", "V_TWIN", "V_PASS2", "V_P1", "BUSY", "V_BUILD"):
        lst.append("  %08X  %s" % (M.SYM[k], k))
    lst.append("RESERVED DATA: %08X-%08X = second control object S2 (lane G)" % (M.COMMANDS_S2, M.COMMANDS_S2 + 0xAFF))
    (out / "listing.txt").write_text("\n".join(lst) + "\n")

    # check against merged-v2: every word outside lane E's exit section and this lane's section must be equal
    def lane_words(path):
        d = {}
        for line in pathlib.Path(path).read_text().splitlines():
            if line.startswith("patch=1,EE,"):
                p = line.split(",")
                d[int(p[2], 16)] = int(p[4], 16)
        return d
    v2 = lane_words(ROOT / "patches" / "merged-v2" / "SLPM-66675_F266B00B.pnach")
    mine = dict(code)
    mine.update(hook_words)
    e_exit = {a for a in v2 if 0x000F0420 <= a <= 0x000F05BF} | {0x0019A168, 0x00182D04}
    diff = sorted(a for a in v2 if a not in e_exit and mine.get(a) != v2[a])
    extra = sorted(a for a in mine if a not in v2 and not (AT <= a <= END) and a not in (0x0019A57C, 0x0019A590))
    print("%d code words, %d hook words -> %s" % (len(code), len(hook_words), out / "SLPM-66675_F266B00B.pnach"))
    print("   exits-r 0x%08X-0x%08X (%d words), DIST %g" % (rows[0][0], rows[-1][0] + 3, len(rows), dist))
    print("check against merged-v2: %d words of v2 outside lane E's exit section, different: %s; unexpected extra: %s" % (
        len([a for a in v2 if a not in e_exit]), ", ".join("%08X" % a for a in diff) or "none",
        ", ".join("%08X" % a for a in extra) or "none"))
    for k in ("r_inside", "r_sign", "r_walk", "r_jump", "r_offer", "R_D2", "R_TEXT"):
        if k in syms:
            print("   %-9s %08X" % (k, syms[k]))


if __name__ == "__main__":
    main()
