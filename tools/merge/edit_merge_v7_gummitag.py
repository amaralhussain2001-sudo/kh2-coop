"""ONE-OFF EDIT (tenth round, 2026-11-16; RUN ONCE, never again): THE SEVENTY-EIGHTH GLUE --gummitag = the Gummi points of
weapons other than cannons go to the ship that fired (the research agent's design "gt", local/research/gummi-gt_proposal.asm.txt).

Why glue 77 (--gummiall) failed: its code lay INSIDE glue 66's old shots' table (0x000EE800 .. 0x000EF7FF); a cannon shot's mark
changed its "lw t3,0x40(a0)" at 0x000EF170 into "lw t3,1(a0)" (STATE part 130). Since build 23 that table is at 0x000DF000.
Glue 77 stays in the builder and stays out of builds; this glue uses the same room 0x000EF000 .. 0x000EF400 (no patch word,
no runtime table there; the enemies' table 0x000EF800 .. 0x000EFFFF stays free) and the two cannot be built together.

Design (no table, no "fires now" word): when a generic or a special weapon fires (0x01F49B38, 0x01F4A6E8; a0 = the weapon),
gt_tag writes 0xA501 / 0xA502 into the weapon's hit values + 30 (weapon + 110, two padding bytes) when its owner block hangs on
ship 1 / 2 (owner = weapon + 0x40, block + 0x4A4 = ship + 0x3E0), else 0. Every shot copies the 48 hit values (shot + 72), so every
hit record carries the tag. gq_hit's first word jumps to gt_hit: the cannon shots' own call (ra 0x01F54278) goes on in gq_hit
unchanged (glue 66's table, as build 23); another call takes the tag (no tag, or a ram block's call 0x01F36D1C: player 1's, as
build 23) for the credit and the enemies' table. The "10 points" (0x01F26D00) and "100 / 1000 points" (0x01F27A40) hits set the
credit from the tag when there is one; without a tag (a cannon shot: cannons are not tagged) the credit stays as it was (build 23).
Registers: t4 .. t9 only (the routines take a0 .. a2; the hit routine also tolerates gq_hit's t1).
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
F = ROOT / "tools" / "merge" / "merge_v7.py"
BAK = ROOT / "local" / "merge_v7-before-gummitag.py"

src = F.read_text(encoding="utf-8")
assert "--gummitag" not in src, "already run"
assert not BAK.exists(), "backup exists: already run?"
shutil.copyfile(F, BAK)


def once(old, new):
    global src
    assert src.count(old) == 1, (src.count(old), old[:60])
    src = src.replace(old, new)


# 1. the header: the glue's paragraph and its option in the usage line
once("""are credited by it.

  python -I tools/merge/merge_v7.py [outDir]""", """are credited by it.

SEVENTY-EIGHTH GLUE (built only with the option --gummitag, needs --ship2score, never with --gummiall): THE GUMMI POINTS OF
WEAPONS OTHER THAN CANNONS GO TO THE SHIP THAT FIRED (design "gt"). gt_inst gives a fresh flight module four jumps: a generic or a
special weapon's fire (0x01F49B38, 0x01F4A6E8) writes the firing ship as a tag 0xA501 / 0xA502 into the weapon's hit values + 30
(weapon + 110, padding), which every shot and so every hit record copies; the "10 points" (0x01F26D00) and "100 / 1000 points"
(0x01F27A40) hits take the tag for the credit. gq_hit's first word jumps to gt_hit: the cannon shots' call keeps glue 66's table
(as build 23), every other call takes the tag (none: player 1's, as before). Room 0x000EF000 .. 0x000EF400 (glue 77's).

  python -I tools/merge/merge_v7.py [outDir]""")
once("[--holdpair]", "[--holdpair] [--gummitag]")

# 2. the source, after glue 77's
once("""# ---- sixty-sixth glue (only with --ship2score) --------------------------------------------------------------
""", '''# ---- seventy-eighth glue (only with --gummitag) --------------------------------------------------------------
GT_AT = 0x000EF000                                 # (glue 77's room; the two are never built together)
GT_END = 0x000EF400
GT_SITES = (                                       # (the place in the flight module, its first word, the routine)
    (0x01F49B38, 0x27BDFFA0, "gt_gen"),            # a generic weapon fires one shot (a0 = the weapon, a1, a2)
    (0x01F4A6E8, 0x27BDFFA0, "gt_spc"),            # a special weapon fires (a0 = the weapon)
    (0x01F26D00, 0x27BDFFF0, "gt_h10"),            # "10 points": a hit without damage (a1 = the shot + 72)
    (0x01F27A40, 0x27BDFFF0, "gt_h100"),           # "100 / 1000 points" (its only call 0x01F5BAD4: a1 = the shot + 72)
)
GT_SRC = """
gt_inst:                          # from 0x00167E90 (the controller task, every frame): a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gti_go
    nop
