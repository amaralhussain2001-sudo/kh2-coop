"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue; plan row 9, second half) in its
second form, after the runs tg1, tg2, tg3:
 - only in Shan-Yu's room (world 08, room 09) for now;
 - the second hero is noted (who the script's own hero is, who the second, which captor), every later capture of
   the first is copied to him, and his "held by" word is set to a mark so that the hold rules of the glues 36 to
   47 keep seeing ONE held hero (the script's own);
 - a release rule at the field's START look-out: 20 steps after the script's own hero has left the move, the
   second hero's motion is ended with the game's own "no motion" call 0x0017EFA0(part, 0);
 - the green command goes to BOTH menus (a second pass through the offer routine 0x00189E18);
 - the second hero's command is sent to the boss AS THE FIRST HERO's (the forty-seventh glue would drop it).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tg_tick" in s:
    raise SystemExit("already there")

a = s.index('TG_SRC = """')
b = s.index('"""' + chr(10) + 'TG_HOOK')
new_src = '''TG_SRC = """
tg_cap:                           # jump at 0x00180378 (its first two instructions are at tg_go). a0 = the captor's
    lui t7,0x000E                 # motion part, a1 = the victim, a2 = the motion number, f12 = the time
    lw t6,0x7E30(t7)
    bne t6,zero,tg_go             # this IS the second call
    lui t5,0x000F
    lw t6,0x05CC(t5)              # the twin
    beq t6,zero,tg_go
    lui t5,0x0035
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
    bne t2,t3,tg_new              # is the other hero the second one of this move already?
    lw t2,0x7E3C(t7)
    beq t2,t9,tg_do               # yes: every capture is copied to him
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
    sw a1,0x7E34(t7)              # the script's own hero
    sw t3,0x7E38(t7)              # the second hero
    sw t9,0x7E3C(t7)              # the captor's word
tg_do:
    lw t2,-11076(t5)              # the game's counter: the first hero is in the move now
    sw t2,0x7E40(t7)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,40(sp)
    sd t3,48(sp)
    swc1 f12,32(sp)
    addiu t2,zero,1
    sw t2,0x7E30(t7)
    jal 0x00180378                # the same move on the second hero
    move a1,t3
    lui t7,0x000E
    sw zero,0x7E30(t7)
    ld t3,48(sp)
    addiu t2,zero,-1
    sw t2,0x240(t3)               # a mark instead of the captor's word: the hold rules see ONE held hero
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
tg_tick:                          # from 0x00138538 (the field's START look-out, each step): the release rule
    lui t7,0x000E
    lw t3,0x7E38(t7)              # the second hero of a move
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
    lw t2,0x7E34(t7)              # the script's own hero
    beq t2,t6,tt_a
    nop
    bne t2,t4,tt_free2
    nop
tt_a:
    lw t9,0x7E3C(t7)              # the captor's word
    lw t1,0x240(t2)
    bne t1,t9,tt_free
    lw t1,0x160(t2)
    andi t1,t1,0x4000
    beq t1,zero,tt_free
    lw t1,-11076(t5)
    b tt_go                       # the first hero is in the move: note the time
    sw t1,0x7E40(t7)
tt_free:
    lw t1,-11076(t5)
    lw t0,0x7E40(t7)
    subu t1,t1,t0
    sltiu t1,t1,20
    bne t1,zero,tt_go             # less than 20 steps out of it: between two captures
    nop
tt_free2:
    lw t1,0x160(t3)
    andi t1,t1,0x4000
    beq t1,zero,tt_clear          # the second hero is out already
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,t3,320               # his motion part
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
    lw t2,0x7E38(t3)              # a move with two heroes of this source?
    beq t2,zero,tr_held
    lw t5,0x7E3C(t3)
    bne t5,t4,tr_held
    nop
    lw s0,0x7E34(t3)              # this pass: the script's own hero
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
x = "TG_END = 0x000E9E00"
assert s.count(x) == 1
s = s.replace(x, "TG_END = 0x000EA000")

old = '''        labels, n = add_code(TG_AT, TG_END, tg_src, {}, "EXPERIMENT: a boss's paired move is started on the other hero too when he is near")
        a, w0, w1 = TG_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["tg_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first tg_cap")
        hook_game(a + 4, w1, 0, "(swc1 f20,32(sp) is done in tg_go)")
        n_glue += n + 2
'''
assert s.count(old) == 1, s.count(old)
new = '''        tick_next = words[0x00138538]                                      # jal pad_both, or jal ms_tick with --ownmenu
        assert (tick_next >> 26) == 3
        labels, n = add_code(TG_AT, TG_END, tg_src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a boss's paired move is started on the other hero too when he is near")
        a, w0, w1 = TG_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["tg_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first tg_cap")
        hook_game(a + 4, w1, 0, "(swc1 f20,32(sp) is done in tg_go)")
        hook_base(0x00138538, tick_next, jal(labels["tg_tick"]), "the field's START look-out: first the release rule of a move with two heroes")
        hook_base(0x00189E3C, jal(RH_AT), jal(labels["tg_ro"]), "a motion offers a command: to both heroes of a move with two")
        n_glue += n + 2
'''
s = s.replace(old, new)

# the forty-seventh glue's "drop" gets a way through for the second hero of a move (only with --together)
old = '''        labels, n = add_code(RC_AT, RC_END, RC_SRC, {}, "a hero's Reaction Command: the sender is the player; one object holds one hero")'''
assert s.count(old) == 1, s.count(old)
new = '''        rc_src = RC_SRC
        if "--together" in sys.argv:                                       # (the experiment of the fiftieth glue)
            x = """rc_drop:
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
"""
            assert rc_src.count(x) == 1
            rc_src = rc_src.replace(x, """rc_drop:
    lui t7,0x000E
    lw t2,0x7E38(t7)              # (--together) is THIS hero the second one of the source's move?
    bne t2,a1,rc_drop2
    lw t2,0x7E3C(t7)
    bne t2,t9,rc_drop2
    nop
    b rc_send                     # yes: his command is sent as the first hero's
    lw a1,0x7E34(t7)
rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")
        labels, n = add_code(RC_AT, RC_END, rc_src, {}, "a hero's Reaction Command: the sender is the player; one object holds one hero")'''
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
