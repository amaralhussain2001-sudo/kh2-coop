r"""One-off (STATE part 141): the seventy-ninth glue's SECOND FORM. Found by run r11mo1e (probe tools/own/mo_probe.py): in a talk the
field goes on (its START look-out runs every step; START would give the skip menu), so po_tick let the owner go 34 steps after
player 2's Talk, long before the elf's "Make presents?" box. Now:
  * po_pad notes the game's counter whenever a MESSAGE WINDOW asks for its controller (the call at 0x001ACBD4; V_MSGSTEP
    0x000DE808);
  * po_tick lets the owner go only when the owner is at least MO_HOLD (90) steps old AND no message window asked for
    MO_MSGHOLD (30) steps. So a talk keeps its owner for as long as its boxes come, and a shop / the pause menu as before.
  python -I tools/merge/edit_merge_v7_menuowner2.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "V_MSGSTEP" in t:
    raise SystemExit("already done")


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep("""V_OWNSTEP = 0x000DE804                             # the game's counter (0x0034D4BC) when the owner was set
MO_HOLD = 30                                       # steps the owner outlives the field's START look-out (the screen comes)
""", """V_OWNSTEP = 0x000DE804                             # the game's counter (0x0034D4BC) when the owner was set
V_MSGSTEP = 0x000DE808                             # the game's counter when a message window last asked for its controller
MO_HOLD = 90                                       # steps the owner outlives the field's START look-out (the screen comes)
MO_MSGHOLD = 30                                    # and steps after the last message window's question (a talk goes on)
""")
rep("""po_pad:                           # the second glue's pad_both (0x000F4740) jumps here first. Out: v0 = the record. t2-t7
    lui t7,0x0013
""", """po_pad:                           # the second glue's pad_both (0x000F4740) jumps here first. Out: v0 = the record. t2-t7
    lui t7,0x001B
    ori t7,t7,0xCBDC              # a message window asks (the call at 0x001ACBD4): note the counter (a talk goes on)
    bne ra,t7,pp_who
    lui t7,0x0035
    lw t6,-11076(t7)              # the game's counter (0x0034D4BC)
    lui t7,0x000E
    sw t6,-6136(t7)               # V_MSGSTEP
pp_who:
    lui t7,0x0013
""")
rep("""    lw t4,-6140(t7)               # V_OWNSTEP
    subu t5,t5,t4
    sltiu t5,t5,MO_HOLD           # set less than MO_HOLD steps ago: what it opens is still coming
    bne t5,zero,pt_go
    nop
    sw zero,-6144(t7)             # the field runs again: nobody owns the screen
""", """    lw t4,-6140(t7)               # V_OWNSTEP
    subu t4,t5,t4
    sltiu t4,t4,MO_HOLD           # set less than MO_HOLD steps ago: what it opens is still coming
    bne t4,zero,pt_go
    lw t4,-6136(t7)               # V_MSGSTEP
    subu t4,t5,t4
    sltiu t4,t4,MO_MSGHOLD        # a message window asked less than MO_MSGHOLD steps ago: the talk goes on
    bne t4,zero,pt_go
    nop
    sw zero,-6144(t7)             # the field runs again and no box is open: nobody owns the screen
""")
rep("""                "CMD_NEXT": (cmd_next & 0x3FFFFFF) << 2, "MO_HOLD": MO_HOLD}
        assert V_OWNER == 0x000E0000 - 6144 and V_OWNSTEP == V_OWNER + 4""",
    """                "CMD_NEXT": (cmd_next & 0x3FFFFFF) << 2, "MO_HOLD": MO_HOLD, "MO_MSGHOLD": MO_MSGHOLD}
        assert V_OWNER == 0x000E0000 - 6144 and V_OWNSTEP == V_OWNER + 4 and V_MSGSTEP == V_OWNER + 8""")
rep("""(V_OWNSTEP 0x000DE804). po_tick (the field's START look-out, each field step) sets nobody again once the owner is 30 steps old
(what a green command opens comes a few steps later).""",
    """(V_OWNSTEP 0x000DE804). po_tick (the field's START look-out, each field step) sets nobody again once the owner is 90 steps old
AND no message window asked for its controller for 30 steps (V_MSGSTEP 0x000DE808, noted by po_pad): in a talk the field goes
on, so the talk keeps its owner as long as its boxes come (second form, edit_merge_v7_menuowner2.py, after run r11mo1e).""")
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the seventy-ninth glue's second form")
