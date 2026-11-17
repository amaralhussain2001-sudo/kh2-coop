"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue; plan row 9, second half) in its
FOURTH form, after the runs tg7, tg8, tg9 (candidate v66):
 what v66 showed: the second hero's own Triangle pushes, his move ends by itself, both in sync, 0 fault lines. Two
 flaws: (1) Shan-Yu's GRAB (he lifts one hero and throws him: captures 0xFE, 0xFC with no hooked script) was
 copied to the hero who stood near, and that hero then hung in the start pose for 2 to 5 seconds; (2) the second
 hero pushed in the direction he happened to look.
Now, only in Shan-Yu's room (world 08, room 09):
 th_new (the call at 0x00171FE4): a PAIR is made ONLY HERE, when the boss's script hooks its hero-side script onto
   a hero: the other hero gets his own copy when he is up, free (not held, no hooked script) and within 500 units
   of the first. While the pair lives, every later hook on one of them is copied to the other as long as the other
   is still in the move (held, or with a hooked script). Not from inside a hero's own hooked script.
 tg_cap (the jump at 0x00180378): a capture made by the boss's OWN script on one hero of a living pair is copied to
   the other hero when he is still in the move; he is turned to look at the boss first (0x0016AEF0, the routine of
   the script call "set direction"). No pair, no copy: a grab stays the grabbed hero's alone.
 tg_tick (the call at 0x00138538): the pair is forgotten 10 steps after nobody is held and nobody has a hooked
   script. The safety rule: a hero of the pair who is held, has NO hooked script, and has had no capture for 120
   steps is freed with "no motion" (0x0017EFA0) and the game's "go idle" (0x0016BD60(hero, 0), the routine of the
   script call "idle").
 th_tick, tg_ro and the forty-seventh glue's rule for a pair: as in the third form.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together4.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tn_first" in s:
    raise SystemExit("already there")
assert "th_new" in s, "the third form must be there first"

