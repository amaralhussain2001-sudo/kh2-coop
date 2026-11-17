"""One-off: tools/merge/merge_v7.py gets the SIXTY-FIFTH GLUE (built only with --holdpair, with --together):
BOTH HEROES INSIDE THE SAME HOLD OF A BOSS (plan row 9, second half, the other fights; the user's answer B of the
ninth round: no OK for "a hold takes one hero only"), AND A BOSS THAT IS BUSY WITH ONE HERO DOES NOT ANSWER THE OTHER
HERO'S COMMAND IN THE GAPS OF A HOLD (job 4: the Groundshaker's lost hold).

Read (ninth round, part 93):
 - a boss's hold is made of script calls that name ONE hero: capture (trap 1,29 -> 0x00180378), attach to a bone
   (1,18 -> 0x00171C60 -> 0x001C0D38), detach (1,102), "go idle" (1,74), flags (1,70 / 1,71), place and direction
   (1,148 / 1,79), and the motion calls on the hero (1,11 / 1,12 / 1,13). In 9 of the 11 bosses the sequence is
   driven by ONE script (the boss's act, or a script hooked onto the hero that also starts the boss's acts): a
   second copy of that script for the second hero (the fiftieth glue's way for Shan-Yu) would drive the boss
   twice.
 - the Groundshaker's FE / FD steps are the ANSWERS to a hero's Reaction Command (B_LK120, REACTION_CALLBACK ->
   L4217 / L4149). In the fault's run the free hero got an FE while the boss was between two steps with the other
   hero: the forty-seventh glue's "one object holds one hero" looks at "held at this moment or noted less than
   90 steps ago", and the note was only written when a script asked for "the player".
What the glue does (0x000ECF40 ..; values 0x000E7EA0 .. 0x000E7EBF), in every room but Shan-Yu's (the fiftieth
glue's own pair there):
 hp_form   A PAIR is made when an enemy's script (not a hero's, not a helper's) captures a hero or attaches him
           to itself, NOT as the answer to a hero's own command, and the other hero is up, free (not held, no
           hooked script) and within 500 units: the first hero, the second hero, the captor.
 hp_cap    (the jump at 0x00180378, in front of the glues that sit there) a capture on one hero of a living pair
           by its captor is made on the other hero too.
 hp_att, hp_mirH, hp_mirD (the script call table's words for attach, detach, idle, set flag, reset flag, set
           place, set direction, motion start / change / push): while the pair lives and the captor's script
           runs, a call for one hero of the pair is made for the other hero too. So the second hero is a MIRROR
           of the first all through the hold, and ONE script drives it. (The mirrored attach carries no callback.)
 hp_tick   (0x00138538) each step: (1) the hold note of the glues 36 / 39 / 47 (0x000E7C0C ..) is written while a
           hero is held, and kept fresh while he has a hooked script: a sequence has no gaps any more; (2) the
           pair is forgotten 10 steps after neither hero is held or hooked; a hero of the pair who is still in a
           captured motion, has no hooked script, is not the hero the script named last, and whose partner has been
           free for 40 steps is let go the
           game's own way (0x0017EFA0, 0x0016BD60, and 0x001C0E60 when he is attached).
 And in the forty-seventh glue: both heroes of a living pair may press the captor's command, once a step.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdpair.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hp_form" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTY-FIFTH GLUE (built only with the option --holdpair, with --together): BOTH HEROES INSIDE THE SAME HOLD OF A
BOSS, in every room but Shan-Yu's (plan row 9, the other fights), AND NO GAPS IN "THIS BOSS IS BUSY WITH A HERO"
(the Groundshaker's lost hold). hp_form makes a PAIR when an enemy's script captures a hero or attaches him to
itself (not as the answer to a hero's own command) and the other hero is up, free and within 500 units; hp_cap
(0x00180378) and the wrappers of ten script calls (attach, detach, idle, flags, place, direction, the motion
calls) make every call of the captor's script for one hero of the pair for the other hero too: the second hero
is a mirror of the first, one script drives the hold. hp_tick: the hold note of the glues 36 / 39 / 47 is
written each step while a hero is held or hooked; the pair is forgotten when the hold is over; a mirror left
behind is let go after 40 steps. In glue 47 both heroes of a pair may press the captor's command, once a step.

'''
s = s.replace(a, hdr + a)
b = " [--bindname]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--holdpair]")

i = s.index("def main():")
src = '''# ---- sixty-fifth glue (only with --holdpair) ----------------------------------------------------------------
HP_AT = 0x000ECF40
HP_END = 0x000ED800
HP_TRAPS = (                                       # (the script call, its table word, the game's handler, its inputs, the kind of its first argument)
    (102, 0x0034E030, 0x00171CC0, "H"),            # detach
    (74, 0x0034DF50, 0x001723D0, "H"),             # go idle
    (70, 0x0034DF30, 0x00173AE8, "H"),             # set a flag
    (71, 0x0034DF38, 0x00173B20, "H"),             # reset a flag
    (148, 0x0034E1A0, 0x00171460, "H"),            # set the place
    (79, 0x0034DF78, 0x00173C18, "H"),             # set the direction
    (11, 0x0034DD58, 0x00171150, "D"),             # motion start
    (12, 0x0034DD60, 0x001711B0, "D"),             # motion change
    (13, 0x0034DD68, 0x001711E0, "D"),             # motion push
)
HP_SRC = """
hp_two:                           # out: t6 = the twin, t4 = player 1's hero (0 = not there), t5 = 0x00350000, t7 = 0x000E0000
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lui t5,0x0035
    lw t4,0x2400(t5)
    jr ra
    lui t7,0x000E

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

