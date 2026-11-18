r"""One-off (STATE part 141, after a review): the seventy-ninth glue's THIRD FORM.
  * The script engine's two button tests (the sixteenth glue's calls at 0x0016DBA8 'button held' and 0x0016DBF0 'button pressed':
    the button-mash parts of boss moves) always hear both controllers, as the read-me promises. (Before: a green command in a
    fight made them hear only that player for at least 90 steps, so a grabbed hero whose partner pressed Triangle last could
    not mash.)
  * An owner whose box is open RIGHT NOW (a message window asked less than 4 steps ago; an open box asks every second step) is
    not replaced by the OTHER player's START (po_open) or green command (po_cmd): he cannot take over a talk in the middle.
  python -I tools/merge/edit_merge_v7_menuowner4.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "pp_mash" in t:
    raise SystemExit("already done")


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep("""    ori t7,t7,0xC7A0              # and so does the command menu's first button (the call at 0x0013C798)
    beq ra,t7,po_both
    lui t7,0x000E
""", """    ori t7,t7,0xC7A0              # and so does the command menu's first button (the call at 0x0013C798)
    beq ra,t7,po_both
    lui t7,0x0016
pp_mash:                          # and the script's two button tests (boss button-mashing; calls 0x0016DBA8 / 0x0016DBF0)
    ori t7,t7,0xDBB0
    beq ra,t7,po_both
    lui t7,0x0016
    ori t7,t7,0xDBF8
    beq ra,t7,po_both
    lui t7,0x000E
""")
rep("""poo_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter (0x0034D4BC)
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t3,-6144(t7)               # V_OWNER
poo_go:""", """poo_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter (0x0034D4BC)
    lw t6,-6144(t7)               # the owner now
    beq t6,zero,poo_take
    nop
    beq t6,t3,poo_take
    lw t4,-6136(t7)               # V_MSGSTEP
    subu t4,t5,t4
    sltiu t4,t4,4                 # the other player's box is open right now (an open box asks every second step):
    bne t4,zero,poo_go            # he keeps it
    nop
poo_take:
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t3,-6144(t7)               # V_OWNER
poo_go:""")
rep("""poc_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t4,-6144(t7)               # V_OWNER
poc_go:""", """poc_set:
    lui t7,0x000E
    lui t5,0x0035
    lw t5,-11076(t5)              # the game's counter
    lw t6,-6144(t7)               # the owner now
    beq t6,zero,poc_take
    nop
    beq t6,t4,poc_take
    lw t8,-6136(t7)               # V_MSGSTEP
    subu t8,t5,t8
    sltiu t8,t8,4                 # the other player's box is open right now: he keeps it
    bne t8,zero,poc_go
    nop
poc_take:
    sw t5,-6140(t7)               # V_OWNSTEP
    sw t4,-6144(t7)               # V_OWNER
poc_go:""")
rep("""player's logical controller alone; nobody (0) = both, as before. The field's START look-out (the call at 0x00138538) and the
command menu's first button (0x0013C798) always hear both.""",
    """player's logical controller alone; nobody (0) = both, as before. The field's START look-out (the call at 0x00138538), the
command menu's first button (0x0013C798) and the script's two button tests (0x0016DBA8 / 0x0016DBF0: boss button-mashing)
always hear both. While the owner's box is open (a message window asked less than 4 steps ago) the OTHER player's START or
green command does not take the screen over (third form, edit_merge_v7_menuowner4.py).""")
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the seventy-ninth glue's third form")
