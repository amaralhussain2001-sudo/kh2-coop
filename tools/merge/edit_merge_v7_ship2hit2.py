"""One-off: the FIFTY-FIRST GLUE of tools/merge/merge_v7.py (--ship2hit), SECOND form, after the runs gh1 and gh2
(candidate v75: ship 2's hull goes 177 -> 115 while ship 1's goes 177 -> 0; in sync, 0 fault lines):
 (1) THE MISSION IS OVER WHEN EITHER SHIP FALLS (the rule the plan already has for the Light Cycles, row 36): when
     "take damage" has brought SHIP 2's hull to 0 (the game then sets the flag 0x10 at ship + 0x1438), ship 1's
     hull is set to 0 and it gets the same flag, so the game's own end of the mission runs.
 (2) THE ONE HULL GAUGE SHOWS THE WEAKER SHIP: the gauge's routine 0x01F69790 asks for "the player ship" twice
     (0x01F697C4 for the hull, 0x01F697D4 for the full hull); both calls now get the ship with the lower hull.
 (3) a test of the test, option --ship2first: only ship 2 is asked "does this ball touch you" (so that ship 2 is
     the one that falls in a test run).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2hit2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gs_low" in s:
    raise SystemExit("already there")
assert "gs_test" in s

# 1. the installer also writes the gauge's two calls
old = '''    lui t4,0x000E
    sw zero,0x7E4C(t4)
gi_go:
    j GM_NEXT                     # the twenty-sixth glue's gm_pad
    nop
'''
new = '''    lui t4,0x000E
    sw zero,0x7E4C(t4)
    lui t3,0x01F7                 # the hull gauge (0x01F69790) asks for "the player ship" at 0x01F697C4 and 0x01F697D4
    lui t4,0x0C7C
    ori t4,t4,0x873E              # jal 0x01F21CF8
    lw t5,-26684(t3)
    bne t5,t4,gi_go
    lw t5,-26668(t3)
    bne t5,t4,gi_go
    lui t4,@JAL_LOW_HI@
    ori t4,t4,@JAL_LOW_LO@
    sw t4,-26684(t3)              # jal gs_low
    sw t4,-26668(t3)
gi_go:
    j GM_NEXT                     # the twenty-sixth glue's gm_pad
    nop
gs_low:                           # the gauge's "player ship": the ship with the lower hull
    lui t7,0x01F8
    lw v0,-8636(t7)               # the game's (ship 1)
    lui t6,0x000F
    lw t5,0x2604(t6)              # ship 2
    beq t5,zero,gl_out
    lw t4,0x2600(t6)
    bne t4,v0,gl_out
    nop
    lwc1 f0,0x4AC(v0)
    lwc1 f1,0x4AC(t5)
    c.lt.s f1,f0
    bc1f gl_out
    nop
    move v0,t5
gl_out:
    jr ra
    nop
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)

# 2. take damage: when ship 2 falls, ship 1 goes with it
a = s.index("gs_dmg:  ")
b = s.index('"""', a)
new_dmg = '''gs_dmg:                           # 0x01F203A8(a0 = a ship, a1 = the amount): take damage
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,gd_chk
    lui t5,0x000F
    lw t4,0x2600(t5)
    bne a0,t4,gd_chk
    nop
    move a0,t6
    sw zero,0x7E4C(t7)            # used up
gd_chk:
    lui t5,0x000F
    lw t4,0x2604(t5)              # ship 2
    beq t4,zero,gd_go
    nop
    bne a0,t4,gd_go               # not ship 2: as the game
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    jal gd_go                     # ship 2 takes the damage
    nop
    ld t4,8(sp)
    lw t3,0x1438(t4)
    andi t3,t3,0x10
    beq t3,zero,gd_out            # ship 2 is still flying
    lui t5,0x000F
    lw t2,0x2600(t5)              # ship 2 has fallen: the mission is over when either ship falls, so ship 1 goes
    beq t2,zero,gd_out            # with it: hull 0 and the game's own "at its end" flag
    nop
    lw t3,0x1438(t2)
    andi t1,t3,0x10
    bne t1,zero,gd_out
    ori t3,t3,0x10
    sw t3,0x1438(t2)
    sw zero,0x4AC(t2)
gd_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
gd_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F203A8
    j 0x01F203B0
    sd s0,0(sp)
'''
s = s[:a] + new_dmg + s[b:]

# 3. the build step: the gauge's call word, and the test option
old = '''        for k in ("TEST", "ABLE", "HIT", "DMG"):                           # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        code, labels = assemble(GS_AT, src, syms)
        src = GS_SRC
'''
new = '''        if "--ship2first" in sys.argv:                                     # (test of the test: only ship 2 is asked)
            x = """    jal gt_orig                   # ship 1 first
    nop
    bne v0,zero,gt_done           # ship 1 is touched: as the game
"""
            assert GS_SRC.count(x) == 1
            gs_src = GS_SRC.replace(x, """    nop                           # (--ship2first: ship 1 is not asked)
    nop
    nop
""")
        else:
            gs_src = GS_SRC
        src = gs_src
        for k in ("TEST", "ABLE", "HIT", "DMG"):                           # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        src = src.replace("@JAL_LOW_HI@", "0").replace("@JAL_LOW_LO@", "0")
        code, labels = assemble(GS_AT, src, syms)
        src = gs_src
        w_low = jal(labels["gs_low"])
        src = src.replace("@JAL_LOW_HI@", "0x%04X" % (w_low >> 16)).replace("@JAL_LOW_LO@", "0x%04X" % (w_low & 0xFFFF))
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
x = " [--ship2hit]"
assert s.count(x) == 1
s = s.replace(x, " [--ship2hit [--ship2first]]")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
