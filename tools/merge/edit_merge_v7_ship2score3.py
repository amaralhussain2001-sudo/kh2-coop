"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), third form (ninth round, job 6, second
half): A SECOND SCORE ROW (player 2's points) UNDER THE GAME'S, and A DIGIT BESIDE THE HULL GAUGE that says whose
ship the gauge shows.
Read in the flight module: the score on screen is an object (the HUD's part at + 88): start 0x01F67748 (state 1),
step 0x01F67D40 (1: make 0x01F67768, 2: show 0x01F67968, 3: fade out), end 0x01F67758 (state 3), free 0x01F676A8;
"show" reads the score with the call at 0x01F679A8 and lays the digits out from its frame picture (+ 4). The hull
gauge is the HUD's part at + 140 (its first picture at + 4). Pictures: the HUD's sheet 0x01F48038(), a new picture
0x01F46E80(sheet, group, number), its place 0x01F47690(picture, &x, &y) / 0x01F477C0(picture, x, y), its number
0x01F47A58(picture) / 0x01F47A10(picture, number); a digit is group 8 number 72 with the picture numbers 52 + 2 x
digit.
What is added (four more jumps and one call written by gq_inst):
  gq_sdstart / gq_sdend / gq_sdfree / gq_sdstep: whatever the game does with its score row, it does with a second
      score object in the patch's memory (0x000E7F40) too; when row 2 is made, its frame picture is set GQ_ROW_DY
      lower.
  gq_get (the call at 0x01F679A8): row 2 shows player 2's points, the game's row shows the score - player 2's
      points = player 1's. The game's own score (the mission's result) is not touched.
  the mark (0x000E7F78): while row 2 is shown, a digit beside the gauge's first picture: 1 or 2 = the ship with
      the lower hull (the fifty-first glue shows that ship's hull in the gauge).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gq_sdstep" in s:
    raise SystemExit("already there")

# (1) the new places
a = '''    (0x01F4DE70, 0x27BDFFF0, "gq_reset"),          # the score is set to 0
)
'''
assert s.count(a) == 1
s = s.replace(a, '''    (0x01F4DE70, 0x27BDFFF0, "gq_reset"),          # the score is set to 0
    (0x01F67D40, 0x27BDFFF0, "gq_sdstep"),         # the score row's step
    (0x01F67748, 0x240F0001, "gq_sdstart"),        # the score row starts
    (0x01F67758, 0x240F0003, "gq_sdend"),          # the score row ends
    (0x01F676A8, 0x27BDFFE0, "gq_sdfree"),         # the score row is freed
)
GQ_CALLS = (                                       # (a call in the flight module, its word, the routine that is called in its place)
    (0x01F679A8, 0x0C7D37B4, "gq_get"),            # the score row reads the score
)
GQ_ROW_DY = 22                                     # player 2's row stands this much lower than the game's
GQ_MARK_DX = -18                                   # the gauge's digit: from the gauge's first picture
GQ_MARK_DY = -6
''')

# (2) the routines
a = '''gq_reset:                         # 0x01F4DE70: the score is set to 0 (a new flight)
'''
assert s.count(a) == 1
NEW = '''gq_get:                           # the call at 0x01F679A8 (was 0x01F4DED0 "the score"): the row that is being shown asks
    lui t7,0x000E
    lw t6,0x7F7C(t7)              # row 2 is in work
    lw t5,0x7EFC(t7)              # player 2's points
    bne t6,zero,gqg_2
    lui t4,0x01F8
    lw v0,0x039C(t4)              # the game's score
    jr ra
    subu v0,v0,t5                 # the game's row: player 1's points
gqg_2:
    jr ra
    move v0,t5

gq_sdstart:                       # 0x01F67748(a0 = the score row): it starts (the whole routine)
    addiu t7,zero,1
    sb zero,48(a0)
    sw t7,40(a0)
    lui t6,0x000E
    sb zero,0x7F70(t6)            # row 2 too
    sw t7,0x7F68(t6)
    lui t5,0x3F80
    jr ra
    sw t5,0x7F6C(t6)              # (its start value 1.0, as the game's row has from its builder)

gq_sdend:                         # 0x01F67758(a0 = the score row): it ends (the whole routine)
    addiu t7,zero,3
    sw t7,40(a0)
    lui t6,0x000E
    jr ra
    sw t7,0x7F68(t6)

gq_sdfree:                        # 0x01F676A8(a0 = the score row): its pictures are freed
    lui t7,0x000E
    ori t6,t7,0x7F40
    beq a0,t6,gqd_body            # (the call for row 2 itself)
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gqd_body                  # the game's row
    nop
    lui t7,0x000E
    jal gqd_body                  # row 2
    ori a0,t7,0x7F40
    lui t7,0x000E
    lw a0,0x7F78(t7)              # the gauge's digit
    sw zero,0x7F68(t7)
    beq a0,zero,gqd_1
    sw zero,0x7F78(t7)
    lw t6,0(a0)
    lw t6,4(t6)
    jalr t6                       # the picture is ended as the game ends its own
    nop
gqd_1:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gqd_body:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F676A8
    j 0x01F676B0
    sd s2,16(sp)

gq_sdstep:                        # 0x01F67D40(a0 = the score row): its step
    lui t7,0x000E
    ori t6,t7,0x7F40
    beq a0,t6,gqs_body            # (the call for row 2 itself)
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal gqs_body                  # the game's row
    nop
    lui t7,0x000E
    lw t5,0x7F68(t7)              # row 2's state before its step
    sd t5,32(sp)
    addiu t4,zero,1
    sw t4,0x7F7C(t7)              # row 2 is in work
    jal gqs_body
    ori a0,t7,0x7F40
    lui t7,0x000E
    sw zero,0x7F7C(t7)
    ld t5,32(sp)
    addiu t4,zero,1
    bne t5,t4,gqs_mark            # it was not "make" before
    lw t3,0x7F68(t7)
    addiu t4,zero,2
    bne t3,t4,gqs_mark            # it is not made now
    lw a0,0x7F44(t7)              # JUST MADE: its frame picture
    beq a0,zero,gqs_mark
    addiu a1,sp,16
    jal 0x01F47690                # its place
    addiu a2,sp,20
    lui t7,0x000E
    lw a0,0x7F44(t7)
    lw a1,16(sp)
    lw a2,20(sp)
    jal 0x01F477C0                # ... is set lower
    addiu a2,a2,@ROW_DY@
gqs_mark:
    lui t7,0x000E
    lw t5,0x7F68(t7)
    addiu t4,zero,2
    bne t5,t4,gqs_out             # row 2 is not shown: no digit work
    lw t3,0x7F78(t7)
    bne t3,zero,gqs_have
    nop
    jal 0x01F48038                # the HUD's picture sheet
    nop
    move a0,v0
    addiu a1,zero,8
    jal 0x01F46E80                # a new picture: a digit
    addiu a2,zero,72
    lui t7,0x000E
    beq v0,zero,gqs_out
    sw v0,0x7F78(t7)
gqs_have:
    lui t6,0x000F
    lw t5,0x2600(t6)              # ship 1
    lw t4,0x2604(t6)              # ship 2
    addiu t3,zero,54              # the digit 1
    beq t5,zero,gqs_num
    nop
    beq t4,zero,gqs_num
    nop
    lwc1 f0,0x4AC(t5)             # the hulls
    lwc1 f1,0x4AC(t4)
    c.lt.s f1,f0
    bc1f gqs_num                  # ship 2's is not the lower one
    nop
    addiu t3,zero,56              # the digit 2
gqs_num:
    sd t3,24(sp)
    jal 0x01F47A58                # the digit's picture number now
    lw a0,0x7F78(t7)
    ld a1,24(sp)
    beq v0,a1,gqs_pos
    lui t7,0x000E
    jal 0x01F47A10                # another one
    lw a0,0x7F78(t7)
gqs_pos:
    ld t5,8(sp)                   # the game's score row; the hull gauge is the HUD's next part (+ 52)
    lw a0,56(t5)                  # the gauge's first picture
    beq a0,zero,gqs_out
    addiu a1,sp,16
    jal 0x01F47690                # its place
    addiu a2,sp,20
    lui t7,0x000E
    lw a0,0x7F78(t7)
    lw a1,16(sp)
    lw a2,20(sp)
    addiu a1,a1,@MARK_DX@
    jal 0x01F477C0
    addiu a2,a2,@MARK_DY@
gqs_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
gqs_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F67D40
    j 0x01F67D48
    addiu t7,zero,1

'''
s = s.replace(a, NEW + a)

# (3) the installer also writes the calls; the three numbers go into the source
a = '''    return GQ_SRC.replace("@CHECKS@", checks.rstrip("\\n")).replace("@WRITES@", writes.rstrip("\\n"))
'''
assert s.count(a) == 1, s.count(a)
b = '''    for site, word0, name in GQ_CALLS:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\\n    lw t5,%d(t7)                 # 0x%08X: still the game's call?\\n    lui t4,0x%04X\\n"
                   "    ori t4,t4,0x%04X\\n    bne t5,t4,gqi_go\\n    nop\\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((3 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: jal %s\\n"
                   ) % (hi, j >> 16, j & 0xFFFF, lo, site, name)
    src = GQ_SRC.replace("@ROW_DY@", str(GQ_ROW_DY)).replace("@MARK_DX@", str(GQ_MARK_DX)).replace("@MARK_DY@", str(GQ_MARK_DY))
    return src.replace("@CHECKS@", checks.rstrip("\\n")).replace("@WRITES@", writes.rstrip("\\n"))
'''
s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
