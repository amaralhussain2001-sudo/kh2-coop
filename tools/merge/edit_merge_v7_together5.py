"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue; plan row 9, second half), FIFTH
form, after the runs tg10, tg11, tg12 (candidate v67: the clash works for both heroes, a lift by the falcon stays
the lifted hero's alone; both screens show the clash camera and "Press"). What was left: the second hero played
the clash where he happened to stand, out of the clash camera's picture.
Now (tg_do, the copy of a capture made by the boss's own script): when the second hero is NOT in the move yet
(the first capture of a clash), he is first PUT BESIDE the first hero with the game's "set position" routine
0x0016ACE0 (the routine of the script call of that name): the first hero's place plus 0.45 times the way from the
first hero to the boss, turned a quarter to the side. Then, as before, he is turned to look at the boss.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together5.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tg_side" in s:
    raise SystemExit("already there")
assert "tn_first" in s, "the fourth form must be there first"
a = s.index("tg_do:" + NL)
b = s.index("tg_go:" + NL, a)
new = '''tg_do:
    lw t9,0(a0)
    sw t9,0x7E3C(t7)              # the captor's word
    addiu sp,sp,-112
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    swc1 f12,32(sp)
    swc1 f13,36(sp)
    sd a3,40(sp)
    sd t3,48(sp)
    swc1 f14,56(sp)
    sd t8,80(sp)
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,tg_dir            # he is in the move already: he keeps his place
    nop
tg_side:
    lwc1 f0,0x70(t8)              # the boss
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(a1)              # the first hero
    lwc1 f3,0x78(a1)
    sub.s f4,f0,f2
    sub.s f5,f1,f3                # the way from the first hero to the boss
    lui t2,0x3EE6
    ori t2,t2,0x6666              # 0.45
    mtc1 t2,f6
    mul.s f5,f5,f6
    mul.s f4,f4,f6
    add.s f2,f2,f5                # x: the first hero's + 0.45 * the way's z
    sub.s f3,f3,f4                # z: the first hero's - 0.45 * the way's x
    swc1 f2,64(sp)
    lw t2,0x74(a1)
    sw t2,68(sp)
    swc1 f3,72(sp)
    lw t2,0x7C(a1)
    sw t2,76(sp)
    move a0,t3
    jal 0x0016ACE0                # he is put beside the first hero
    addiu a1,sp,64
    ld t3,48(sp)
    ld t8,80(sp)
tg_dir:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f0,f0,f2
    sub.s f1,f1,f3
    swc1 f0,64(sp)                # the way from him to the boss (x, 0, z, 0)
    sw zero,68(sp)
    swc1 f1,72(sp)
    sw zero,76(sp)
    move a0,t3
    jal 0x0016AEF0                # he looks at the boss
    addiu a1,sp,64
    lui t7,0x000E
    addiu t2,zero,1
    sw t2,0x7E30(t7)
    ld a0,8(sp)
    ld a1,48(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f13,36(sp)
    lwc1 f14,56(sp)
    jal 0x00180378                # the same move on the other hero of the pair
    lwc1 f12,32(sp)
    lui t7,0x000E
    sw zero,0x7E30(t7)
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f13,36(sp)
    lwc1 f14,56(sp)
    lwc1 f12,32(sp)
    addiu sp,sp,112
'''
s = s[:a] + new + s[b:]
x = "TG_END = 0x000EA600"
assert s.count(x) == 1
s = s.replace(x, "TG_END = 0x000EA800")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
