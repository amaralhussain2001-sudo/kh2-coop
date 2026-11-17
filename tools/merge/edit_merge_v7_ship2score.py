"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (option --ship2score, needs --ship2hit): THE GUMMI FLIGHT
COUNTS PLAYER 2'S POINTS (ninth round, job 6, first half: the counting; the second score row comes with the next
edit).
Read in the flight module (docs/STATE.md, parts 93 and 95):
  the ship's "fire" 0x01F1EE00(ship); a shot's start-up 0x01F536D0(shot, ...) (class 0x01F81458, the cannons; its
  hits come from 0x01F54278); "an enemy takes a hit" 0x01F26998(enemy, the shot + 72) (10 points a hit);
  "the enemy is destroyed" 0x01F26520(enemy) (its worth); every adder ends in 0x01F4DE90(amount); the score is set
  to 0 by 0x01F4DE70. A shot's record does not say which ship fired it (runs gsh1 / gsh2).
What the glue does (six jumps written into a fresh flight module by gq_inst, in front of the fifty-first glue's
gs_inst at 0x00167E90):
  gq_fire   the ship that fires is noted while its "fire" runs (0x000E7EF0), and as "the ship that fired last"
            (0x000E7EF4: 1 or 2).
  gq_init   a shot that starts up while a ship fires gets that ship's number in a side table (one byte for each
            16 bytes of address, 0x000EE800 .. 0x000EF7FF); a shot that starts up while no ship fires gets 0.
  gq_hit    the hit's shooter = the shot's number (the cannons' hits), else the ship that fired last; it is "the
            credit" (0x000E7EF8) and is noted for the enemy (a second table, 0x000EF800 .. 0x000EFFFF).
  gq_kill   the credit = the ship whose shot hit this enemy last.
  gq_add    points that the game adds while the credit is ship 2 are also added to PLAYER 2'S POINTS (0x000E7EFC),
            unless the game's score is locked.
  gq_reset  a new flight: player 2's points are 0.
The game's own score is not touched (the mission's result, the medals). Player 1's points = the score - player
2's. Without the option the builder writes what it wrote before.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "GQ_SRC" in s:
    raise SystemExit("already there")

