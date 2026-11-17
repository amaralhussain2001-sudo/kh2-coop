"""One-off: THE SEVENTY-SEVENTH GLUE of tools/merge/merge_v7.py (--gummiall): THE GUMMI POINTS OF EVERY PLAYER WEAPON GO TO THE SHIP
THAT FIRED (tenth round; the user's words of 2026-11-16: "try to close everything now"; open item c, the known limit of part 97).
BEFORE: the sixty-sixth glue (--ship2score) credits a hit to the ship that fired only for the cannons (gq_init marks a cannon shot
by its weapon's place; gq_hit trusts the mark only for the cannon shots' call 0x01F54278); every other weapon's hit was player 1's.
READ (research of 2026-11-16, ovl_gumibattle.x at 0x01F18000; notes and the first draft in the scratchpad's agentC folder; every
hook word and every caller checked by me in the module file): a weapon's block is weapon + 0x40, the block's parent (+ 0x4A4) is
ship + 0x3E0 for the player's ships (both ship constructors); the generic weapons fire through 0x01F49B38 (class 0x01F813B0), the
special ones (lock-on kinds 68 / 70 / 84) through 0x01F4A6E8; every shot starts up in 0x01F3E1A0 or 0x01F3FA20 (the cannon's own
start-up calls 0x01F3E1A0 from 0x01F538BC); the enemy's "take a hit" 0x01F26998 is called with a1 = shot + 72 from 0x01F54270
(cannons) and from eight more shot classes (return addresses in gx_wl), and the "10 points" hit 0x01F26D00 from six callers, all
with a1 = shot + 72.
THE GLUE (code 0x000EF000 .. 0x000EF400; word 0x000E7EF4 = "the ship that fires now", cleared by gq_reset already):
  gx_inst (new head of the controller task's calls at 0x00167E90): a fresh flight module (0x01F18014 = 0x636A) whose five sites
    still hold their first words gets a jump at each: gx_spawn (0x01F49B38), gx_spec (0x01F4A6E8), gx_base1 (0x01F3E1A0), gx_base2
    (0x01F3FA20), gx_h10 (0x01F26D00).
  gx_spawn / gx_spec: around a weapon's fire, "the ship that fires now" = 1 / 2 / 0 by the weapon's block's parent (gx_own).
  gx_base1 / gx_base2: a shot that starts up notes that ship in glue 66's shots' table (0x000EE800 + ((shot >> 4) & 0xFFF)); the
    cannon's own start-up (return 0x01F538C4) is left to gq_init.
  gx_hit (glue 66's gq_hit now jumps here, first word): for the nine shot calls (gx_wl) the hit is credited to the noted ship
    (0 = not known = player 1), else player 1, as gq_hit did for the cannons; then gq_hit's own two steps.
  gx_h10: the "10 points" hit is credited the same way.
NOT COVERED (READ): the block class 0x01F81228 (hits with a record on its stack), 0x01F75620 (class 0x01F81998), Teeny Ships' weapons
(their parent is the Teeny Ship's): player 1's, as before. A shot made outside its weapon's fire call gets 0 = player 1's.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_gummiall.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--gummiall" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-SEVENTH GLUE (built only with the option --gummiall, needs --ship2score): THE GUMMI POINTS OF EVERY PLAYER WEAPON GO TO
THE SHIP THAT FIRED. gx_inst gives a fresh flight module five more jumps: around a weapon's fire (0x01F49B38, 0x01F4A6E8) the firing
ship is noted (its block's parent = ship + 0x3E0), each shot that starts up (0x01F3E1A0, 0x01F3FA20) takes that note into the
sixty-sixth glue's shots' table, and the hits of nine shot kinds (gx_hit, in front of gq_hit) and the "10 points" hit (0x01F26D00)
are credited by it.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- seventy-seventh glue (only with --gummiall) --------------------------------------------------------------
GX_AT = 0x000EF000
GX_END = 0x000EF400
GX_SITES = (                                       # (the place in the flight module, its first word, its second, the routine)
    (0x01F49B38, 0x27BDFFA0, 0x248F0050, "gx_spawn"),   # a generic weapon fires one shot (a0 = the weapon)
    (0x01F4A6E8, 0x27BDFFA0, 0xFFB20040, "gx_spec"),    # a special weapon fires (a0 = the weapon)
    (0x01F3E1A0, 0x27BDFFE0, 0xAC850040, "gx_base1"),   # a shot's start-up (base class 0x01F81280)
    (0x01F3FA20, 0x27BDFFE0, 0xAC850040, "gx_base2"),   # a shot's start-up (base class 0x01F812B8)
    (0x01F26D00, 0x27BDFFF0, 0xFFBF0000, "gx_h10"),     # "10 points": a hit without damage (a1 = the shot + 72)
)
GX_SRC = """
gx_inst:                          # from 0x00167E90 (the controller task, every frame): a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gxi_go
    nop
@CHECKS@
@WRITES@
gxi_go:
    j GX_NEXT
    nop

