"""One-off: the EIGHTY-SIXTH GLUE --hullgauges into merge_v7.py (docs/STATE.md part 152, item 11 (b) of his list: BOTH Gummi
hull gauges, ship 1's at the game's place, ship 2's mirrored to the bottom left). Without the option the builder writes the old
words bit for bit. Copy of the builder before it: local/merge_v7-before-hullgauges.py.
  python -I tools/merge/edit_merge_v7_hullgauges.py          (run ONCE; it refuses a second run)
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
P = ROOT / "tools" / "merge" / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "EIGHTY-SIXTH GLUE" in t:
    raise SystemExit("already in")
shutil.copyfile(P, ROOT / "local" / "merge_v7-before-hullgauges.py")

HEAD = """
EIGHTY-SIXTH GLUE (built only with the option --hullgauges, with --ship2hit and --ship2score): BOTH GUMMI SHIPS' HULL GAUGES. The
flight's HUD has one hull gauge (232 bytes at the HUD manager + 140, steps 0x01F69DD8: 1 make, 2 show, 3 fade); the fifty-first
glue's gs_low made it show the weaker ship. Now a second gauge object G2 (0x000D4B00) of the same class is built (ctor 0x01F69098),
started, ended and freed with the game's (gb_start / gb_end / gb_free in place of 0x01F693B0 / 0x01F693C0 / 0x01F69210) and stepped
after it (gb_step at the call 0x01F66D10) while the game's "player ship" 0x01F7DE44 holds ship 2 (only while ship 1 is the game's).
All of G2's memory (its pictures, the two direct ones 0x01F69440 / 0x01F6948C, the 8-byte link blocks of 0x01F47C30 at 0x01F47C5C,
its digit "2") comes from pool B (48 places of 400 bytes, 0x000D0000 .. 0x000D4B00; gb_new in front of gq_new at 0x01F47164, gb_raw
in front of the module's new), never from the module's heap (the route parity of part 106); its pictures are ended with the
destroy-only method after their link block word +376 is cleared. G2 stands GB_DX / GB_DY away (gb_place at the show's place call
0x01F699F8; the four pictures the show does not place get that offset). gs_low's two calls are not written (gauge 1 = ship 1) and
the sixty-sixth glue's digit beside gauge 1 is always "1". The installer gb_inst (from 0x00167E90, first) writes the module words
into a fresh flight module and clears G2. Code 0x000D5000 .. 0x000D5800, values 0x000D4C00 (V_WORK, V_POOLN, V_DIG2).
"""

SECTION = '''

# ---- eighty-sixth glue (only with --hullgauges) ------------------------------------------------------------------
GB_AT = 0x000D5000                                 # gb_new must stay the first routine (the sixty-sixth glue's gq_inst calls it)
GB_END = 0x000D5800
GB_POOL, GB_POOL_END = 0x000D0000, 0x000D4B00      # pool B: 48 places of 400 bytes
GB_G2 = 0x000D4B00                                 # the second gauge object (232 bytes)
GB_VARS = 0x000D4C00                               # V_WORK +0, V_POOLN +4, V_DIG2 +8
GB_DX = -384                                       # gauge 2 = gauge 1 moved this far (places count 512 across, 448 down)
GB_DY = 0
GB_MARK2_X = 124                                   # its digit "2": right of gauge 2
GB_MARK2_Y = 396
GB_SITES = (                                       # (place in the flight module, its first word, the routine that takes it over)
    (0x01F693B0, 0x240F0001, "gb_start"),          # the gauge starts (state 1)
    (0x01F693C0, 0x240F0003, "gb_end"),            # the gauge ends (state 3)
    (0x01F69210, 0x27BDFFE0, "gb_free"),           # the gauge's pictures are freed
)
GB_CALLS = (                                       # (a call in the flight module, its word, the routine called in its place)
    (0x01F66D10, 0x0C7DA776, "gb_step"),           # the HUD manager steps the gauge
    (0x01F69440, 0x0C7C6458, "gb_raw"),            # the gauge's make: a picture's 388 bytes, straight from the module's heap
    (0x01F6948C, 0x0C7C6458, "gb_raw"),            # the same, the second one
    (0x01F47C5C, 0x0C7C6458, "gb_raw"),            # a picture's 8-byte link block (0x01F47C30)
    (0x01F699F8, 0x0C7D1DA4, "gb_place"),          # the show asks the gauge's place (0x01F47690)
)
GB_SRC = """
gb_new:                           # (first, at GB_AT) the call at 0x01F47164 (a new picture's 388 bytes; gq_inst writes it)
    lui t7,0x000D
    lw t6,19456(t7)               # V_WORK (0x000D4C00): the second gauge is in work
    bne t6,zero,gb_pool
    nop
    j GQ_NEW                      # as before: the sixty-sixth glue's gq_new
    nop
gb_raw:                           # 0x01F69440 / 0x01F6948C (the gauge's two direct pictures), 0x01F47C5C (a link block)
    lui t7,0x000D
    lw t6,19456(t7)
    bne t6,zero,gb_pool
    nop
    j 0x01F19160                  # as the game: the module's heap
    nop
gb_pool:                          # t7 = 0x000D0000: the next place of pool B (400 bytes each)
    lw t5,19460(t7)               # V_POOLN: places given out
    sltiu t4,t5,48
    beq t4,zero,gbp_full
    addiu t4,t5,1
    sw t4,19460(t7)
    sll t3,t5,8
    sll t2,t5,7
    addu t3,t3,t2
    sll t2,t5,4
    addu t3,t3,t2                 # 400 x its number
    lui v0,0x000D
    jr ra
    addu v0,v0,t3
gbp_full:
    j 0x01F19160                  # (never: the worst case is 42 pictures + 2 link blocks + the digit)
    nop

gb_inst:                          # from 0x00167E90 (the controller task, every frame), first: a fresh flight module gets the words
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gbi_go
    nop
@CHECKS@
@WRITES@
    lui t7,0x000D
    ori t6,t7,0x4B00              # a fresh module: the second gauge and the values are cleared (0x000D4B00 .. 0x000D4C10)
    addiu t5,zero,68
gbi_clr:
    sw zero,0(t6)
    addiu t5,t5,-1
    bne t5,zero,gbi_clr
    addiu t6,t6,4
gbi_go:
    j GB_NEXT
    nop

gb_step:                          # the call at 0x01F66D10 (a0 = the game's gauge): it steps, then the second gauge for ship 2
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    jal 0x01F69DD8                # the game's gauge, as the game
    nop
    lui s0,0x000D
    ori a0,s0,0x4B00              # the second gauge
    lw t6,0(a0)
    lui t5,0x01F8
    addiu t5,t5,0x17C8            # its class 0x01F817C8: it is built
    bne t6,t5,gbt_out
    lw t6,212(a0)
    beq t6,zero,gbt_out           # nothing to do
    lui t7,0x000F
    lw t4,0x2604(t7)              # ship 2
    beq t4,zero,gbt_out
    lw t3,0x2600(t7)              # ship 1
    lui t2,0x01F8
    lw t1,-8636(t2)               # the game's player ship (0x01F7DE44)
    bne t1,t3,gbt_out             # only while ship 1 is the game's (as gs_low)
    nop
    sd t1,16(sp)
    sw t4,-8636(t2)               # the second gauge's step sees ship 2 as the player ship
    addiu t6,zero,1
    sw t6,19456(s0)               # V_WORK: its memory from pool B
    jal 0x01F69DD8
    nop
    sw zero,19456(s0)
    ld t1,16(sp)
    lui t2,0x01F8
    sw t1,-8636(t2)               # the game's player ship again
    jal gb_after
    nop
gbt_out:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32

gb_after:                         # after the second gauge's step: its own offset for the pictures the show does not place; its digit
    lui t7,0x000D
    ori t6,t7,0x4B00
    lw t5,212(t6)
    sltiu t4,t5,2
    bne t4,zero,gba_ret           # not made yet
    addiu t3,zero,@DX@
    addiu t2,zero,@DY@
    lw a0,4(t6)
    beq a0,zero,gba_8
    nop
    sw t3,356(a0)
    sw t2,360(a0)
gba_8:
    lw a0,8(t6)                   # (the picture whose place the show asks)
    beq a0,zero,gba_12
    nop
    sw t3,356(a0)
    sw t2,360(a0)
gba_12:
    lw a0,12(t6)
    beq a0,zero,gba_168
    nop
    sw t3,356(a0)
    sw t2,360(a0)
gba_168:
    lw a0,168(t6)
    beq a0,zero,gba_dig
    nop
    sw t3,356(a0)
    sw t2,360(a0)
gba_dig:
    addiu t4,zero,2
    bne t5,t4,gba_ret             # the digit only while it is shown
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui s0,0x000D
    lw t3,19464(s0)               # V_DIG2
    bne t3,zero,gbg_have
    nop
    jal 0x01F48038                # the HUD's picture sheet
    nop
    addiu t6,zero,1
    sw t6,19456(s0)               # (its memory: pool B)
    move a0,v0
    addiu a1,zero,8
    jal 0x01F46E80                # a new picture: a digit
    addiu a2,zero,72
    sw zero,19456(s0)
    beq v0,zero,gbg_out
    sw v0,19464(s0)
gbg_have:
    jal 0x01F47A58                # its picture number now
    lw a0,19464(s0)
    addiu t6,zero,56              # the digit 2
    beq v0,t6,gbg_pos
    lw a0,19464(s0)
    jal 0x01F47A10                # another one
    addiu a1,zero,56
gbg_pos:
    lw a0,19464(s0)
    addiu a1,zero,@MARK2_X@
    jal 0x01F477C0                # its place
    addiu a2,zero,@MARK2_Y@
gbg_out:
    ld ra,0(sp)
    ld s0,8(sp)
    addiu sp,sp,32
gba_ret:
    jr ra
    nop

gb_place:                         # the call at 0x01F699F8 in the show (0x01F47690: a0 = the gauge's +8 picture, a1 / a2 = x / y)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a1,8(sp)
    jal 0x01F47690
    sd a2,16(sp)
    lui t7,0x000D
    lw t6,19456(t7)               # the second gauge's show: its place is moved
    beq t6,zero,gbl_out
    ld a1,8(sp)
    ld a2,16(sp)
    lw t5,0(a1)
    addiu t5,t5,@DX@
    sw t5,0(a1)
    lw t5,0(a2)
    addiu t5,t5,@DY@
    sw t5,0(a2)
gbl_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32

gb_start:                         # 0x01F693B0 (a0 = the game's gauge): it starts; the second gauge too (built the first time)
    addiu sp,sp,-16
    sd ra,0(sp)
    addiu t7,zero,1
    sb zero,228(a0)
    sw t7,212(a0)                 # the game's gauge, as the game
    lui t7,0x000D
    ori a0,t7,0x4B00
    lw t6,0(a0)
    lui t5,0x01F8
    addiu t5,t5,0x17C8
    beq t6,t5,gbs_have
    nop
    jal 0x01F69098                # the second gauge is built (its two bars; all its places empty)
    nop
    b gbs_go
    nop
gbs_have:
    jal gb_drop                   # its old pictures (if any) are ended
    nop
gbs_go:
    lui t7,0x000D
    ori a0,t7,0x4B00
    addiu t6,zero,1
    sb zero,228(a0)
    sw t6,212(a0)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

gb_end:                           # 0x01F693C0 (a0 = the game's gauge): it ends (fades); the second gauge too
    addiu t7,zero,3
    sw t7,212(a0)                 # the game's gauge, as the game
    lui t6,0x000D
    ori t5,t6,0x4B00
    lw t4,212(t5)
    addiu t3,zero,2
    beq t4,t3,gbe_fade
    addiu t3,zero,1
    bne t4,t3,gbe_out
    nop
    sw zero,212(t5)               # never made: nothing to fade
gbe_out:
    jr ra
    nop
gbe_fade:
    jr ra
    sw t7,212(t5)                 # shown: it fades with the game's

gb_free:                          # 0x01F69210 (a0 = the game's gauge): its pictures are freed; the second gauge's too
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gbf_body                  # the game's, as the game
    nop
    jal gb_drop
    nop
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gbf_body:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F69210
    j 0x01F69218
    sd s2,16(sp)

gb_drop:                          # the second gauge's pictures (+4 .. +168) and its digit are ended; pool B is empty again
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    lui s0,0x000D
    ori s0,s0,0x4B04
    addiu s1,zero,42
gbd_l:
    lw a0,0(s0)
    beq a0,zero,gbd_n
    nop
    sw zero,376(a0)               # its link block is pool memory: not for the module's delete
    lw t6,0(a0)                   # its class
    lw t6,0(t6)                   # the first method: destroy only (as gq_end for own pictures)
    jalr t6
    nop
    sw zero,0(s0)
gbd_n:
    addiu s1,s1,-1
    bne s1,zero,gbd_l
    addiu s0,s0,4
    lui s0,0x000D
    lw a0,19464(s0)               # the digit
    beq a0,zero,gbd_0
    sw zero,19464(s0)
    sw zero,376(a0)
    lw t6,0(a0)
    lw t6,0(t6)
    jalr t6
    nop
gbd_0:
    lui t7,0x000D
    sw zero,19460(t7)             # V_POOLN: pool B is empty again
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
"""


def gb_source(labels):
    """The eighty-sixth glue's source with the installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, name in GB_SITES + GB_CALLS:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\\n    lw t5,%d(t7)                 # 0x%08X: still the game's word?\\n    lui t4,0x%04X\\n"
                   "    ori t4,t4,0x%04X\\n    bne t5,t4,gbi_go\\n    nop\\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
    for site, word0, name in GB_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: j %s\\n"
                   "    sw zero,%d(t7)\\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    for site, word0, name in GB_CALLS:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        j = ((3 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: jal %s\\n"
                   ) % (hi, j >> 16, j & 0xFFFF, lo, site, name)
    src = GB_SRC.replace("@DX@", str(GB_DX)).replace("@DY@", str(GB_DY))
    src = src.replace("@MARK2_X@", str(GB_MARK2_X)).replace("@MARK2_Y@", str(GB_MARK2_Y))
    return src.replace("@CHECKS@", checks.rstrip("\\n")).replace("@WRITES@", writes.rstrip("\\n"))
