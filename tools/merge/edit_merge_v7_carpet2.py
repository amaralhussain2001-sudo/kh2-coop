"""One-off: tools/merge/merge_v7.py gets the FIFTY-SECOND GLUE (built only with --carpet2; an experiment until its
runs are read): A CARPET UNDER PLAYER 2'S HERO ON THE MAGIC CARPET (the vehicle items of the eighth round).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_carpet2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gc_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-SECOND GLUE (built only with the option --carpet2): A CARPET UNDER PLAYER 2'S HERO.
What was there (seventh round, part 7e; disc v5 gives player 2 a carpet RIDER of his own): one carpet only; it
stays under the engine's player, and player 2's hero flies in the riding pose with nothing under him.
Read in the program:
 - the carpet is the object 0x0168 (N_AL010_BTL, kind BTLNPC, status 5008); the BTLNPC class (0x00351078) writes
   the last one built to 0x00351068 and puts it into the action state 19;
 - state 19's own routine 0x001B2DB8 (the word at 0x00350FF8 in that state's table 0x00350FE0) takes THE ENGINE'S
   PLAYER (0x0034E948) every step, turns the carpet as he looks (0x0016AFE0 / 0x0016AEB8) and puts it at his place
   (0x0016C028, 0x0016ACE0). That is all that binds the carpet to a hero; it is not a paired move (run carp1);
 - the hero's side starts the carpet's motions with the pointer 0x00351068 at four places (0x00178E1C, 0x00178E34
   in the hero's command routine, 0x00178E94 in its end call, 0x001B2A04 in the riding state 10);
 - the game makes an object with 0x0016F000(object number, place, turn): the same routine the script call "make
   an object" uses.
gc_tick (the call at 0x00138538, each step of the field): when BOTH heroes are carpet riders (object 0x04FF) and
  the game's carpet is alive, a SECOND carpet is made once at player 2's hero (0x000E7E54; made for the carpet
  0x000E7E58; at most four tries for one carpet, 0x000E7E5C). 0x00351068 stays the first carpet.
gc_upd (the word at 0x00350FF8): the second carpet's state routine runs with player 2's hero as "the player".
gc_c1, gc_c2, gc_c3 (the four places): a carpet motion started by player 2's hero goes to the second carpet.

'''
s = s.replace(a, hdr + a)
b = " [--ship2hit]"
assert s.count(b) == 1
s = s.replace(b, b + " [--carpet2]")

i = s.index("def main():")
src = '''# ---- fifty-second glue, an experiment (only with --carpet2) ------------------------------------------------
GC_AT = 0x000EB400
GC_END = 0x000EB800
GC_SRC = """
gc_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gk_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,gk_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x04FF
    bne t2,t1,gk_go               # he is no carpet rider
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,gk_go               # player 1's hero is none
    lw t3,4200(t5)                # 0x00351068: the game's carpet
    beq t3,zero,gk_go
    nop
    lw t2,0(t3)
    lui t1,0x0035
    ori t1,t1,0x1078
    bne t2,t1,gk_go               # not a living carpet
    lui t7,0x000E
    lw t0,0x7E58(t7)              # the carpet the second one was made for
    bne t0,t3,gk_new              # another one (a new room): count anew
    lw t9,0x7E54(t7)              # the second carpet
    beq t9,zero,gk_make
    nop
    lw t2,0(t9)
    beq t2,t1,gk_go               # it is there and alive
    nop
    b gk_make
    nop
gk_new:
    sw zero,0x7E5C(t7)
