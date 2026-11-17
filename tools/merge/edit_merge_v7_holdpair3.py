"""One-off: THE SIXTY-FIFTH GLUE of tools/merge/merge_v7.py (--holdpair), THIRD FORM (ninth round, jobs 3 and 4).
What the runs of the second form (candidate v104, tools/own/r9_chain17.sh) and the fault's own run of the
Groundshaker with the capture log (run gsC) showed, and what this form does about it:
  1. A pair was only made when the other hero stood within 500 units. The user gave no OK for "the other stays
     free": the distance test is gone. A boss's own grab takes both heroes wherever the second one stands.
  2. A captured motion is not only action FC .. FF: the moves 0x100 .. 0x103 exist too (the last Xemnas's opening
     move 0x101: the mirror hero stayed in it for 932 frames). "Held" is now the held bit (object + 0x160, bit
     0x4000) or an action FC .. FF.
  3. The hooked piece of the captor's script runs AS the hero the script named; its calls were not mirrored, so
     the mirror hero was not let go when the named hero was. Now the calls of a pair hero's own hooked piece are
     mirrored as the captor's are (not when that hero is in a move he started with his own command).
  4. A move a hero started with his own Reaction Command goes on with captures that no command sends (Xaldin's
     jumps, Demyx's water forms). Such a hero is noted (0x000E7EC4 player 1's, 0x000E7EC8 the twin's: the captor;
     + 8 the idle steps; forgotten 45 idle steps after the move) and makes no pair.
  5. THE GROUNDSHAKER'S CAUSE (its attack-hit routine captures whichever hero the attack hits, while its ride runs
     with the other hero): a capture of a free hero by a captor whose sequence runs with the OTHER hero (held by
     it, or hooked with a fresh hold note) makes a WEAK pair (0x000E7EC0 = 1): nothing is mirrored; the
     bystander is let go after 60 steps when he is held, has no hooked script and the script has not named
     him again (then 0x000E7EC0 = 2 and no rule touches the pair).
  6. A mirror hero is also let go when no call of the script named the pair for 600 steps (it was: only when
     the named hero is free for 40 steps).
The room grows to 0x000ECF40 .. 0x000EDC00. Without the option the builder writes what it wrote before.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdpair3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hp_bare:" in s:
    raise SystemExit("already there")
a = "HP_END = 0x000ED800" + NL
assert s.count(a) == 1
s = s.replace(a, "HP_END = 0x000EDC00" + NL)
i = s.index('HP_SRC = """')
j = s.index('"""' + NL, i + 12) + len('"""' + NL)
NEW = r'''HP_SRC = """
hp_other:                         # in: a0 = a hero, a1 = a captor object (0 = any). Out: v0 = his partner in the living pair, or 0
    lui t7,0x000E
    lw t0,0x7EA0(t7)
    beq t0,zero,ho_no
    lw t1,0x7EA4(t7)
    beq a1,zero,ho_any
    lw t2,0x7EA8(t7)
    bne a1,t2,ho_no               # another captor
    nop
ho_any:
    beq a0,t0,ho_yes
    move v0,t1
    bne a0,t1,ho_no
    move v0,t0
ho_yes:
    lui t3,0x000F                 # the partner must still be a hero of this room
    lw t3,0x05CC(t3)
    beq v0,t3,ho_ok
    lui t3,0x0035
    lw t3,0x2400(t3)
    bne v0,t3,ho_no
    nop
ho_ok:
    jr ra
    nop
ho_no:
    jr ra
    move v0,zero

hp_ownset:                        # in: a0 = an object, a1 = the object that takes it. A hero whose OWN command is being answered: noted
    lui t7,0x000E
    lw t1,0x7C18(t7)              # the forty-seventh glue's note: the hero whose command is being answered
    beq t1,zero,hz_out
    nop
    bne t1,a0,hz_out
    lui t6,0x000F
    lw t6,0x05CC(t6)
    bne a0,t6,hz_p1
    lui t5,0x0035
    jr ra
    sw a1,0x7EC8(t7)              # the twin is in a move of his own command
hz_p1:
    lw t4,0x2400(t5)
    bne a0,t4,hz_out
    nop
    sw a1,0x7EC4(t7)              # player 1's hero is
hz_out:
    jr ra
    nop

hp_form:                          # in: a0 = a hero (the victim), a1 = the object that takes him. Out: v0 = the other hero when a FULL pair is made (the caller mirrors the call), else 0 (no pair, or a weak pair)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,hf_no
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,hf_no
    lui t7,0x000E
    beq a0,t4,hf_p1               # the victim is player 1's hero
    nop
    bne a0,t6,hf_no               # he is no hero
    nop
    move t3,t4                    # the victim is the twin: the other hero is player 1's
    addiu t9,zero,2               # (the other hero's number in the hold note)
    lw t8,0x7EC8(t7)              # the victim's "own move" note
    b hf_h
    lw t0,0x7EC4(t7)              # the other hero's
hf_p1:
    move t3,t6
    addiu t9,zero,1
    lw t8,0x7EC4(t7)
    lw t0,0x7EC8(t7)
hf_h:
    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    beq t2,t1,hf_no               # Shan-Yu's room: the fiftieth glue's own pair
    srl t2,a1,22
    addiu t2,t2,-6
    bne t2,zero,hf_no             # the captor is not an object
    nop
    beq a1,t4,hf_no               # a hero or a helper holds him (a Limit ...): as the game
    nop
    beq a1,t6,hf_no
    lw t2,0(a1)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,hf_no
    lw t2,0x7C18(t7)
    bne t2,zero,hf_no             # a hero's own command is being answered: he does that move alone
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,hf_no
    nop
    lw t2,0(t2)
    beq t2,zero,hf_no             # he is down
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,hf_join           # he is held
    lw t2,0xAEC(t3)
    bne t2,zero,hf_join           # he has a hooked script
    lw t2,0x154(t3)
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,hf_join             # he is in a captured motion
    nop
    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command
    nop
    sw a0,0x7EA0(t7)              # A FULL PAIR: the hero the script names, the other hero, the captor
    sw a0,0x7EBC(t7)              # (the hero the script named last)
    sw t3,0x7EA4(t7)
    sw a1,0x7EA8(t7)
    sw zero,0x7EC0(t7)
    lw t2,-11076(t5)
    sw t2,0x7EAC(t7)
    sw zero,0x7EB4(t7)
    sw zero,0x7EB8(t7)
    jr ra
    move v0,t3
hf_join:                          # the other hero is busy: is he in THIS captor's sequence?
    lw t1,0x140(a1)               # the captor's word
    beq t1,zero,hf_no
    lw t2,0x240(t3)
    bne t2,t1,hf_jn               # not held by it at this moment: does the hold note say so?
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,hf_weak
    nop
hf_jn:
    lw t2,0x7C0C(t7)
    bne t2,t1,hf_no
    lw t2,0x7C10(t7)
    bne t2,t9,hf_no
    lw t2,-11076(t5)
    lw t1,0x7C14(t7)
    subu t2,t2,t1
    sltiu t2,t2,90
    beq t2,zero,hf_no
    nop
hf_weak:
    sw t3,0x7EA0(t7)              # A WEAK PAIR: the hero of the captor's sequence, the bystander it captures now
    sw t3,0x7EBC(t7)
    sw a0,0x7EA4(t7)
    sw a1,0x7EA8(t7)
    addiu t2,zero,1
    sw t2,0x7EC0(t7)
    lw t2,-11076(t5)
    sw t2,0x7EAC(t7)
    sw zero,0x7EB4(t7)
    sw zero,0x7EB8(t7)
hf_no:
    jr ra
    move v0,zero

hp_cap:                           # jump at 0x00180378, in front of the glues there. a0 = the captor's motion part, a1 = the victim, a2 = the move
    lui t7,0x000E
    lw t0,0x7EB0(t7)
    bne t0,zero,hq_go             # (the mirror's own call)
    nop
    addiu sp,sp,-96
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    swc1 f12,40(sp)
    swc1 f13,44(sp)
    swc1 f14,48(sp)
    lw t0,0x7EA0(t7)
    addiu a1,a0,-320              # the captor object
    beq t0,zero,hq_new
    ld a0,16(sp)
    jal hp_other                  # a pair lives: is the victim one of the two, and is this its captor
    nop
    beq v0,zero,hq_back
    lui t7,0x000E
    ld t1,16(sp)
    lw t2,0x7EC0(t7)
    beq t2,zero,hq_mir
    sw t1,0x7EBC(t7)              # the hero the script named
    lw t3,0x7EA4(t7)              # a weak pair: nothing is mirrored
    bne t1,t3,hq_back
    addiu t2,zero,2
    b hq_back
    sw t2,0x7EC0(t7)              # ... and its bystander is named again: he is in a sequence of his own now
hq_new:
    jal hp_ownset                 # no pair: a hero's own command? then the move is noted as his own
    nop
    ld a1,8(sp)
    addiu a1,a1,-320
    jal hp_form                   # is this the start of a hold that takes the other hero too
    ld a0,16(sp)
    beq v0,zero,hq_back
    lui t7,0x000E
hq_mir:
    addiu t1,zero,1
    sw t1,0x7EB0(t7)
    lui t5,0x0035
    lw t1,-11076(t5)
    sw t1,0x7EAC(t7)
    move a1,v0
    ld a0,8(sp)
    ld a2,24(sp)
    ld a3,32(sp)
    lwc1 f13,44(sp)
    lwc1 f14,48(sp)
    jal 0x00180378                # the same move on the other hero
    lwc1 f12,40(sp)
    lui t7,0x000E
    sw zero,0x7EB0(t7)
hq_back:
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,32(sp)
    lwc1 f12,40(sp)
    lwc1 f13,44(sp)
    lwc1 f14,48(sp)
    addiu sp,sp,96
hq_go:
    j CAP_NEXT
    nop

hp_scr:                           # in: a0 = an object. Out: v0 = his partner when he is a hero of the living FULL pair AND the call comes from the captor's script or from his own hooked piece of it, else 0
    lui t5,0x0035
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,hs_no
    lui t7,0x000E
    lw t2,0x7EC0(t7)
    bne t2,zero,hs_no             # a weak pair: nothing is mirrored
    lw t8,56(t8)                  # its object
    lw t2,0x7EA8(t7)
    beq t8,t2,hs_ok               # the captor's own script
    nop
    bne t8,a0,hs_no               # ... or the hooked piece of it that runs AS this hero
    lui t6,0x000F
    lw t1,0xAEC(a0)
    beq t1,zero,hs_no
    lw t6,0x05CC(t6)              # the twin
    lw t1,0x7EC4(t7)              # player 1's "own move" note
    bne a0,t6,hs_o2
    nop
    lw t1,0x7EC8(t7)              # the twin's
hs_o2:
    bne t1,zero,hs_no             # the piece belongs to a move he started with his own command
    nop
hs_ok:
    j hp_other
    move a1,t2
hs_no:
    jr ra
    move v0,zero

hp_att:                           # the script call "attach" (1,18; was 0x00171C60). a0 = its inputs: the child, the parent, the bone, a flag, a callback, its value
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x00171C60                # the game's attach for the hero the script names
    nop
    sd v0,16(sp)
    lui t7,0x000E
    lw t0,0x7EB0(t7)
    bne t0,zero,ha_out
    ld a0,8(sp)
    lw t1,0(a0)
    beq t1,zero,ha_out
    lw t2,4(a0)
    beq t2,zero,ha_out
    lw t0,0x7EA0(t7)
    lw a1,4(t2)                   # the parent object
    beq t0,zero,ha_new
    lw a0,4(t1)                   # the child object
    lw t0,0x7EC0(t7)
    bne t0,zero,ha_out            # a weak pair: nothing is mirrored
    nop
    jal hp_other
    nop
    b ha_have
    nop
ha_new:
    sd a0,40(sp)
    sd a1,48(sp)
    jal hp_ownset
    nop
    ld a0,40(sp)
    jal hp_form
    ld a1,48(sp)
ha_have:
    beq v0,zero,ha_out
    ld a0,8(sp)
    lw t1,0(a0)
    lw t2,4(t1)
    sd t2,24(sp)                  # the child the script named
    sw v0,4(t1)                   # ... is the other hero for one more call
    lw t3,16(a0)
    sd t3,32(sp)
    sw zero,16(a0)                # (without the script's callback: one hero's attach carries it)
    lui t7,0x000E
    sw t2,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    jal 0x00171C60
    sw t3,0x7EAC(t7)
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    lw t1,0(a0)
    ld t2,24(sp)
    sw t2,4(t1)
    ld t3,32(sp)
    sw t3,16(a0)
ha_out:
    ld v0,16(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,64

hp_mirH:                          # a script call whose first input is an object's handle. a0 = the inputs, t0 = the game's handler
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd t0,16(sp)
    jalr t0                       # the game's call for the object the script names
    nop
    sd v0,24(sp)
    lui t7,0x000E
    lw t1,0x7EA0(t7)
    beq t1,zero,mh_out            # no pair
    lw t1,0x7EB0(t7)
    bne t1,zero,mh_out
    ld a0,8(sp)
    lw t2,0(a0)
    beq t2,zero,mh_out
    nop
    jal hp_scr
    lw a0,4(t2)                   # the object
    beq v0,zero,mh_out
    ld a0,8(sp)
    lw t2,0(a0)
    lw t3,4(t2)
    sd t3,32(sp)
    sw v0,4(t2)                   # the other hero of the pair, for one more call
    lui t7,0x000E
    sw t3,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    sw t3,0x7EAC(t7)
    ld t0,16(sp)
    jalr t0
    nop
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    lw t2,0(a0)
    ld t3,32(sp)
    sw t3,4(t2)
mh_out:
    ld v0,24(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48

hp_mirD:                          # a script call whose first input is the object itself. a0 = the inputs, t0 = the game's handler
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd t0,16(sp)
    jalr t0
    nop
    sd v0,24(sp)
    lui t7,0x000E
    lw t1,0x7EA0(t7)
    beq t1,zero,md_out
    lw t1,0x7EB0(t7)
    bne t1,zero,md_out
    ld a0,8(sp)
    jal hp_scr
    lw a0,0(a0)                   # the object
    beq v0,zero,md_out
    ld a0,8(sp)
    lw t3,0(a0)
    sd t3,32(sp)
    sw v0,0(a0)
    lui t7,0x000E
    sw t3,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    sw t3,0x7EAC(t7)
    ld t0,16(sp)
    jalr t0
    nop
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    ld t3,32(sp)
    sw t3,0(a0)
md_out:
    ld v0,24(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
@STUBS@
hp_rc:                            # jump from the forty-seventh glue's rc_drop2 ("this hero's command does nothing"): a0 = the source, a1 = the hero, t5 = 0x00350000
    lui t7,0x000E
    lw t2,0x7EA0(t7)              # both heroes are in this captor's hold (a full pair): either may press, once a step
    beq t2,zero,hr_drop
    lw t1,0x7EC0(t7)
    bne t1,zero,hr_drop
    lw t1,0x7EA8(t7)
    bne t1,a0,hr_drop
    lw t1,0x7EA4(t7)
    beq t2,a1,hr_pair
    nop
    bne t1,a1,hr_drop
    nop
hr_pair:
    lw t2,0x7C1C(t7)              # the step of the last command that was sent
    lw t1,-11076(t5)
    beq t2,t1,hr_drop
    nop
    j RC_SEND
    nop
hr_drop:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop

hp_note:                          # in: a0 = a hero (or 0), a1 = 1 (the twin) / 2 (player 1's). The hold note of the glues 36 / 39 / 47, each step
    beq a0,zero,hn_out
    lui t7,0x000E
    lui t5,0x0035
    lw t1,-11076(t5)              # the game's counter
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    beq t2,zero,hn_hook           # not held at this moment
    lw t3,0x240(a0)               # the captor's word
    beq t3,zero,hn_hook
    nop
    sw t3,0x7C0C(t7)              # held: the note is written
    sw a1,0x7C10(t7)
    jr ra
    sw t1,0x7C14(t7)
hn_hook:
    lw t2,0xAEC(a0)
    beq t2,zero,hn_out            # no hooked script either
    lw t3,0x7C10(t7)
    bne t3,a1,hn_out              # the note is about the other hero
    nop
    sw t1,0x7C14(t7)              # still in the sequence (a hooked script): the note stays fresh
hn_out:
    jr ra
    nop

hp_busy:                          # in: a0 = a hero. Out: v0 = 1 when he is held, has a hooked script or is in a captured motion
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    bne t2,zero,hb_yes
    lw t2,0xAEC(a0)
    bne t2,zero,hb_yes
    lw t2,0x154(a0)
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,hb_yes
    nop
    jr ra
    move v0,zero
hb_yes:
    jr ra
    addiu v0,zero,1

hp_bare:                          # in: a0 = a hero. Out: v0 = 1 when he is held (the held bit, or a captured motion FC .. FF) and has NO hooked script
    lw t2,0xAEC(a0)
    bne t2,zero,hx_no
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    bne t2,zero,hx_yes
    lw t2,0x154(a0)
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,hx_yes
    nop
hx_no:
    jr ra
    move v0,zero
hx_yes:
    jr ra
    addiu v0,zero,1

hp_own:                           # in: a0 = a hero (or 0), a1 = the address of his "own move" note (+ 8: his idle steps). The note is forgotten 45 idle steps after the move
    lw t0,0(a1)
    beq t0,zero,hw_out
    nop
    beq a0,zero,hw_clr
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a1,8(sp)
    jal hp_busy
    nop
    ld a1,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
    bne v0,zero,hw_busy
    lw t1,8(a1)
    addiu t1,t1,1
    slti t2,t1,45
    bne t2,zero,hw_out
    sw t1,8(a1)
hw_clr:
    sw zero,0(a1)
hw_busy:
    sw zero,8(a1)
hw_out:
    jr ra
    nop

hp_tick:                          # from 0x00138538 (each step the field looks for START)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,40(sp)
    lui t7,0x000F
    lw a0,0x05CC(t7)              # the twin
    jal hp_note
    addiu a1,zero,1
    lui t5,0x0035
    lw a0,0x2400(t5)              # player 1's hero
    jal hp_note
    addiu a1,zero,2
    lui t7,0x000F
    lw a0,0x05CC(t7)
    lui t7,0x000E
    jal hp_own                    # the twin's "own move" note
    addiu a1,t7,0x7EC8
    lui t5,0x0035
    lw a0,0x2400(t5)
    lui t7,0x000E
    jal hp_own                    # player 1's
    addiu a1,t7,0x7EC4
    lui t7,0x000E
    lw s0,0x7EA0(t7)              # the pair
    beq s0,zero,hk_out
    lw s1,0x7EA4(t7)
    move a0,s0
    jal hp_other                  # are both still heroes of this room
    move a1,zero
    beq v0,zero,hk_clear
    move a0,s1
    jal hp_other
    move a1,zero
    beq v0,zero,hk_clear
    nop
    jal hp_busy
    move a0,s0
    move s2,v0
    jal hp_busy
    move a0,s1
    move s3,v0
    lui t7,0x000E
    or t0,s2,s3
    bne t0,zero,hk_some
    lw t1,0x7EB4(t7)
    addiu t1,t1,1                 # nobody is held or hooked
    slti t2,t1,10
    bne t2,zero,hk_out
    sw t1,0x7EB4(t7)
hk_clear:
    lui t7,0x000E
    sw zero,0x7EA0(t7)            # the hold is over: the pair is forgotten
    sw zero,0x7EA4(t7)
    sw zero,0x7EA8(t7)
    b hk_out
    sw zero,0x7EC0(t7)
hk_some:
    sw zero,0x7EB4(t7)
    lw t0,0x7EC0(t7)
    beq t0,zero,hk_full
    addiu t1,zero,1
    bne t0,t1,hk_keep             # a weak pair whose bystander was named again: no rule
    nop
    jal hp_bare                   # a weak pair: the bystander (the second hero)
    move a0,s1
    beq v0,zero,hk_keep
    lui t7,0x000E
    move a0,s1
    b hk_count
    addiu t3,zero,60
hk_full:
    lw t2,0x7EBC(t7)
    move a0,s1                    # the mirror hero = the one the script did not name last
    bne t2,s1,hk_m
    move t9,s2                    # (is the named one busy)
    move a0,s0
    move t9,s3
hk_m:
    sd a0,32(sp)
    sd t9,48(sp)
    jal hp_bare
    nop
    ld a0,32(sp)
    ld t9,48(sp)
    beq v0,zero,hk_keep           # the mirror hero is free, or has a hooked script of his own
    lui t7,0x000E
    beq t9,zero,hk_count          # the named hero is free: the mirror hero is left behind
    addiu t3,zero,40
    lui t5,0x0035
    lw t1,-11076(t5)
    lw t2,0x7EAC(t7)
    subu t1,t1,t2
    sltiu t1,t1,1200
    bne t1,zero,hk_keep           # the script named the pair less than 600 steps ago: the hold is alive
    nop
    b hk_free                     # no call for the pair for 600 steps: the mirror hero is let go
    nop
hk_count:
    lw t1,0x7EB8(t7)
    addiu t1,t1,1
    slt t2,t1,t3
    bne t2,zero,hk_out
    sw t1,0x7EB8(t7)
hk_free:
    sd a0,32(sp)                  # he is let go the game's own way
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion"
    move a1,zero
    ld a0,32(sp)
    jal 0x0016BD60                # "go idle"
    move a1,zero
    jal 0x001C0CD8                # is he attached
    ld a0,32(sp)
    beq v0,zero,hk_clear
    nop
    jal 0x001C0E60                # detach
    ld a0,32(sp)
    b hk_clear
    nop
hk_keep:
    lui t7,0x000E
    sw zero,0x7EB8(t7)
hk_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,40(sp)
    addiu sp,sp,64
    j TICK_NEXT
    move a0,zero
"""
'''
s = s[:i] + NEW + s[j:]
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