'''

BLOCK = '''
    if "--hullgauges" in sys.argv:                                         # eighty-sixth glue (both Gummi ships' hull gauges)
        assert "--ship2hit" in sys.argv and "--ship2score" in sys.argv, "--hullgauges needs --ship2hit and --ship2score"
        gb_next = words[0x00167E90]                                        # the last glue's installer call there
        assert (gb_next >> 26) == 3
        syms = {"GB_NEXT": (gb_next & 0x3FFFFFF) << 2, "GQ_NEW": gq_new_at}
        _code, gb_labels = assemble(GB_AT, gb_source(None), syms)
        code, labels = assemble(GB_AT, gb_source(gb_labels), syms)
        assert labels == gb_labels and labels["gb_new"] == GB_AT
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert GB_AT + 4 * len(code) <= GB_END, "the eighty-sixth glue does not fit"
        clash = [a for a in words if GB_POOL <= a < GB_VARS + 16 or GB_AT <= a < GB_END]
        assert not clash, "patch words in the eighty-sixth glue's room: %08X" % clash[0]
        for i, w in enumerate(code):
            a = GB_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (both Gummi hull gauges)"
        hook_base(0x00167E90, gb_next, jal(labels["gb_inst"]), "the controller task: first the eighty-sixth glue's words into a fresh flight module")
        n_glue += len(code)
