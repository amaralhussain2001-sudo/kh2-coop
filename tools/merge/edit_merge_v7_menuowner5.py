r"""One-off (STATE part 141): the seventy-ninth glue's FOURTH FORM. Run r11tk4: during player 2's talk player 1's START PAUSED it
("PAUSE" over player 2's box; START in a talk goes to 0x00253410), because the field's START look-out (return 0x00138540) always
heard both controllers. Now it hears only the owner while his box is open right now (a message window asked less than 4 steps
ago); in the plain field it hears both, as before.
  python -I tools/merge/edit_merge_v7_menuowner5.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "pp_cmdmenu" in t:
    raise SystemExit("already done")


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep("""pp_who:
    lui t7,0x0013
    ori t7,t7,0x8540              # the field's START look-out (the call at 0x00138538) always hears both controllers,
    beq ra,t7,po_both
    lui t7,0x0013
""", """pp_who:
    lui t7,0x0013
    ori t7,t7,0x8540              # the field's START look-out (the call at 0x00138538) hears both controllers,
    bne ra,t7,pp_cmdmenu
    lui t7,0x000E
    lw t6,-6144(t7)               # unless a player's box is open right now: then only he can pause his talk
    beq t6,zero,po_both
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter
    lw t4,-6136(t7)               # V_MSGSTEP
    subu t4,t5,t4
    sltiu t4,t4,4
    beq t4,zero,po_both
    nop
    beq zero,zero,po_own          # (t6 = the owner)
    nop
pp_cmdmenu:
    lui t7,0x0013
""")
rep("""    lw t6,-6144(t7)               # V_OWNER (0x000DE800)
    beq t6,zero,po_both           # nobody owns the screen: both controllers, as before
    addiu t6,t6,-1                # 0 = player 1, 1 = player 2
""", """    lw t6,-6144(t7)               # V_OWNER (0x000DE800)
    beq t6,zero,po_both           # nobody owns the screen: both controllers, as before
    nop
po_own:                           # t6 = the owner (1 or 2)
    addiu t6,t6,-1                # 0 = player 1, 1 = player 2
""")
rep("""command menu's first button (0x0013C798) and the script's two button tests (0x0016DBA8 / 0x0016DBF0: boss button-mashing)
always hear both.""", """command menu's first button (0x0013C798) and the script's two button tests (0x0016DBA8 / 0x0016DBF0: boss button-mashing)
always hear both (the START look-out only the owner while his box is open: fourth form, edit_merge_v7_menuowner5.py).""")
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the seventy-ninth glue's fourth form")
