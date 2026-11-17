"""One-off: eleventh glue of tools/merge/merge_v6.py, second version: 0x00198860 / 0x00198970 get the HERO (not
the board), so no note of the board is needed."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "V_TBOARD" not in t:
    raise SystemExit("already done")
a = t.index("when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(hero, board) -> 0x00198860(board, 2)) the board")
b = t.index("  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--helper] [--react]")
t = t[:a] + """when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(board, hero) -> 0x00198860(hero, 2)) the board
commands are opened on the control object of THE ENGINE'S PLAYER (load at 0x00198910, then 0x001BDB70), and
when he gets off (0x00198970(hero)) they are closed on that one too (load at 0x00198990). Both routines have
the hero in a register (s2 / s0) and do not use it for this.
Now: when that hero is the twin, his own control object is taken (lane G's S2, object+0xB44); for every other
object the engine's player as before (the two routines have 12 and 6 callers, vehicles of other kinds too).
Routines sk_who, sk_off at 0x000F4F00.
(First version, wrong reading: it took the routines' object for the board and noted "the twin's board" at the
ride call; the note never matched. Test n3-mail-board.)

""" + t[b:]
a = t.index("V_TBOARD = 0x000F47F0")
b = t.index("REACT_AT = 0x000F4A00", a)
t = t[:a] + '''BOARD_SRC = """
sk_who:                           # hook 0x00198910 (was: lw t6,-5816(t7), the engine's player). s2 = the hero
    lui t5,0x000F                 # that gets on. Out: t6 = the hero whose control object gets the board commands
    lw t6,0x05CC(t5)              # the twin (lane E's pointer, 0 = none)
    beq t6,s2,skw_out             # the twin gets on: his own
    lui t7,0x0035
    lw t6,-5816(t7)
skw_out:
    jr ra
    nop
sk_off:                           # hook 0x0019898C (0x00198990 is now a nop). s0 = the hero that gets off.
    lui t5,0x000F                 # Out: t6 = the hero whose control object leaves the board commands
    lw t6,0x05CC(t5)
    beq t6,s0,sko_out
    lui t7,0x0035
    lw t6,-5816(t7)
sko_out:
    jr ra
    nop
"""
BOARD_HOOKS = (                   # (address, word expected, word after it expected, routine, nop the next word, what)
    (0x00198910, 0x8DEEE948, 0x0200302D, "sk_who", False, "the board commands open: on the rider's control object"),
    (0x0019898C, 0x3C0F0035, 0x8DEEE948, "sk_off", True, "the board commands close: on the rider's control object"),
)

''' + t[b:]
old = '''        code, labels = assemble(BOARD_AT, BOARD_SRC, {"V_TBOARD": V_TBOARD})'''
assert t.count(old) == 1
t = t.replace(old, '''        code, labels = assemble(BOARD_AT, BOARD_SRC, {})''')
p.write_text(t, encoding="utf-8")
print("ok")