hp_form:                          # in: a0 = a hero, a1 = the object that takes him. Out: v0 = the other hero when a pair is made (noted), or 0
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,hf_no
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,hf_no
    lui t7,0x000E
    beq a0,t6,hf_h
    move t3,t4
    bne a0,t4,hf_no               # he is no hero
    move t3,t6
hf_h:
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
    lw t2,0x7C18(t7)              # the forty-seventh glue's note: a hero's own command is being answered
    bne t2,zero,hf_no             # yes: he does that move alone
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,hf_no
    nop
    lw t2,0(t2)
    beq t2,zero,hf_no             # he is down
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,hf_no             # he is held already
    lw t2,0xAEC(t3)
    bne t2,zero,hf_no             # he has a hooked script
    lw t2,0x154(t3)
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,hf_no               # he is in a captured motion
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
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
    bc1f hf_no                    # too far: he stays free
    nop
    sw a0,0x7EA0(t7)              # THE PAIR: the first hero, the second hero, the captor
    sw a0,0x7EBC(t7)              # (the hero the script named last)
    sw t3,0x7EA4(t7)
    sw a1,0x7EA8(t7)
    lw t2,-11076(t5)
    sw t2,0x7EAC(t7)
    sw zero,0x7EB4(t7)
    sw zero,0x7EB8(t7)
    jr ra
    move v0,t3
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
    beq t0,zero,hq_new
    addiu a1,a0,-320              # the captor object
    jal hp_other                  # a pair lives: is the victim one of the two, and is this its captor
    ld a0,16(sp)
    b hq_have
    nop
hq_new:
    jal hp_form                   # no pair: is this the start of a hold that takes the other hero too
    ld a0,16(sp)
hq_have:
    beq v0,zero,hq_back
    lui t7,0x000E
    ld t1,16(sp)
    sw t1,0x7EBC(t7)              # the hero the script named: the other one is his mirror
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

hp_scr:                           # in: a0 = an object. Out: v0 = his partner when he is a hero of the living pair AND the captor's script is running, else 0
    lui t5,0x0035
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,hs_no
    lui t7,0x000E
    lw t8,56(t8)                  # its object
    lw t2,0x7EA8(t7)
    bne t8,t2,hs_no
    move a1,t2
    j hp_other
    nop
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
    jal hp_other
    nop
    b ha_have
    nop
ha_new:
    jal hp_form
    nop
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

