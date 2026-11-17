"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), fifth form (ninth round, job 6).
Seen in run gt3 (fourth form): player 2's digits stand to the right of the score frame (0015560 = his points),
but the game's own row was EMPTY: row 2's frame picture (made after the game's digits) lay on them. And the
gauge's digit was not seen: the gauge's first picture's place is (0, 0) (its layout places it), so the digit
stood outside the picture.
Now: row 2's frame picture is put outside the picture each step (its place word + 356 = 3000); the gauge's
digit stands at a fixed place (GQ_MARK_X, GQ_MARK_Y) left of the gauge. (The picture's places count 512 across.)
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score5.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "GQ_MARK_X" in s:
    raise SystemExit("already there")

a = '''GQ_MARK_DX = -18                                   # the gauge's digit: from the gauge's first picture
GQ_MARK_DY = -6
'''
assert s.count(a) == 1
s = s.replace(a, '''GQ_MARK_X = 388                                    # the gauge's digit: left of the hull gauge (places count 512 across, 448 down)
GQ_MARK_Y = 396
''')

a = '''    ori t6,t7,0x7F48              # its digit pictures (row 2 + 8 .. + 36)
    addiu t3,zero,8
'''
assert s.count(a) == 1
s = s.replace(a, '''    ori t6,t7,0x7F48              # its digit pictures (row 2 + 8 .. + 36)
    lw t2,0x7F44(t7)              # its frame picture would lie on the game's digits: out of the picture
    beq t2,zero,gqs_nf
    addiu t1,zero,3000
    sw t1,356(t2)
gqs_nf:
    addiu t3,zero,8
''')

i = s.index("gqs_pos:\n")
j = s.index("gqs_out:\n", i)
s = s[:i] + '''gqs_pos:
    lui t7,0x000E
    lw a0,0x7F78(t7)
    addiu a1,zero,@MARK_X@
    jal 0x01F477C0                # the digit's place
    addiu a2,zero,@MARK_Y@
''' + s[j:]

a = '''.replace("@MARK_DX@", str(GQ_MARK_DX)).replace("@MARK_DY@", str(GQ_MARK_DY))'''
assert s.count(a) == 1
s = s.replace(a, '''.replace("@MARK_X@", str(GQ_MARK_X)).replace("@MARK_Y@", str(GQ_MARK_Y))''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
