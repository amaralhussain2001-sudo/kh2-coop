"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue; plan row 9, second half) in its
THIRD form, after the runs tg4, tg5, tg6 and a reading of the program:
 the hero's side of a boss's move is a script that the boss's script HOOKS onto the hero it holds
 (trap_obj_hook 0x00171FA8: a new context from 0x0016CF00(script root, 0, function, [object, extra], count), set
 on the hero with 0x00177460(hero, context) = hero + 0xAEC; it runs once a step at 0x00177510 and removes itself
 when it is through). That hooked script offers the green command, reads the push and ends the move for him.
 Run tg5 showed what a second hero misses when only the motions are copied: no "Press" in his menu, his presses
 do nothing, and nothing ends his move (my forced end left him in a stiff pose).
Now, only in Shan-Yu's room (world 08, room 09):
 th_new (the call at 0x00171FE4): when a script is hooked onto a hero and the other hero is up and within 800
   units of him, the other hero gets HIS OWN COPY of the hooked script (a second context with him as the first
   argument); the pair is noted (0x000E7E34 first hero, 0x000E7E38 second hero, 0x000E7E40 the time).
 th_tick (the call at 0x00177510): notes "a hero's hooked script is running" (0x000E7E48).
 tg_cap (the jump at 0x00180378): a capture made by the boss's OWN script (not inside a hooked script) is copied to
   the second hero; captures made by a hero's hooked script are his own and are not copied.
 the forty-seventh glue's "one object holds one hero" rule lets both heroes of such a pair through.
 tg_tick (the call at 0x00138538): the safety rule: 120 steps after the first hero has left the move, a second
   hero who is still held is freed (his hooked script removed, "no motion"); 40 steps after both are out the
   pair is forgotten.
 tg_ro (0x00189E3C): a command offered by the boss's MOTION goes to both heroes of the pair.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "th_new" in s:
    raise SystemExit("already there")