hp_tick:                          # from 0x00138538 (each step the field looks for START)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    lui t7,0x000F
    lw a0,0x05CC(t7)              # the twin
    jal hp_note
    addiu a1,zero,1
    lui t5,0x0035
    lw a0,0x2400(t5)              # player 1's hero
    jal hp_note
    addiu a1,zero,2
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
    lui t7,0x000E
    or t0,s2,v0
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
    b hk_out
    sw zero,0x7EA8(t7)
hk_some:
    sw zero,0x7EB4(t7)
    and t0,s2,v0
    bne t0,zero,hk_both
    nop
    bne s2,zero,hk_one            # only the first hero is busy: is he a mirror left behind
    move a0,s0
    move a0,s1
hk_one:
    lw t2,0x7EBC(t7)
    beq a0,t2,hk_both             # he is the hero the script named last: a live hold is never cut (the sixtieth glue's minute stays)
    nop
    lw t2,0xAEC(a0)
    bne t2,zero,hk_both           # he has a hooked script: his move is alive
    lw t2,0x154(a0)
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    bne t2,t1,hk_both             # he is in no captured motion
    lw t1,0x7EB8(t7)
    addiu t1,t1,1
    slti t2,t1,40
    bne t2,zero,hk_out
    sw t1,0x7EB8(t7)
    sd a0,32(sp)                  # 40 steps alone in a captured motion with the partner free: he is let go
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
hk_both:
    sw zero,0x7EB8(t7)
hk_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    addiu sp,sp,64
    j TICK_NEXT
    move a0,zero
"""


'''
s = s[:i] + src + s[i:]

# the forty-seventh glue: both heroes of a living pair may press the captor's command, once a step
x = '''rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")
'''
assert s.count(x) == 1
y = '''rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")
            if "--holdpair" in sys.argv:                                   # (the sixty-fifth glue's pair: both heroes are in the captor's hold)
                x = """rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
"""
                assert rc_src.count(x) == 1
                rc_src = rc_src.replace(x, """rc_drop2:
    lui t7,0x000E
    lw t2,0x7EA0(t7)              # (--holdpair) both heroes are in this captor's hold: either may press, once a step
    beq t2,zero,rc_drop3
    lw t1,0x7EA8(t7)
    bne t1,a0,rc_drop3
    lw t1,0x7EA4(t7)
    beq t2,a1,rc_pair
    nop
    bne t1,a1,rc_drop3
    nop
rc_pair:
    lw t2,0x7C1C(t7)              # the step of the last command that was sent
    lw t1,-11076(t5)
    bne t2,t1,rc_send
    nop
rc_drop3:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")
'''
s = s.replace(x, y)

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--holdpair" in sys.argv:                                           # sixty-fifth glue (both heroes inside the same hold of a boss)
        assert "--together" in sys.argv, "--holdpair needs --together (the forty-seventh glue's pair exit)"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        cap_next = words.get(0x00180378)
        assert cap_next is not None and (cap_next >> 26) == 2
        stubs = ""
        for num, tab, fn, kind in HP_TRAPS:
            stubs += "hp_t%d:\\n    lui t0,0x%04X\\n    j hp_mir%s\\n    ori t0,t0,0x%04X\\n" % (num, fn >> 16, kind, fn & 0xFFFF)
        labels, n = add_code(HP_AT, HP_END, HP_SRC.replace("@STUBS@", stubs),
                             {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "CAP_NEXT": (cap_next & 0x3FFFFFF) << 2},
                             "both heroes inside the same hold of a boss; the hold note is written each step")
        hook_base(0x00138538, tick_next, jal(labels["hp_tick"]), "the field's START look-out: first, the hold note and the pair of a hold")
        hook_base(0x00180378, cap_next, (2 << 26) | ((labels["hp_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first, the other hero of a hold's pair")
        hook_game(0x0034DD90, 0x00171C60, labels["hp_att"], "the script call 'attach': the other hero of the pair too")
        for num, tab, fn, kind in HP_TRAPS:
            hook_game(tab, fn, labels["hp_t%d" % num], "the script call (1,%d): the other hero of the pair too" % num)
        n_glue += n + 1 + len(HP_TRAPS)

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
