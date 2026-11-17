"""One-off: tools/merge/merge_v7.py gets the FORTY-SIXTH GLUE (a script's "the player" is the hero its object holds,
held a moment ago, or THE NEARER HERO, in every place a script runs; Luxord's card / die takes the same hero).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_playernear.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tp_player2" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-SIXTH GLUE (option --no-playernear leaves it out; it needs the forty-fifth and replaces its routine):
A SCRIPT'S "THE PLAYER" IS THE SAME HERO IN EVERY PLACE THE SCRIPT RUNS (job 10, faults F10 / F11).
What was there (runs x1, x2, x3 of chain 40, recorder at the paired-move call): with ONE hero Xigbar's sniper part
makes ONE capture (move 0xFC at counter 4988) and ends by itself. With two heroes there are TWO captures in the
same step, one for each hero, then 0xFD and an endless row of 0xFF every 84 steps on the twin, and the part never
ends, with the forty-fifth glue too. The first capture's stack shows where the script's own thread runs: object
update 0x00178C84 -> 0x0016BB28 -> 0x0016CB54 -> 0x0016CC9C -> the runner 0x0016CD48. In that path the engine's
player is player 1's hero, while in the object's thinking (0x0016A950, twelfth glue) it is the NEARER hero. So one
script saw two different "players" in one step and held both.
Now tp_player2 answers trap_sysobj_player for an object that is neither a hero nor a helper: the hero this
object holds in a paired move now; else the hero it held less than 90 steps ago; else THE NEARER HERO by the
twelfth glue's own rule (a hero who is down does not count; as near = player 1's hero). The same answer in the
thread path, in callbacks and in thinking.
And cf_who2 (the call at 0x001741EC, forty-fourth glue): Luxord's "turn the hero into a card / a die" asks the
same routine, so both halves of his trick take the same hero (run lux5: with the forty-fourth glue alone the
first trick still held player 2's hero while player 1's hero was the die).

'''
s = s.replace(a, hdr + a)
b = "[--no-scriptplayer]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-playernear]")
i = s.index("def main():")
src = '''# ---- forty-sixth glue --------------------------------------------------------------------------------------
TQ_AT = 0x000E9400
TQ_END = 0x000E9600
TQ_SRC = """
tp_player2:                       # from 0x00171074 (was jal 0x0016B0D0): a script asks for "the player"
    lui t5,0x0035
    lw v0,-5816(t5)               # the engine's player: the game's answer
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tq_out
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tq_out
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,tq_out
    nop
    lw t8,56(t8)                  # its object
    srl t3,t8,22
    addiu t3,t3,-6
    bne t3,zero,tq_out            # not an object
    nop
    beq t8,t4,tq_out              # a hero's own script: as it is
    nop
    beq t8,t6,tq_out
    lw t3,0(t8)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,tq_out              # a helper
    nop
    lw t9,0x140(t8)               # the first word of its motion part
    beq t9,zero,tq_out
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,tq_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,tq_ntw
    nop
tq_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,tq_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,tq_nh1
    nop
tq_mem:                           # nobody at this moment: whom did it hold a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,tq_near
    lw t2,-11076(t5)              # the game's counter
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,tq_near
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    bne t3,zero,tq_h1
    nop
tq_tw:
    jr ra
    move v0,t6
tq_h1:
    jr ra
    move v0,t4
tq_ntw:                           # the twin is held now: note it, he is the answer
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tq_tw
    sw t3,0x7C14(t7)
tq_nh1:                           # player 1's hero is held now
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tq_h1
    sw t3,0x7C14(t7)
tq_near:                          # nobody held, nobody remembered: THE NEARER HERO (the twelfth glue's rule)
    lw t3,0x48C(t6)               # the twin's unit slot
    beq t3,zero,tq_h1
    nop
    lw t3,0(t3)
    beq t3,zero,tq_h1             # the twin is down: player 1's hero
    nop
    lw t2,0x48C(t4)
    beq t2,zero,tq_dist
    nop
    lw t2,0(t2)
    beq t2,zero,tq_tw             # player 1's hero is down: the twin
    nop
tq_dist:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t4)
    lwc1 f3,0x78(t4)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # distance to player 1's hero, squared
    lwc1 f4,0x70(t6)
    lwc1 f5,0x78(t6)
    sub.s f4,f4,f0
    sub.s f5,f5,f1
    mul.s f4,f4,f4
    mul.s f5,f5,f5
    add.s f4,f4,f5                # distance to the twin, squared
    c.lt.s f4,f2
    bc1f tq_h1                    # player 1's hero is nearer (or as near)
    nop
    b tq_tw
    nop
tq_out:
    jr ra
    nop
cf_who2:                          # from 0x001741EC (was jal 0x001D14A0): which hero is turned into the card / the die
    addiu sp,sp,-16
    sd ra,0(sp)
    jal tp_player2                # the same answer as the script's "the player"
    nop
    ld ra,0(sp)
    bne v0,zero,cq_ret
    addiu sp,sp,16
    lui t5,0x0035
    lw v0,0x2400(t5)              # nobody: the game's own answer
cq_ret:
    jr ra
    nop
"""


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-playernear" not in sys.argv and "--no-scriptplayer" not in sys.argv:      # forty-sixth glue
        labels, n = add_code(TQ_AT, TQ_END, TQ_SRC, {}, "a script's player: the held hero, else the nearer hero, in every runner")
        hook_base(TP_HOOK[0], jal(TP_AT), jal(labels["tp_player2"]), "trap_sysobj_player: held, held a moment ago, else the NEARER hero")
        if "--no-captureform" not in sys.argv:
            hook_base(0x001741EC, jal(CF_AT), jal(labels["cf_who2"]), "trap_player_capture_form: the same hero as the script's player")
        n_glue += n

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