a = s.index('TG_SRC = """')
b = s.index('"""' + NL + 'TG_HOOK')
new_src = '''TG_SRC = """
tg_cap:                           # jump at 0x00180378 (its first two instructions are at tg_go). a0 = the captor's
    lui t7,0x000E                 # motion part, a1 = the victim, a2 = the motion number, f12 = the time
    lw t6,0x7E30(t7)
    bne t6,zero,tg_go             # this IS the second call
    lui t5,0x0035
    lw t3,0x7E38(t7)              # a pair is noted: a capture of either of them keeps its clock fresh
    beq t3,zero,tg_c1
    lw t2,0x7E34(t7)
    beq a1,t3,tg_c0
    nop
    bne a1,t2,tg_c1
    nop
tg_c0:
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
tg_c1:
    lw t6,0x7E48(t7)
    bne t6,zero,tg_go             # a hero's own hooked script makes this capture: it is his alone
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,tg_go
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tg_go
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    bne t2,t1,tg_go               # (the experiment: only Shan-Yu's room, world 08 room 09)
    nop
    beq a1,t6,tg_o                # the victim is the twin: the other hero is player 1's
    move t3,t4
    bne a1,t4,tg_go               # the victim is no hero
    move t3,t6
tg_o:
    addiu t8,a0,-320              # the captor object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,tg_go             # not an object
    nop
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
    lw t9,0(a0)                   # the captor's motion word
    lw t2,0x7E38(t7)
    beq t2,t3,tg_do               # the other hero is the second one of the pair: the capture is copied
    nop
    lw t2,0x7E34(t7)
    bne t2,t3,tg_new
    nop
    lw t2,0x7E38(t7)
    beq t2,a1,tg_do               # (the boss took the second hero himself: copied to the first)
    nop
tg_new:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # his distance to the captor, squared
    lui t2,0x491C
    ori t2,t2,0x4000              # 640000.0 = 800 units, squared
    mtc1 t2,f4
    c.lt.s f2,f4
    bc1f tg_go                    # too far: he stays free
    nop
    sw a1,0x7E34(t7)              # the first hero (the script's own)
    sw t3,0x7E38(t7)              # the second hero
tg_do:
    sw t9,0x7E3C(t7)              # the captor's word
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,40(sp)
    swc1 f12,32(sp)
    addiu t2,zero,1
    sw t2,0x7E30(t7)
    jal 0x00180378                # the same move on the other hero of the pair
    move a1,t3
    lui t7,0x000E
    sw zero,0x7E30(t7)
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f12,32(sp)
    addiu sp,sp,64
tg_go:
    addiu sp,sp,-48               # the two instructions that sat at 0x00180378
    j 0x00180380
    swc1 f20,32(sp)
th_new:                           # from 0x00171FE4 (was jal 0x0016CF00): a new context for a script that is hooked onto
    addiu sp,sp,-80               # an object. a0 = the script root, a1 = 0, a2 = the function, a3 = [object, extra], t0 = how many
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
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tn_out
    nop
    lw t2,0(t2)
    beq t2,zero,tn_out            # he is down
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
    lui t2,0x491C
    ori t2,t2,0x4000              # 800 units, squared
    mtc1 t2,f4
    c.lt.s f2,f4
    bc1f tn_out                   # too far: he stays free
    lui t7,0x000E
    sw t8,0x7E34(t7)              # the first hero
    sw t3,0x7E38(t7)              # the second hero
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
    ld t9,24(sp)
    lw t2,4(t9)
    sw t3,48(sp)                  # the second array: [the second hero, the same extra object]
    sw t2,52(sp)
    sd t3,56(sp)
    ld a0,8(sp)
    move a1,zero
    ld a2,16(sp)
    addiu a3,sp,48
    jal 0x0016CF00                # his own context of the same function
    ld t0,32(sp)
    ld a0,56(sp)
    jal 0x00177460                # hooked onto him
    move a1,v0
tn_out:
    ld v0,40(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,80
th_tick:                          # from 0x00177510 (the forty-third glue's jal hs_tick, or the game's runner): a hero's
    addiu sp,sp,-16               # hooked script runs. Noted, so that tg_cap leaves its captures alone.
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
tg_tick:                          # from 0x00138538 (the field's START look-out, each step): the safety rule
    lui t7,0x000E
    lw t3,0x7E38(t7)              # the second hero of a pair
    beq t3,zero,tt_go
    lui t5,0x000F
    lw t6,0x05CC(t5)              # the twin
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t3,t6,tt_ok
    nop
    bne t3,t4,tt_clear            # not a hero of this room any more
    nop
tt_ok:
    lw t2,0x7E34(t7)              # the first hero
    beq t2,t6,tt_a
    nop
    bne t2,t4,tt_clear
    nop
tt_a:
    lw t1,0x160(t2)
    andi t1,t1,0x4000
    beq t1,zero,tt_b
    lw t1,-11076(t5)
    b tt_go                       # the first hero is in the move: the clock is fresh
    sw t1,0x7E40(t7)
tt_b:
    lw t0,0x7E40(t7)
    subu t1,t1,t0                 # steps since the first hero (or the last capture) was in it
    lw t0,0x160(t3)
    andi t0,t0,0x4000
    bne t0,zero,tt_b2             # the second hero is still held
    sltiu t0,t1,40
    bne t0,zero,tt_go             # both out, less than 40 steps: between two captures
    nop
    b tt_clear                    # both out: the pair is forgotten
    nop
tt_b2:
    sltiu t0,t1,120
    bne t0,zero,tt_go             # his own end of the move may run a little longer
    nop
    addiu sp,sp,-16               # held for 120 steps after the first hero left: freed
    sd ra,0(sp)
    sd t3,8(sp)
    move a0,t3
    jal 0x00177460                # his hooked script goes
    move a1,zero
    ld t3,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,t3,320
    jal 0x0017EFA0                # "no motion": the game's own way to end a paired move
    move a1,zero
    ld ra,0(sp)
    addiu sp,sp,16
    lui t7,0x000E
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

old = '''        labels, n = add_code(TG_AT, TG_END, tg_src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a boss's paired move is started on the other hero too when he is near")'''
assert s.count(old) == 1, s.count(old)
new = '''        hook_next = words.get(0x00177510, game_word(0x00177510))           # jal hs_tick (forty-third glue), or the game's jal 0x0016CD48
        assert (hook_next >> 26) == 3
        labels, n = add_code(TG_AT, TG_END, tg_src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "HOOK_NEXT": (hook_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: both heroes in a boss's paired move (the second hero gets his own copy of the hooked script)")
        if 0x00177510 in words:
            hook_base(0x00177510, hook_next, jal(labels["th_tick"]), "a hero's hooked script runs: noted")
        else:
            hook_game(0x00177510, hook_next, jal(labels["th_tick"]), "a hero's hooked script runs: noted")
        hook_game(0x00171FE4, 0x0C05B3C0, jal(labels["th_new"]), "a script is hooked onto a hero: the other hero of the pair gets his own copy")'''
s = s.replace(old, new)

# the forty-seventh glue's "drop": the second form (each hero of a pair presses for himself)
old_a = s.index('            rc_src = rc_src.replace(x, """rc_drop:')
old_b = s.index('""")', old_a) + 4
new_rc = '''            rc_src = rc_src.replace(x, """rc_drop:
    lui t7,0x000E
    lw t2,0x7E38(t7)              # (--together) a pair in a move: each of the two presses for himself
    beq t2,zero,rc_drop2
    nop
    beq t2,a1,rc_send
    lw t2,0x7E34(t7)
    beq t2,a1,rc_send
    nop
rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")'''
s = s[:old_a] + new_rc + s[old_b:]
x = "TG_END = 0x000EA000"
assert s.count(x) == 1
s = s.replace(x, "TG_END = 0x000EA400")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