@CHECKS@
@WRITES@
gti_go:
    j GT_NEXT
    nop

gt_gen:                           # 0x01F49B38(a0 = a generic weapon, a1, a2): it fires one shot
    daddu t9,ra,zero
    jal gt_tag
    nop
    daddu ra,t9,zero
    addiu sp,sp,-96               # the two instructions that sat at 0x01F49B38
    j 0x01F49B40
    addiu t7,a0,80

gt_spc:                           # 0x01F4A6E8(a0 = a special weapon): it fires
    daddu t9,ra,zero
    jal gt_tag
    nop
    daddu ra,t9,zero
    addiu sp,sp,-96               # the two instructions that sat at 0x01F4A6E8
    j 0x01F4A6F0
    sd s2,64(sp)

gt_tag:                           # a0 = a weapon -> weapon + 110 = 0xA501 / 0xA502 (its owner block hangs on ship 1 / 2), else 0
    lw t4,0x40(a0)                # the owner (a block for a player's weapon)
    andi t5,t4,3
    bne t5,zero,gtt_0             # no aligned pointer
    lui t5,0x0010
    sltu t6,t4,t5
    bne t6,zero,gtt_0             # below 0x00100000
    lui t5,0x0200
    addiu t5,t5,-4096
    sltu t6,t4,t5
    beq t6,zero,gtt_0             # at or above 0x01FFF000
    lui t5,0x000F
    lw t4,0x4A4(t4)               # the block's parent
    lw t6,0x2600(t5)              # ship 1
    ori t7,zero,0xA501
    beq t6,zero,gtt_s2
    addiu t6,t6,0x3E0
    beq t4,t6,gtt_w
    nop
gtt_s2:
    lw t6,0x2604(t5)              # ship 2
    ori t7,zero,0xA502
    beq t6,zero,gtt_0
    addiu t6,t6,0x3E0
    beq t4,t6,gtt_w
    nop
gtt_0:
    move t7,zero
gtt_w:
    jr ra
    sh t7,110(a0)                 # the hit values + 30: copied into every shot (shot + 72 + 30) and so into every hit record

gt_who:                           # a1 = a hit record -> t7 = 1 / 2 (the ship that fired), 0 = not known. t4 .. t7 only
    andi t4,a1,3
    bne t4,zero,gtw_0
    lui t5,0x0010
    sltu t4,a1,t5
    bne t4,zero,gtw_0
    lui t5,0x0200
    addiu t5,t5,-32
    sltu t4,a1,t5
    beq t4,zero,gtw_0             # at or above 0x01FFFFE0
    nop
    lhu t4,30(a1)                 # the tag
    srl t5,t4,8
    addiu t6,zero,0xA5
    bne t5,t6,gtw_0
    andi t7,t4,0xFF
    sltiu t5,t7,3                 # 0, 1, 2 only
    bne t5,zero,gtw_out
    nop
gtw_0:
    move t7,zero
gtw_out:
    jr ra
    nop

gt_hit:                           # from gq_hit's first word (its delay slot "lui t1,0x01F5" ran): 0x01F26998(a0 = an enemy, a1 = the hit record)
    lui t8,0x01F5
    ori t8,t8,0x4278              # the cannon shots' own call: glue 66's shots' table, as build 23
    bne ra,t8,gth_tag
    nop
    j GQH_NEXT                    # gq_hit + 4
    lui t7,0x000E                 # gq_hit's first word
gth_tag:
    daddu t9,ra,zero
    lui t8,0x01F3
    ori t8,t8,0x6D1C              # 0x01F36D14's call: a ram block's record on its own stack (no shot, no tag)
    beq ra,t8,gth_k
    addiu t7,zero,1
    jal gt_who
    nop
    daddu ra,t9,zero
    bne t7,zero,gth_k
    nop
    addiu t7,zero,1               # no tag: player 1's (as build 23)
