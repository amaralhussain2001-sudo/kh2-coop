"""One-off: tools/merge/merge_v6.py, FOURTEENTH GLUE: the Reaction Command that the timeline of a scripted
move opens ("Break Raid" in Twilight Thorn's throw) goes to the hero who is IN the move.
Found on 2026-11-11 (tests g7-thorn, g9-thorn): the event player's callback 0x00197D40, kind 1, hands the
command to the engine's player (load at 0x00197DE0, call of 0x00196E98(event, hero) at 0x00197DE4), so with the
twin in the move the command sat in player 1's menu and only player 1's Triangle started it."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "EVRC_SRC" in t:
    raise SystemExit("already there")


def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (t.count(old), old[:70])
    t = t.replace(old, new)


rep("REACT_AT = 0x000F4A00", '''EVRC_AT = 0x000F5B00
EVRC_END = 0x000F5B80
EVRC_SRC = """
ev_rc:                            # call at 0x00197DE4 (was: jal 0x00196E98). a0 = the event, a1 = the engine's player
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,er_go
    nop
    beq a1,zero,er_go
    nop
    lw t3,0x160(t6)               # bit 0x4000: this hero is in a scripted move
    lw t2,0x160(a1)
    srl t3,t3,14
    srl t2,t2,14
    andi t3,t3,1
    andi t2,t2,1
    beq t3,t2,er_go               # both or neither: as it is
    nop
    beq t3,zero,er_go             # player 1's hero is the one in the move
    nop
    move a1,t6                    # the twin is: the command is his
er_go:
    j 0x00196E98
    nop
"""
EVRC_HOOK = (0x00197DE4, 0x0C065BA6, "the command a scripted move's timeline opens: to the hero in the move")

REACT_AT = 0x000F4A00''')
rep('''    if "--react" in sys.argv:          # EXPERIMENT''', '''    if "--no-evrc" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(EVRC_AT, EVRC_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert EVRC_AT + 4 * len(code) <= EVRC_END, "event command glue too long"
        for i, w in enumerate(code):
            a = EVRC_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (a scripted move's command goes to the hero in the move)"
        a, w0, what = EVRC_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<I", elf.data, off + a - va)[0]
        assert have == w0, "hook %08X: program has %08X" % (a, have)
        words[a] = (3 << 26) | ((labels["ev_rc"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (event command): " + what
        n_glue += len(code) + 1

    if "--react" in sys.argv:          # EXPERIMENT''')
rep("  python -I tools/merge/merge_v6.py [outDir]", '''FOURTEENTH GLUE (option --no-evrc leaves it out): THE COMMAND OF A SCRIPTED MOVE GOES TO THE HERO IN THE MOVE.
A boss's scripted move is an event (object 0x0035037C) played from a timeline. When the timeline opens a
Reaction Command window, the event player's callback (0x00197D40, kind 1) hands the command to the engine's
player (0x00197DE0 / 0x00197DE4 -> 0x00196E98(event, hero)). With the twin in the move ("Break Raid" in Twilight
Thorn's throw) the command sat in player 1's menu and only player 1's Triangle started it (tests g7-thorn,
b5 / b6). Now the call goes through ev_rc (0x000F5B00): when exactly one hero carries the "in a scripted move"
bit (object +0x160, 0x4000) and it is the twin, the twin is handed in.

  python -I tools/merge/merge_v6.py [outDir]''')
rep("[--no-helpers] [--no-nea", "[--no-helpers] [--no-evrc] [--no-nea")
p.write_text(t, encoding="utf-8")
print("ok")