a = s.index('TG_SRC = """')
b = s.index('"""' + NL + 'TG_HOOK')
new_src = '''TG_SRC = """
tg_cap:                           # jump at 0x00180378 (its first two instructions are at tg_go). a0 = the captor's
    lui t7,0x000E                 # motion part, a1 = the victim, a2 = the motion number, f12 = the time
    lw t6,0x7E30(t7)
    bne t6,zero,tg_go             # this IS the second call
    lw t3,0x7E38(t7)              # the second hero of a living pair
    beq t3,zero,tg_go             # no pair: as the game (a grab is the grabbed hero's alone)
    lw t2,0x7E34(t7)              # the first hero
    beq a1,t3,tg_c0               # the victim is the second: the other one is the first
    move t3,t2
    lw t4,0x7E38(t7)
    bne a1,t2,tg_go               # the victim is neither of the two
    move t3,t4
tg_c0:
    lui t5,0x0035
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)              # a capture of either: the clock is fresh
    lw t6,0x7E48(t7)
    bne t6,zero,tg_go             # a hero's own hooked script makes this capture: it is his alone
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    bne t2,t1,tg_go               # (the experiment: only Shan-Yu's room, world 08 room 09)
    addiu t8,a0,-320              # the captor object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,tg_go             # not an object
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    lw t4,0x2400(t5)              # player 1's hero
    beq t3,t6,tg_o
    nop
    bne t3,t4,tg_go               # the other one is no hero of this room any more
    nop
tg_o:
    beq t8,t4,tg_go               # a hero or a helper holds (a Limit ...): as the game
    nop
    beq t8,t6,tg_go
    lw t2,0(t8)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,tg_go
    nop
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tg_go
    nop
    lw t2,0(t2)
    beq t2,zero,tg_go             # he is down
    nop
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,tg_do             # he is held: still in the move
    lw t2,0xAEC(t3)
    beq t2,zero,tg_go             # not held and no hooked script: he has left the move
    nop
tg_do:
    lw t9,0(a0)
    sw t9,0x7E3C(t7)              # the captor's word
    addiu sp,sp,-96
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    swc1 f12,32(sp)
    sd a3,40(sp)
    sd t3,48(sp)
    swc1 f13,36(sp)
    swc1 f14,56(sp)
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
    addiu sp,sp,96
tg_go:
    addiu sp,sp,-48               # the two instructions that sat at 0x00180378
    j 0x00180380
    swc1 f20,32(sp)
th_new:                           # from 0x00171FE4 (was jal 0x0016CF00): a new context for a script that is hooked onto
    addiu sp,sp,-96               # an object. a0 = the script root, a1 = 0, a2 = the function, a3 = [object, extra], t0 = how many
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
tn_copy:
    sw t8,0x7E34(t7)              # the first hero
    sw t3,0x7E38(t7)              # the second hero
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
    ld t9,24(sp)
    lw t2,4(t9)
    sw t3,64(sp)                  # the second array: [the other hero, the same extra]
    sw t2,68(sp)
    sd t3,48(sp)
    ld a0,8(sp)
    move a1,zero
    ld a2,16(sp)
    addiu a3,sp,64
    jal 0x0016CF00                # his own context of the same function
    ld t0,32(sp)
    ld a0,48(sp)
    jal 0x00177460                # hooked onto him
    move a1,v0
tn_out:
    ld v0,40(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,96
th_tick:                          # from 0x00177510 (the forty-third glue's jal hs_tick, or the game's runner): a hero's
    addiu sp,sp,-16               # hooked script runs. Noted, so that tg_cap and th_new leave what it does alone.
    sd ra,0(sp)
    lui t7,0x000E
    addiu t2,zero,1
    jal HOOK_NEXT
    sw t2,0x7E48(t7)
    lui t7,0x000E
    sw zero,0x7E48(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
tg_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000E
    lw t3,0x7E38(t7)              # the second hero of a pair
    beq t3,zero,tt_go
    lui t5,0x000F
    lw t6,0x05CC(t5)              # the twin
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    lw t2,0x7E34(t7)              # the first hero
    beq t3,t6,tt_v1
    nop
    bne t3,t4,tt_clear            # not the heroes of this room any more
    nop
    bne t2,t6,tt_clear
    nop
    b tt_ok
    nop
tt_v1:
    bne t2,t4,tt_clear
    nop
tt_ok:
    lw t1,-11076(t5)
    lw t0,0x7E40(t7)
    subu t1,t1,t0                 # steps since the last hook or capture of either
    lw t8,0x160(t2)
    andi t8,t8,0x4000             # the first: held
    lw t9,0xAEC(t2)               # the first: hooked script
    lw v0,0x160(t3)
    andi v0,v0,0x4000             # the second: held
    lw v1,0xAEC(t3)               # the second: hooked script
    or t0,t8,v0
    or t0,t0,t9
    or t0,t0,v1
    bne t0,zero,tt_live
    sltiu t0,t1,10
    bne t0,zero,tt_go             # all quiet for less than 10 steps
    nop
    b tt_clear                    # all quiet: the pair is forgotten
    nop
tt_live:
    sltiu t0,t1,120
    bne t0,zero,tt_go             # a capture came in the last 120 steps
    nop
    beq t8,zero,tt_l2             # the safety rule: held, no hooked script, no capture for 120 steps
    nop
    beq t9,zero,tt_free
    move a0,t2
tt_l2:
    beq v0,zero,tt_go
    nop
    bne v1,zero,tt_go
    move a0,t3
tt_free:
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion": the paired move ends
    move a1,zero
    ld a0,8(sp)
    jal 0x0016BD60                # "go idle": his action is ended the game's own way
    move a1,zero
    ld ra,0(sp)
    addiu sp,sp,16
    lui t7,0x000E
    lui t5,0x0035
    lw t1,-11076(t5)
    b tt_go
    sw t1,0x7E40(t7)
tt_clear:
    sw zero,0x7E38(t7)
tt_go:
    j TICK_NEXT
    move a0,zero
tg_ro:                            # hook 0x00189E3C (was the thirty-eighth glue's jal ro2). s1 = the object whose
    lui t7,0x0035                 # motion offers the command, s3 = the command, s2 = its argument. Out: s0
    lw s0,-5816(t7)               # the engine's player
    lui t3,0x000E
    lw t2,0x7E44(t3)
    beq t2,zero,tr_1
    nop
    sw zero,0x7E44(t3)            # the second pass: this offer is for the second hero
    jr ra
    move s0,t2
tr_1:
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,tr_out
    nop
    beq s1,t6,tr_twin             # the twin's own motion offers it (fifteenth glue)
    nop
    lw t4,0x140(s1)               # the first word of the source's motion part
    beq t4,zero,tr_out
    nop
    lw t2,0x7E38(t3)              # a pair in a move of this source?
    beq t2,zero,tr_held
    lw t5,0x7E3C(t3)
    bne t5,t4,tr_held
    nop
    lw s0,0x7E34(t3)              # this pass: the first hero
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sw t2,0x7E44(t3)
    move a0,s1
    move a1,s3
    jal 0x00189E18                # and once more for the second hero
    move a2,s2
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,48
tr_held:
    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,t4,tr_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,tr_out
    nop
tr_twin:
    move s0,t6
tr_out:
    jr ra
    nop
'''
s = s[:a] + new_src + s[b:]

old = '            x = "    bc1f tg_go                    # too far: he stays free"'
assert s.count(old) == 1, s.count(old)
s = s.replace(old, '            x = "    bc1f tn_out                   # too far: he stays free"')
x = "TG_END = 0x000EA400"
assert s.count(x) == 1
s = s.replace(x, "TG_END = 0x000EA600")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
