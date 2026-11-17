"""One-off: tools/merge/merge_v7.py gets the FIFTY-FIRST GLUE (built only with --ship2hit; an experiment until its
runs are read): PLAYER 2'S GUMMI SHIP CAN BE HIT AND HAS ITS OWN HULL (the vehicle items of the eighth round).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2hit.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gs_test" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-FIRST GLUE (built only with the option --ship2hit): PLAYER 2'S GUMMI SHIP CAN BE HIT AND HAS ITS OWN HULL.
What was there (lane S3, and the seventh round, part 7c): the second ship of the twenty-seventh glue is never
damaged; its hull stays at its first value while ship 1's goes down.
Read in the flight module (ovl_gumibattle.x at 0x01F18000): every kind of enemy shot asks for "the player ship"
with the getter 0x01F21CF8 (132 callers; the pointer 0x01F7DE44), makes a ball of its own place and size
(0x01F406E0) and asks the SHIP "does this ball touch you" (0x01F217C8(ship, ball)), then "can you be hit now"
(0x01F217A8(ship)), then calls the ship's "you are hit" (0x01F20320(ship, hit record); five callers) or its
"take damage" (0x01F203A8(ship, amount); two more callers). "Take damage" takes the amount off the hull in the
ship's own status record (ship + 0x4A8; 0x01F23320) and starts the end of the ship when the hull is 0. All of
these routines work on the ship they are handed. Only the question is asked about ship 1 alone.
gs_inst (the call at 0x00167E90, before the twenty-sixth glue's gm_pad): when a fresh flight module is in memory
  (its mark 0x636A and the four places still the game's own words), four jumps are written into it.
gs_test (0x01F217C8): the question about ship 1 is asked for ship 1 first; when ship 1 is not touched and ship 2
  is under control (state 2), it is asked for ship 2; when ship 2 is touched, "the hit is ship 2's" is noted
  (0x000E7E4C). Every new question clears the note.
gs_able (0x01F217A8), gs_hit (0x01F20320), gs_dmg (0x01F203A8): while the note stands, a call for ship 1 is a
  call for ship 2; "you are hit" and "take damage" use the note up.
NOT KNOWN before the runs: what the flight does when SHIP 2's hull is 0 (the game's own end of the mission is
started by "take damage" for whichever ship it is handed).

'''
s = s.replace(a, hdr + a)
b = " [--together [--together-far]]"
assert s.count(b) == 1
s = s.replace(b, b + " [--ship2hit]")

i = s.index("def main():")
src = '''# ---- fifty-first glue, an experiment (only with --ship2hit) ------------------------------------------------
GS_AT = 0x000EB000
GS_END = 0x000EB400
GS_SRC = """
gs_inst:                          # from 0x00167E90 (was the base's jal gm_pad): a fresh flight module gets four jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gi_go
    lw t5,0x17C8(t7)              # 0x01F217C8 "does this ball touch you": still addiu sp,sp,-128?
    lui t4,0x27BD
    ori t4,t4,0xFF80
    bne t5,t4,gi_go
    lw t5,0x17A8(t7)              # 0x01F217A8 "can you be hit now": still addiu sp,sp,-16?
    lui t4,0x27BD
    ori t4,t4,0xFFF0
    bne t5,t4,gi_go
    lw t5,0x0320(t7)              # 0x01F20320 "you are hit": still addiu sp,sp,-32?
    lui t4,0x27BD
    ori t4,t4,0xFFE0
    bne t5,t4,gi_go
    lw t5,0x03A8(t7)              # 0x01F203A8 "take damage": the same word
    bne t5,t4,gi_go
    lui t4,@J_TEST_HI@
    ori t4,t4,@J_TEST_LO@
    sw t4,0x17C8(t7)              # j gs_test
    sw zero,0x17CC(t7)
    lui t4,@J_ABLE_HI@
    ori t4,t4,@J_ABLE_LO@
    sw t4,0x17A8(t7)              # j gs_able
    sw zero,0x17AC(t7)
    lui t4,@J_HIT_HI@
    ori t4,t4,@J_HIT_LO@
    sw t4,0x0320(t7)              # j gs_hit
    sw zero,0x0324(t7)
    lui t4,@J_DMG_HI@
    ori t4,t4,@J_DMG_LO@
    sw t4,0x03A8(t7)              # j gs_dmg
    sw zero,0x03AC(t7)
    lui t4,0x000E
    sw zero,0x7E4C(t4)