'''

PAIRS = [
    # the header: the glue's paragraph and the option in the usage line
    ("\n  python -I tools/merge/merge_v7.py [outDir]", HEAD + "\n  python -I tools/merge/merge_v7.py [outDir]"),
    ("[--bindname] [--holdpair] [--gummitag]\n", "[--bindname] [--holdpair] [--gummitag] [--hullgauges]\n"),
    # the glue's room, constants and source after the eighty-fifth glue's source
    ('sa_game:\n    j 0x0014EE28\n    nop\n"""\n', 'sa_game:\n    j 0x0014EE28\n    nop\n"""\n' + SECTION),
    # the fifty-first glue: with --hullgauges gs_low's two calls are not written (gauge 1 shows ship 1)
    ('''        else:
            gs_src = GS_SRC
        src = gs_src
''', '''        else:
            gs_src = GS_SRC
        if "--hullgauges" in sys.argv:                                     # (eighty-sixth glue: gauge 1 = ship 1, no gs_low)
            x = "    sw t4,-26684(t3)              # jal gs_low\\n    sw t4,-26668(t3)\\n"
            assert gs_src.count(x) == 1
            gs_src = gs_src.replace(x, "    nop                           # (--hullgauges: gs_low is not written)\\n    nop\\n")
        src = gs_src