gx_spawn:                         # 0x01F49B38(a0 = a weapon, a1, a2): one shot of a generic weapon
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gx_own
    nop
    lui t7,0x000E
    jal gxs_body
    sw t2,0x7EF4(t7)              # the ship that fires now
    lui t7,0x000E
    sw zero,0x7EF4(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gxs_body:
    addiu sp,sp,-96               # the two instructions that sat at 0x01F49B38
    j 0x01F49B40
    addiu t7,a0,80

gx_spec:                          # 0x01F4A6E8(a0 = a special weapon): it fires
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gx_own
    nop
    lui t7,0x000E
    jal gxp_body
    sw t2,0x7EF4(t7)
    lui t7,0x000E
    sw zero,0x7EF4(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gxp_body:
    addiu sp,sp,-96               # the two instructions that sat at 0x01F4A6E8
    j 0x01F4A6F0
    sd s2,64(sp)

gx_own:                           # a0 = a weapon -> t2 = 1 / 2 (the ship whose block carries it), 0 = none. t2 .. t5 only
    lw t3,0x40(a0)                # its block
    beq t3,zero,gxo_out
    move t2,zero
    lw t3,0x4A4(t3)               # the block's parent (ship + 0x3E0 for a player's ship)
    lui t5,0x000F
    lw t4,0x2604(t5)              # ship 2
    beq t4,zero,gxo_s1
    addiu t4,t4,0x3E0
    beq t3,t4,gxo_out
    addiu t2,zero,2
gxo_s1:
    move t2,zero
    lw t4,0x2600(t5)              # ship 1
    beq t4,zero,gxo_out
    addiu t4,t4,0x3E0
    bne t3,t4,gxo_out
    nop
    addiu t2,zero,1
gxo_out:
    jr ra
    nop

gx_base1:                         # 0x01F3E1A0(a0 = a shot, a1 .. a3, t0, t1): a shot starts up
    lui t7,0x000E
    lui t6,0x01F5
    ori t6,t6,0x38C4              # the cannon's start-up calls from here: gq_init has marked that shot
    beq ra,t6,gxb1_go
    srl t4,a0,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800              # the shots' table (as gq_init)
    addu t4,t4,t3
    lw t2,0x7EF4(t7)              # the ship that fires now (0 = no player's weapon)
    sb t2,0(t4)
gxb1_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F3E1A0
    j 0x01F3E1A8
    sw a1,64(a0)

gx_base2:                         # 0x01F3FA20(a0 = a shot, ...): the other start-up
    lui t7,0x000E
    srl t4,a0,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800
    addu t4,t4,t3
    lw t2,0x7EF4(t7)
    sb t2,0(t4)
    addiu sp,sp,-32               # the two instructions that sat at 0x01F3FA20
    j 0x01F3FA28
    sw a1,64(a0)

gx_hit:                           # from gq_hit's first word (0x01F26998(a0 = an enemy, a1 = the hit record)): whose shot hit it
    lui t7,0x000E
    lui t3,%hi(gx_wl)
    addiu t3,t3,%lo(gx_wl)        # the calls whose a1 is a shot + 72
gxh_l:
    lw t1,0(t3)
    beq t1,zero,gxh_last          # another caller: player 1's
    addiu t3,t3,4
    bne t1,ra,gxh_l
    addiu t4,a1,-72               # the shot
    srl t4,t4,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship that fired it
    bne t2,zero,gxh_k
    nop
gxh_last:
    addiu t2,zero,1               # not known: player 1's
gxh_k:
    sw t2,0x7EF8(t7)              # the credit
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800              # the enemies' table
    addu t4,t4,t3
    sb t2,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)
gx_wl:
    .word 0x01F54278
    .word 0x01F55BF0
    .word 0x01F55F2C
    .word 0x01F572AC
    .word 0x01F584E8
    .word 0x01F59BEC
    .word 0x01F5AF84
    .word 0x01F72E64
    .word 0x01F74544
    .word 0

gx_h10:                           # 0x01F26D00(a0 = a thing, a1 = a shot + 72): 10 points, no damage
    lui t7,0x000E
    addiu t4,a1,-72
    srl t4,t4,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800
    addu t4,t4,t3
    lbu t2,0(t4)
    bne t2,zero,gx10_k
    nop
    addiu t2,zero,1
gx10_k:
    sw t2,0x7EF8(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26D00
    j 0x01F26D08
    sd ra,0(sp)
"""


def gx_source(labels):
    """The seventy-seventh glue's source with its installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, _word1, name in GX_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\\n    lui t4,0x%04X\\n"
                   "    ori t4,t4,0x%04X\\n    bne t5,t4,gxi_go\\n    nop\\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: j %s\\n"
                   "    sw zero,%d(t7)\\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    return GX_SRC.replace("@CHECKS@", checks.rstrip("\\n")).replace("@WRITES@", writes.rstrip("\\n"))


'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--gummiall" in sys.argv:                                           # seventy-seventh glue (Gummi points of every player weapon)
        assert "--ship2score" in sys.argv, "--gummiall needs --ship2score (the sixty-sixth glue)"
        gx_next = words[0x00167E90]
        assert (gx_next >> 26) == 3
        syms = {"GX_NEXT": (gx_next & 0x3FFFFFF) << 2}
        _code, gx_labels = assemble(GX_AT, gx_source(None), syms)
        labels, n = add_code(GX_AT, GX_END, gx_source(gx_labels), syms, "the Gummi points of every player weapon")
        assert labels == gx_labels
        gqh = [a for a in range(GQ_AT, GQ_END, 4) if words.get(a) == 0x3C0F000E and words.get(a + 4) == 0x3C0901F5
               and words.get(a + 8) == 0x35294278]                         # gq_hit: lui t7,0x000E / lui t1,0x01F5 / ori t1,t1,0x4278
        assert len(gqh) == 1, gqh
        hook_base(gqh[0], 0x3C0F000E, (2 << 26) | ((labels["gx_hit"] >> 2) & 0x3FFFFFF), "gq_hit: first gx_hit (every player weapon's shot)")
        hook_base(0x00167E90, gx_next, jal(labels["gx_inst"]), "the controller task: first, the seventy-seventh glue's jumps into a fresh flight module")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
