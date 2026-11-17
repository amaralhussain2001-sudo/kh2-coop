"""One-off: the FIFTY-FIRST GLUE of tools/merge/merge_v7.py (--ship2hit), THIRD form, after the run gh3 (candidate
v75, the whole mission with both players firing: completed, in sync, 0 fault lines): ship 1's hull went 13 -> 59
when it took a repair, ship 2's never rose. Read in the flight module: the ship's "repair" is 0x01F200C8(ship, the
amount in f12) = 0x01F233B0(status, amount) and the flag 0x4; the pick-up code hands it "the player ship".
Now gs_rep (a fifth jump, at 0x01F200C8): a repair of ship 1 is also given to ship 2 while ship 2 flies.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2hit3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gs_rep" in s:
    raise SystemExit("already there")
assert "gs_low" in s

# 1. the installer: one more place to test and one more jump
old = '''    lw t5,0x03A8(t7)              # 0x01F203A8 "take damage": the same word
    bne t5,t4,gi_go
    lui t4,@J_TEST_HI@
'''
new = '''    lw t5,0x03A8(t7)              # 0x01F203A8 "take damage": the same word
    bne t5,t4,gi_go
    lw t5,0x00C8(t7)              # 0x01F200C8 "repair": still addiu sp,sp,-16?
    lui t4,0x27BD
    ori t4,t4,0xFFF0
    bne t5,t4,gi_go
    lui t4,@J_REP_HI@
    ori t4,t4,@J_REP_LO@
    sw t4,0x00C8(t7)              # j gs_rep
    sw zero,0x00CC(t7)
    lui t4,@J_TEST_HI@
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)

# 2. the routine
old = '''gs_low:                           # the gauge's "player ship": the ship with the lower hull
'''
new = '''gs_rep:                           # 0x01F200C8(a0 = a ship, f12 = the amount): repair
    lui t7,0x000F
    lw t6,0x2604(t7)              # ship 2
    beq t6,zero,gr_go
    lw t5,0x2600(t7)
    bne a0,t5,gr_go               # not ship 1
    lw t4,0x1438(t6)
    andi t4,t4,0x10
    bne t4,zero,gr_go             # ship 2 has fallen
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    swc1 f12,16(sp)
    jal gr_go                     # ship 2 gets the same repair
    move a0,t6
    ld a0,8(sp)
    lwc1 f12,16(sp)
    ld ra,0(sp)
    addiu sp,sp,32
gr_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F200C8
    j 0x01F200D0
    sd s0,0(sp)
gs_low:                           # the gauge's "player ship": the ship with the lower hull
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)

# 3. the build step
old = '''        for k in ("TEST", "ABLE", "HIT", "DMG"):                           # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        src = src.replace("@JAL_LOW_HI@", "0").replace("@JAL_LOW_LO@", "0")'''
new = '''        for k in ("TEST", "ABLE", "HIT", "DMG", "REP"):                    # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        src = src.replace("@JAL_LOW_HI@", "0").replace("@JAL_LOW_LO@", "0")'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
old = '''        for k, lab in (("TEST", "gs_test"), ("ABLE", "gs_able"), ("HIT", "gs_hit"), ("DMG", "gs_dmg")):'''
new = '''        for k, lab in (("TEST", "gs_test"), ("ABLE", "gs_able"), ("HIT", "gs_hit"), ("DMG", "gs_dmg"), ("REP", "gs_rep")):'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
