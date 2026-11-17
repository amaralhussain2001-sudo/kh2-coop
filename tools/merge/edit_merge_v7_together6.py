"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue; plan row 9, second half), SIXTH
form, after the runs tg13, tg14, tg15 (candidate v68: in sync, 0 fault lines, but the second hero was NOT put beside
the first: he still pushed where he stood, away from the boss).
Why (READ in Shan-Yu's script, function 347): the clash's first capture (252) is made by the HOOKED function
itself, so each hero's own copy makes it and the copy path tg_do, where the fifth form placed him, is not walked.
Now the placing is done where the pair is MADE (th_new, first pairing only): the second hero is put 70 units to
the side of the first (the first hero's place plus 70 times his direction turned a quarter; "get direction"
0x0016AF58, "set position" 0x0016ACE0) and gets the first hero's direction (0x0016AEF0). The boss's script has
turned the first hero for the clash just before it hooks.
tg_do keeps only "he looks at the boss" for the captures the boss's own script makes.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together6.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tn_place" in s:
    raise SystemExit("already there")
assert "tg_side" in s, "the fifth form must be there first"

# 1. tg_do: no placing there
a = s.index("    lw t2,0x160(t3)" + NL + "    andi t2,t2,0x4000" + NL + "    bne t2,zero,tg_dir")
b = s.index("tg_dir:" + NL, a)
s = s[:a] + s[b:]

# 2. th_new: the whole routine anew
a = s.index("th_new:  ")
b = s.index("th_tick:  ", a)
new = '''th_new:                           # from 0x00171FE4 (was jal 0x0016CF00): a new context for a script that is hooked onto
    addiu sp,sp,-128              # an object. a0 = the script root, a1 = 0, a2 = the function, a3 = [object, extra], t0 = how many
    sd ra,0(sp)
    sd a0,8(sp)
    sd a2,16(sp)
    sd a3,24(sp)
    sd t0,32(sp)
    jal 0x0016CF00
    nop
    sd v0,40(sp)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tn_out
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tn_out
    lui t2,0x0033
    lhu t2,-17696(t2)
    addiu t1,zero,0x0908
    bne t2,t1,tn_out              # (the experiment: only Shan-Yu's room)
    ld t8,24(sp)
    lw t8,0(t8)                   # the object the script is hooked onto
    beq t8,t6,tn_o
    move t3,t4
    bne t8,t4,tn_out              # not a hero
    move t3,t6
tn_o:
    lui t7,0x000E
    lw t2,0x7E48(t7)
    bne t2,zero,tn_out            # a hero's own hooked script hooks: each hero's script does that for itself
    nop
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tn_out
    nop
    lw t2,0(t2)
    beq t2,zero,tn_out            # he is down
    nop
    sd t3,48(sp)
    sd t8,56(sp)
    lw t1,0x160(t3)
    andi t1,t1,0x4000             # is he held
    lw t0,0xAEC(t3)               # has he a hooked script
    lw t2,0x7E38(t7)
    beq t2,zero,tn_first
    nop
    or t1,t1,t0                   # a pair lives: he gets the copy while he is still in the move
    beq t1,zero,tn_out
    nop
    b tn_copy
    nop
tn_first:
    or t1,t1,t0
    bne t1,zero,tn_out            # no pair yet, and he is busy in something else
    nop
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # the two heroes' distance, squared
    lui t2,0x4874
    ori t2,t2,0x2400              # 250000.0 = 500 units, squared
    mtc1 t2,f4
    c.lt.s f2,f4
    bc1f tn_out                   # too far: he stays free
    nop
tn_place:
    addiu a0,sp,64
    jal 0x0016AF58                # the first hero's direction (the script has turned him for the move)
    move a1,t8
    ld t8,56(sp)
    lwc1 f0,64(sp)
    lwc1 f1,72(sp)
    lui t2,0x428C                 # 70.0
    mtc1 t2,f6
    mul.s f2,f1,f6
    mul.s f3,f0,f6
    lwc1 f4,0x70(t8)
    lwc1 f5,0x78(t8)
    add.s f4,f4,f2                # x: the first hero's + 70 * his direction's z
    sub.s f5,f5,f3                # z: the first hero's - 70 * his direction's x
    swc1 f4,80(sp)
    lw t2,0x74(t8)
    sw t2,84(sp)
    swc1 f5,88(sp)
    lw t2,0x7C(t8)
    sw t2,92(sp)
    ld a0,48(sp)
    jal 0x0016ACE0                # the second hero is put beside the first
    addiu a1,sp,80
    ld a0,48(sp)
    jal 0x0016AEF0                # and looks the same way
    addiu a1,sp,64
    ld t3,48(sp)
    ld t8,56(sp)
    lui t7,0x000E
    lui t5,0x0035
tn_copy:
    sw t8,0x7E34(t7)              # the first hero
    sw t3,0x7E38(t7)              # the second hero
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
    ld t9,24(sp)
    lw t2,4(t9)
    sw t3,96(sp)                  # the second array: [the other hero, the same extra]
    sw t2,100(sp)
    ld a0,8(sp)
    move a1,zero
    ld a2,16(sp)
    addiu a3,sp,96
    jal 0x0016CF00                # his own context of the same function
    ld t0,32(sp)
    ld a0,48(sp)
    jal 0x00177460                # hooked onto him
    move a1,v0
tn_out:
    ld v0,40(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,128
'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
