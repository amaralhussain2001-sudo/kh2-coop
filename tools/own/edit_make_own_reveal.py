"""One-off: tools/own/make_own.py, step 7: the menu's "revealed" byte (display+0xFD) is one state for both players."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "make_own.py"
t = p.read_text(encoding="utf-8")
if "SH_FD" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


rep('''oh_p2:
    jal own_swap                  # player 2's rows and list state go into the display
    move a0,s0
    li t6,1
''', '''oh_p2:
    jal own_swap                  # player 2's rows and list state go into the display
    move a0,s0
    lbu t6,{SH_FD}(s1)            # "the menu is revealed" (display+0xFD; the game hides and shows the whole row
    sb t6,0xFD(s0)                # group by it, 0x0013D3F8): one state for both players, here player 1's
    li t6,1
''')
rep('''    jal own_swap                  # player 1's rows and list state come back
    move a0,s0
    sw zero,{O_CSW}(s1)
''', '''    lbu t6,0xFD(s0)               # revealed in player 2's run (his button, his Reaction Command): for both
    sb t6,{SH_FD}(s1)
    jal own_swap                  # player 1's rows and list state come back
    move a0,s0
    sw zero,{O_CSW}(s1)
''')
rep("SH_FE=O_SH + 0xFE - 0x18,", "SH_FE=O_SH + 0xFE - 0x18, SH_FD=O_SH + 0xFD - 0x18,")
p.write_text(t, encoding="utf-8")
print("ok")