gi_go:
    j GM_NEXT                     # the twenty-sixth glue's gm_pad
    nop
gs_test:                          # 0x01F217C8(a0 = a ship, a1 = a ball): does the ball touch the ship
    lui t7,0x000F
    lw t6,0x2604(t7)              # ship 2
    beq t6,zero,gt_orig
    lw t5,0x2600(t7)              # ship 1
    bne a0,t5,gt_orig             # asked about something else
    lui t4,0x000E
    sw zero,0x7E4C(t4)            # a new question: no hit of ship 2 is waiting
    lw t3,0x50C(t6)
    addiu t2,zero,2
    bne t3,t2,gt_orig             # ship 2 is not under control (flying in, done, destroyed)
    lw t3,0x1438(t6)
    andi t3,t3,0x10
    bne t3,zero,gt_orig           # ship 2 is at its end already
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a1,16(sp)
    sd t6,24(sp)
    jal gt_orig                   # ship 1 first
    nop
    bne v0,zero,gt_done           # ship 1 is touched: as the game
    ld a0,24(sp)
    jal gt_orig                   # the same ball and ship 2
    ld a1,16(sp)
    beq v0,zero,gt_done
    lui t4,0x000E
    ld t6,24(sp)
    sw t6,0x7E4C(t4)              # ship 2 is touched: the calls that follow are ship 2's
gt_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
gt_orig:
    addiu sp,sp,-128              # the two instructions that sat at 0x01F217C8
    j 0x01F217D0
    sd s1,88(sp)
gs_able:                          # 0x01F217A8(a0 = a ship): can it be hit now
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,ga_go
    lui t5,0x000F
    lw t5,0x2600(t5)
    bne a0,t5,ga_go
    nop
    move a0,t6                    # the hit that is waiting is ship 2's
ga_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F217A8
    j 0x01F217B0
    sd ra,0(sp)
gs_hit:                           # 0x01F20320(a0 = a ship, a1 = the hit record): you are hit
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,gh_go
    lui t5,0x000F
    lw t5,0x2600(t5)
    bne a0,t5,gh_go
    nop
    move a0,t6
    sw zero,0x7E4C(t7)            # used up
gh_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F20320
    j 0x01F20328
    sd s0,0(sp)
gs_dmg:                           # 0x01F203A8(a0 = a ship, a1 = the amount): take damage
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,gd_go
    lui t5,0x000F
    lw t5,0x2600(t5)
    bne a0,t5,gd_go
    nop
    move a0,t6
    sw zero,0x7E4C(t7)            # used up
gd_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F203A8
    j 0x01F203B0
    sd s0,0(sp)
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--ship2hit" in sys.argv:                                           # fifty-first glue, an experiment (player 2's Gummi ship can be hit)
        gm_next = words[0x00167E90]                                        # the base's jal gm_pad (twenty-sixth glue)
        assert (gm_next >> 26) == 3
        syms = {"GM_NEXT": (gm_next & 0x3FFFFFF) << 2}
        src = GS_SRC
        for k in ("TEST", "ABLE", "HIT", "DMG"):                           # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        code, labels = assemble(GS_AT, src, syms)
        src = GS_SRC
        for k, lab in (("TEST", "gs_test"), ("ABLE", "gs_able"), ("HIT", "gs_hit"), ("DMG", "gs_dmg")):
            j = (2 << 26) | ((labels[lab] >> 2) & 0x3FFFFFF)
            src = src.replace("@J_%s_HI@" % k, "0x%04X" % (j >> 16)).replace("@J_%s_LO@" % k, "0x%04X" % (j & 0xFFFF))
        labels2, n = add_code(GS_AT, GS_END, src, syms, "EXPERIMENT: player 2's Gummi ship can be hit and has its own hull")
        assert labels2 == labels
        hook_base(0x00167E90, gm_next, jal(labels["gs_inst"]), "the controller task: first the four jumps into a fresh flight module, then gm_pad")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
