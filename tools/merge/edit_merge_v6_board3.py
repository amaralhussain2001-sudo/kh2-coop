"""One-off: eleventh glue of tools/merge/merge_v6.py, third version = the first one again (the routines' object IS
the board; the recorder of test n4-mail-dbg showed it), with the reason why its note stayed empty in the test."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "V_TBOARD" in t:
    raise SystemExit("already done")
a = t.index("when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(board, hero) -> 0x00198860(hero, 2)) the board")
b = t.index("  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--helper] [--react]")
t = t[:a] + """when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(hero, board) -> 0x00198860(board, 2)) the board
commands are opened on the control object of THE ENGINE'S PLAYER (load at 0x00198910, then 0x001BDB70), and
when the board is left (0x00198970(board), also run first by 0x00198860 for a board that is in use) they are
closed on that one too (load at 0x00198990). VERIFIED with a recorder at 0x001BDBD4 (test n4-mail-dbg): the
object of both routines is the board; the hero is s0 of 0x002EB890.
Now: the ride call (0x002EB8EC) notes the board when the rider is the twin (V_TBOARD); for that board the two
places take the twin (his control object, lane G's S2, object+0xB44); for every other board or vehicle the
engine's player as before (the two routines have 12 and 6 callers). Routines sk_ride, sk_who, sk_off at
0x000F4F00.
(In the first test both riders had been put on ONE board by the mission script, see tools/lane-s1/make_mail.py;
the second ride then "left" the board first, which emptied the note. A second version that compared the
routines' object with the twin was wrong.)

""" + t[b:]
a = t.index('BOARD_SRC = """')
b = t.index("REACT_AT = 0x000F4A00", a)
t = t[:a] + '''V_TBOARD = 0x000F47F0             # the board the twin rides (0 = none)
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
    lw t6,0x05CC(t5)
    bne t6,zero,sko_out           # (the note stays: 0x00198860 runs this first for a board in use)
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

''' + t[b:]
old = '''        code, labels = assemble(BOARD_AT, BOARD_SRC, {})'''
assert t.count(old) == 1
t = t.replace(old, '''        code, labels = assemble(BOARD_AT, BOARD_SRC, {"V_TBOARD": V_TBOARD})''')
p.write_text(t, encoding="utf-8")
print("ok")