gth_k:
    lui t6,0x000E
    sw t7,0x7EF8(t6)              # the credit (gq_add reads it)
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t5,t6,0xF800              # the enemies' table (gq_kill reads it)
    addu t4,t4,t5
    sb t7,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)

gt_h10:                           # 0x01F26D00(a0 = a thing, a1 = the shot + 72): 10 points, no damage
    daddu t9,ra,zero
    jal gt_who
    nop
    daddu ra,t9,zero
    beq t7,zero,gt10_go           # no tag (a cannon shot): the credit stays as it is (build 23)
    lui t6,0x000E
    sw t7,0x7EF8(t6)
gt10_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26D00
    j 0x01F26D08
    sd ra,0(sp)

gt_h100:                          # 0x01F27A40(a0 = a thing, a1 = the shot + 72): 100 / 1000 points
    daddu t9,ra,zero
    jal gt_who
    nop
    daddu ra,t9,zero
    beq t7,zero,gt100_go
    lui t6,0x000E
    sw t7,0x7EF8(t6)
gt100_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F27A40
    j 0x01F27A48
    sd ra,0(sp)
"""


def gt_source(labels):
    """The seventy-eighth glue's source with its installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, name in GT_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\\n    lui t4,0x%04X\\n"
                   "    ori t4,t4,0x%04X\\n    bne t5,t4,gti_go\\n    nop\\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: j %s\\n"
                   "    sw zero,%d(t7)\\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    return GT_SRC.replace("@CHECKS@", checks.rstrip("\\n")).replace("@WRITES@", writes.rstrip("\\n"))


# ---- sixty-sixth glue (only with --ship2score) --------------------------------------------------------------
''')

# 3. main: the option, after glue 77's block
once("""        hook_base(0x00167E90, gx_next, jal(labels["gx_inst"]), "the controller task: first, the seventy-seventh glue's jumps into a fresh flight module")
        n_glue += n
""", """        hook_base(0x00167E90, gx_next, jal(labels["gx_inst"]), "the controller task: first, the seventy-seventh glue's jumps into a fresh flight module")
        n_glue += n

    if "--gummitag" in sys.argv:                                           # seventy-eighth glue (Gummi points of other weapons)
        assert "--ship2score" in sys.argv, "--gummitag needs --ship2score (the sixty-sixth glue)"
        assert "--gummiall" not in sys.argv, "--gummitag and --gummiall share 0x000EF000"
        gt_next = words[0x00167E90]
        assert (gt_next >> 26) == 3
        gqh = [a for a in range(GQ_AT, GQ_END, 4) if words.get(a) == 0x3C0F000E and words.get(a + 4) == 0x3C0901F5
               and words.get(a + 8) == 0x35294278]                         # gq_hit: lui t7,0x000E / lui t1,0x01F5 / ori t1,t1,0x4278
        assert len(gqh) == 1, gqh
        syms = {"GT_NEXT": (gt_next & 0x3FFFFFF) << 2, "GQH_NEXT": gqh[0] + 4}
        _code, gt_labels = assemble(GT_AT, gt_source(None), syms)
        labels, n = add_code(GT_AT, GT_END, gt_source(gt_labels), syms, "the Gummi points of other weapons (tag)")
        assert labels == gt_labels
        hook_base(gqh[0], 0x3C0F000E, (2 << 26) | ((labels["gt_hit"] >> 2) & 0x3FFFFFF), "gq_hit: first gt_hit (a tagged shot's ship)")
        hook_base(0x00167E90, gt_next, jal(labels["gt_inst"]), "the controller task: first, the seventy-eighth glue's jumps into a fresh flight module")
        n_glue += n
""")

# 4. the end check: the enemies' table of glue 66 too
once("""        clash = [a for a in gq_own if a in words]
        assert not clash, "the sixty-sixth glue's own pictures lie on patch words: %08X .." % clash[0]
    body =""", """        clash = [a for a in gq_own if a in words]
        assert not clash, "the sixty-sixth glue's own pictures lie on patch words: %08X .." % clash[0]
        etab = [a for a in words if 0x000EF800 <= a < 0x000F0000]
        assert not etab, "the sixty-sixth glue's enemies' table lies on patch words: %08X .." % min(etab)
    body =""")

F.write_text(src, encoding="utf-8")
print("done: the seventy-eighth glue --gummitag; backup", BAK)
