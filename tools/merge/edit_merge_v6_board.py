"""One-off: add the eleventh glue to tools/merge/merge_v6.py (the board commands go to the rider's own control
object)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "BOARD_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--helper] [--react]
''', '''ELEVENTH GLUE: THE SKATEBOARD'S COMMANDS GO TO THE RIDER'S OWN CONTROL OBJECT.
What was there (VERIFIED, test n2-mail-menu on the Mail Delivery disc with a second board: both heroes ride, both
have board mode 1 at object+0xB70, but only player 1's control object has the board menu, id 14; player 2's
stays at the root menu and his screen showed a broken menu, the board menu's pictures with the normal rows):
when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(hero, board) -> 0x00198860(board, 2)) the board
commands are opened on the control object of THE ENGINE'S PLAYER (load at 0x00198910, then 0x001BDB70), and
when the board is left (0x00198970(board)) they are closed on that one too (load at 0x00198990).
Now: the ride call (0x002EB8EC) notes the board when the rider is the twin (V_TBOARD); for that board the two
places take the twin (his control object, lane G's S2); for every other board or vehicle the engine's player as
before. Routines sk_ride, sk_who, sk_off at 0x000F4F00.

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--helper] [--react]
''')
rep('''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''', '''BOARD_AT = 0x000F4F00
BOARD_END = 0x000F4F80
V_TBOARD = 0x000F47F0             # the board the twin rides (0 = none)
BOARD_SRC = """
sk_ride:                          # hook 0x002EB8EC (was: jal 0x00198860). a0 = the board, s0 = the hero that
    lui t7,0x000F                 # gets on
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    lw t5,%lo(V_TBOARD)(t7)
    bne s0,t6,skr_other
    nop
    j 0x00198860
    sw a0,%lo(V_TBOARD)(t7)       # the twin's board
skr_other:
    bne t5,a0,skr_go              # another rider on the board that was noted (an old note): forget it
    nop
    sw zero,%lo(V_TBOARD)(t7)
skr_go:
    j 0x00198860
    nop
sk_who:                           # hook 0x00198910 (was: lw t6,-5816(t7), the engine's player). s2 = the board.
    lui t5,0x000F                 # Out: t6 = the hero whose control object gets the board commands
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s2,skw_p1
    lui t7,0x0035
    lw t6,0x05CC(t5)
    bne t6,zero,skw_out           # the twin's board: the twin
    nop
skw_p1:
    lw t6,-5816(t7)
skw_out:
    jr ra
    nop
sk_off:                           # hook 0x0019898C (0x00198990 is now a nop). s0 = the board that is left.
    lui t5,0x000F                 # Out: t6 = the hero whose control object leaves the board commands
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s0,sko_p1
    lui t7,0x0035
    sw zero,%lo(V_TBOARD)(t5)
    lw t6,0x05CC(t5)
    bne t6,zero,sko_out
    nop
sko_p1:
    lw t6,-5816(t7)
sko_out:
    jr ra
    nop
"""
BOARD_HOOKS = (                   # (address, word expected, word after it expected, routine, nop the next word, what)
    (0x002EB8EC, 0x0C066218, 0x24050002, "sk_ride", False, "a hero gets on a board: the twin's board is noted"),
    (0x00198910, 0x8DEEE948, 0x0200302D, "sk_who", False, "the board commands open: on the rider's control object"),
    (0x0019898C, 0x3C0F0035, 0x8DEEE948, "sk_off", True, "the board commands close: on the rider's control object"),
)

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''')
rep('''    if "--helper" in sys.argv:         # EXPERIMENT''', '''    if "--no-board" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(BOARD_AT, BOARD_SRC, {"V_TBOARD": V_TBOARD})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert BOARD_AT + 4 * len(code) <= BOARD_END, "board glue too long"
        for i, w in enumerate(code):
            a = BOARD_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the board commands go to the rider's control object)"
        n_glue += len(code)
        for a, w0, w1, routine, nop_next, what in BOARD_HOOKS:
            assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<2I", elf.data, off + a - va)
            assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
            words[a] = (3 << 26) | ((labels[routine] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (board): " + what
            n_glue += 1
            if nop_next:
                words[a + 4] = 0
                order.append(a + 4)
                origin[a + 4] = "glue hook (board): the slot after it"
                n_glue += 1

    if "--helper" in sys.argv:         # EXPERIMENT''')
p.write_text(t, encoding="utf-8")
print("ok")
