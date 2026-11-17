"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), fourth form (ninth round, job 6).
Seen in run gs3 (third form): the two score rows lay on each other. The digits' places are worked out each step
from the frame picture's layout place; "set place" (0x01F477C0) on the frame picture does not move them.
Now: after each step of row 2 its eight digit pictures (row 2 + 8 .. + 36) are moved by (GQ_ROW_DX, GQ_ROW_DY)
(their own place words, picture + 356 / + 360). Row 2 stands to the RIGHT of the game's row. The gauge's first
picture's place is noted (0x000E7F30 / 34) for the probe.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score4.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "GQ_ROW_DX" in s:
    raise SystemExit("already there")

a = '''GQ_ROW_DY = 22                                     # player 2's row stands this much lower than the game's
'''
assert s.count(a) == 1
s = s.replace(a, '''GQ_ROW_DX = 210                                    # player 2's row stands this much to the right of the game's row
GQ_ROW_DY = 0
''')

i = s.index("    ld t5,32(sp)\n    addiu t4,zero,1\n    bne t5,t4,gqs_mark            # it was not \"make\" before")
j = s.index("gqs_mark:\n", i)
NEW = '''    lw t5,0x7F68(t7)
    addiu t4,zero,2
    bne t5,t4,gqs_mark            # row 2 is not shown
    ori t6,t7,0x7F48              # its digit pictures (row 2 + 8 .. + 36)
    addiu t3,zero,8
gqs_dig:
    lw t2,0(t6)
    beq t2,zero,gqs_dn
    addiu t3,t3,-1
    lw t1,356(t2)
    addiu t1,t1,@ROW_DX@
    sw t1,356(t2)                 # the digit stands in row 2's place
    lw t1,360(t2)
    addiu t1,t1,@ROW_DY@
    sw t1,360(t2)
gqs_dn:
    bne t3,zero,gqs_dig
    addiu t6,t6,4
'''
s = s[:i] + NEW + s[j:]

a = '''    lui t7,0x000E
    lw a0,0x7F78(t7)
    lw a1,16(sp)
    lw a2,20(sp)
    addiu a1,a1,@MARK_DX@
'''
assert s.count(a) == 1
s = s.replace(a, '''    lui t7,0x000E
    lw a0,0x7F78(t7)
    lw a1,16(sp)
    lw a2,20(sp)
    sw a1,0x7F30(t7)              # (the gauge's place, for the probe)
    sw a2,0x7F34(t7)
    addiu a1,a1,@MARK_DX@
''')
a = '''    src = GQ_SRC.replace("@ROW_DY@", str(GQ_ROW_DY))'''
assert s.count(a) == 1
s = s.replace(a, '''    src = GQ_SRC.replace("@ROW_DX@", str(GQ_ROW_DX)).replace("@ROW_DY@", str(GQ_ROW_DY))''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