'''),
    # the sixty-sixth glue: its picture call at 0x01F47164 goes to gb_new; the digit beside gauge 1 is always 1
    ('''        j = ((3 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: jal %s\\n"
                   ) % (hi, j >> 16, j & 0xFFFF, lo, site, name)
    src = GQ_SRC.replace''', '''        j = ((3 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        if name == "gq_new" and "--hullgauges" in sys.argv:               # (eighty-sixth glue: gb_new first, then gq_new)
            j = (3 << 26) | ((GB_AT >> 2) & 0x3FFFFFF)
        writes += ("    lui t7,0x%04X\\n    lui t4,0x%04X\\n    ori t4,t4,0x%04X\\n    sw t4,%d(t7)                 # 0x%08X: jal %s\\n"
                   ) % (hi, j >> 16, j & 0xFFFF, lo, site, name)
    src = GQ_SRC
    if "--hullgauges" in sys.argv:                                         # (eighty-sixth glue: gauge 1's digit is always 1)
        x = "    addiu t3,zero,56              # the digit 2\\n"
        assert src.count(x) == 1
        src = src.replace(x, "    addiu t3,zero,54              # (--hullgauges: gauge 1 is ship 1's)\\n")
    src = src.replace'''),
    ("        assert labels == gq_labels\n", "        assert labels == gq_labels\n        gq_new_at = labels[\"gq_new\"]                                      # (the eighty-sixth glue's gb_new goes on to it)\n"),
    # the builder block after the eighty-fifth glue's
    ('''        n_glue += len(code) + (3 if "--sound2area" in sys.argv else 1)
''', '''        n_glue += len(code) + (3 if "--sound2area" in sys.argv else 1)
''' + BLOCK),
]
for old, new in PAIRS:
    assert t.count(old) == 1, (t.count(old), old[:80])
    t = t.replace(old, new)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-sixth glue is in")