gk_make:
    lw t2,0x7E5C(t7)
    sltiu t0,t2,4
    beq t0,zero,gk_go             # never more than four tries for one carpet
    addiu t2,t2,1
    sw t2,0x7E5C(t7)
    sw t3,0x7E58(t7)
    sw zero,0x7E54(t7)
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t3,8(sp)
    lw t2,0x70(t6)                # the twin's place
    sw t2,16(sp)
    lw t2,0x74(t6)
    sw t2,20(sp)
    lw t2,0x78(t6)
    sw t2,24(sp)
    lw t2,0x7C(t6)
    sw t2,28(sp)
    mtc1 zero,f12
    addiu a0,zero,0x0168          # the carpet's object number
    jal 0x0016F000                # the game's own "make an object"
    addiu a1,sp,16
    lui t7,0x000E
    sw v0,0x7E54(t7)
    ld t3,8(sp)
    lui t5,0x0035
    sw t3,4200(t5)                # the first carpet stays "the carpet" (the new one's constructor wrote itself there)
    ld ra,0(sp)
    addiu sp,sp,48
gk_go:
    j TICK_NEXT
    move a0,zero
gc_upd:                           # the word at 0x00350FF8 (was 0x001B2DB8): state 19's routine. a1 = the carpet
    lui t7,0x000E
    lw t6,0x7E54(t7)
    bne a1,t6,gu_go               # the game's own carpet: as the game
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,gu_go
    lui t5,0x0035
    addiu sp,sp,-32
    sd ra,0(sp)
    lw t4,-5816(t5)
    sd t4,8(sp)                   # the engine's player
    jal 0x001B2DB8
    sw t6,-5816(t5)               # for this one call "the player" is the twin
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
gu_go:
    j 0x001B2DB8
    nop
gc_c1:                            # from 0x00178E1C and 0x00178E34 (was lw a0,4200(s0)): s2 = the acting hero's motion part
    lw t6,8(s2)                   # its owner: the hero
gc_cx:
    lui t7,0x0035
    lw a0,4200(t7)                # the game's carpet
    lui t5,0x000F
    lw t5,0x05CC(t5)
    bne t6,t5,gx_out              # not the twin
    lui t7,0x000E
    lw t4,0x7E54(t7)
    beq t4,zero,gx_out
    nop
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1078
    bne t3,t2,gx_out              # not a living carpet
    nop
    move a0,t4                    # the twin's own carpet
gx_out:
    jr ra
    nop
gc_c3:                            # from 0x001B2A04 (was lw a0,4200(t7)): s1 = the hero
    b gc_cx
    move t6,s1
gc_c2:                            # from 0x00178E8C (was lui t7,0x35; the next but one instruction is lw a0,4200(t7)):
    lui t7,0x0035                 # a0 = the hero whose motion has ended. Out: t7 + 4200 = where his carpet's pointer is
    lui t5,0x000F
    lw t5,0x05CC(t5)
    bne a0,t5,g2_out              # not the twin
    lui t6,0x000E
    lw t4,0x7E54(t6)
    beq t4,zero,g2_out
    nop
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1078
    bne t3,t2,g2_out
    nop
    ori t7,t6,0x6DEC              # 0x000E7E54 - 4200
g2_out:
    jr ra
    nop
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--carpet2" in sys.argv:                                            # fifty-second glue, an experiment (a carpet under player 2's hero)
        tick_next = words[0x00138538]                                      # jal pad_both, or the glue that sits there already
        assert (tick_next >> 26) == 3
        labels, n = add_code(GC_AT, GC_END, GC_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second carpet, under player 2's hero")
        hook_base(0x00138538, tick_next, jal(labels["gc_tick"]), "the field's START look-out: first, is a second carpet wanted")
        hook_game(0x00350FF8, 0x001B2DB8, labels["gc_upd"], "the carpet's state routine: the second carpet follows player 2's hero")
        hook_game(0x00178E1C, 0x8E041068, jal(labels["gc_c1"]), "the hero's command starts a carpet motion: on his own carpet")
        hook_game(0x00178E34, 0x8E041068, jal(labels["gc_c1"]), "the same, second call")
        hook_game(0x00178E8C, 0x3C0F0035, jal(labels["gc_c2"]), "the end of that motion: his own carpet goes back to rest")
        hook_game(0x001B2A04, 0x8DE41068, jal(labels["gc_c3"]), "the riding state's motion: on his own carpet")
        n_glue += n + 5

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