# (1) the source, in front of the sixty-fifth glue's
a = "HP_AT = 0x000ECF40" + NL
assert s.count(a) == 1
NEW = r'''# ---- sixty-sixth glue (only with --ship2score) --------------------------------------------------------------
GQ_AT = 0x000EDC00
GQ_END = 0x000EE400
GQ_SITES = (                                       # (the place in the flight module, its first word, the routine that takes it over)
    (0x01F1EE00, 0x27BDFFD0, "gq_fire"),           # the ship's "fire"
    (0x01F536D0, 0x27BDFF30, "gq_init"),           # a shot's start-up (the cannons' class)
    (0x01F26998, 0x27BDFFD0, "gq_hit"),            # an enemy takes a hit
    (0x01F26520, 0x27BDFFF0, "gq_kill"),           # the enemy is destroyed
    (0x01F4DE90, 0x27BDFFF0, "gq_add"),            # points are added to the score
    (0x01F4DE70, 0x27BDFFF0, "gq_reset"),          # the score is set to 0
)
GQ_SRC = """
gq_inst:                          # from 0x00167E90, in front of the fifty-first glue's gs_inst: a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gqi_go
    nop
@CHECKS@
@WRITES@
gqi_go:
    j GQ_NEXT
    nop

gq_fire:                          # 0x01F1EE00(a0 = a ship): the ship fires
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    sw a0,0x7EF0(t7)              # the ship that fires now
    lui t6,0x000F
    lw t6,0x2604(t6)              # ship 2
    addiu t5,zero,1
    bne a0,t6,gqf_1
    nop
    addiu t5,zero,2
gqf_1:
    sw t5,0x7EF4(t7)              # ... and the ship that fired last (1 / 2)
    jal gqf_body
    nop
    lui t7,0x000E
    sw zero,0x7EF0(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gqf_body:
    addiu sp,sp,-48               # the two instructions that sat at 0x01F1EE00
    j 0x01F1EE08
    sd s2,16(sp)

gq_init:                          # 0x01F536D0(a0 = a shot, ...): the shot starts up
    lui t7,0x000E
    lw t6,0x7EF0(t7)              # the ship that fires now (0 = none: not a player's shot)
    srl t4,a0,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800              # the shots' table
    addu t4,t4,t3
    beq t6,zero,gqn_w
    move t2,zero
    lui t5,0x000F
    lw t5,0x2604(t5)              # ship 2
    addiu t2,zero,1
    bne t6,t5,gqn_w
    nop
    addiu t2,zero,2
gqn_w:
    sb t2,0(t4)
    addiu sp,sp,-208              # the two instructions that sat at 0x01F536D0
    j 0x01F536D8
    sd s3,152(sp)

gq_hit:                           # 0x01F26998(a0 = an enemy, a1 = the hit record = the shot + 72)
    lui t7,0x000E
    lui t1,0x01F5
    ori t1,t1,0x4278              # the cannon shots' own call of this routine
    bne ra,t1,gqh_last
    addiu t4,a1,-72               # the shot
    srl t4,t4,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship that fired it
    bne t2,zero,gqh_k
    nop
gqh_last:
    lw t2,0x7EF4(t7)              # not known: the ship that fired last
gqh_k:
    sw t2,0x7EF8(t7)              # the credit
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800              # the enemies' table
    addu t4,t4,t3
    sb t2,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)

gq_kill:                          # 0x01F26520(a0 = the enemy): it is destroyed, its worth is added
    lui t7,0x000E
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship whose shot hit it last
    beq t2,zero,gqk_1
    nop
    sw t2,0x7EF8(t7)
    sb zero,0(t4)
gqk_1:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26520
    j 0x01F26528
    sd s0,0(sp)

gq_add:                           # 0x01F4DE90(a0 = points)
    lui t7,0x000E
    lw t2,0x7EF8(t7)
    addiu t1,zero,2
    bne t2,t1,gqa_1               # the credit is not ship 2
    lui t5,0x01F8
    lbu t4,0x03A0(t5)             # the game's score is locked
    bne t4,zero,gqa_1
    nop
    lw t3,0x7EFC(t7)
    addu t3,t3,a0
    sw t3,0x7EFC(t7)              # player 2's points
gqa_1:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F4DE90
    j 0x01F4DE98
    daddu a1,a0,zero

gq_reset:                         # 0x01F4DE70: the score is set to 0 (a new flight)
    lui t7,0x000E
    sw zero,0x7EFC(t7)
    sw zero,0x7EF8(t7)
    sw zero,0x7EF4(t7)
    sw zero,0x7EF0(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x01F4DE70
    j 0x01F4DE78
    lui a0,0x01F8
"""


def gq_source(labels):
    """The sixty-sixth glue's source with the installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, name in GQ_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\n    lui t4,0x%04X\n"
                   "    ori t4,t4,0x%04X\n    bne t5,t4,gqi_go\n    nop\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\n    lui t4,0x%04X\n    ori t4,t4,0x%04X\n    sw t4,%d(t7)                 # 0x%08X: j %s\n"
                   "    sw zero,%d(t7)\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    return GQ_SRC.replace("@CHECKS@", checks.rstrip("\n")).replace("@WRITES@", writes.rstrip("\n"))


'''
s = s.replace(a, NEW + a)

# (2) the builder: in front of the fifty-second glue's block
a = '''    if "--carpet2" in sys.argv:                                            # fifty-second glue, an experiment (a carpet under player 2's hero)
'''
assert s.count(a) == 1
NEW2 = '''    if "--ship2score" in sys.argv:                                         # sixty-sixth glue (the Gummi flight counts player 2's points)
        assert "--ship2hit" in sys.argv, "--ship2score needs --ship2hit"
        gq_next = words[0x00167E90]                                        # the fifty-first glue's jal gs_inst
        assert (gq_next >> 26) == 3
        syms = {"GQ_NEXT": (gq_next & 0x3FFFFFF) << 2}
        _code, gq_labels = assemble(GQ_AT, gq_source(None), syms)
        labels, n = add_code(GQ_AT, GQ_END, gq_source(gq_labels), syms, "the Gummi flight counts player 2's points")
        assert labels == gq_labels
        hook_base(0x00167E90, gq_next, jal(labels["gq_inst"]), "the controller task: first the sixty-sixth glue's jumps into a fresh flight module")
        n_glue += n

'''
s = s.replace(a, NEW2 + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
