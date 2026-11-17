"""One-off: tools/merge/merge_v7.py gets the FORTY-SEVENTH GLUE (a hero's Reaction Command: HE is "the player" of
the callback it sends, and an object that holds one hero does not take the other hero's command), and the
forty-sixth glue becomes an experiment that is only built on request (--playernear).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_sender.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "rc_one" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-SEVENTH GLUE (option --no-sender leaves it out): THE HERO WHO PRESSES A REACTION COMMAND IS "THE PLAYER"
OF THE CALLBACK IT SENDS, AND AN OBJECT THAT HOLDS ONE HERO DOES NOT TAKE THE OTHER HERO'S COMMAND (job 10: Xigbar's
sniper part, Luxord's card trick, the stray calls of Shan-Yu's clash; faults F10 / F11).
What was there (chain 46, the recorder at the paired-move routine with the stack of calls 1 to 4): Xigbar's two
captures at counter 4988 both come from THE SAME PLACE: a hero's update runs his command (0x00178C7C: record at
hero + 0xB44, kind 0 = a Reaction Command) and calls function 11 of the SOURCE object's script through 0x0016BAE8
(source, hero, ...) -> the callback runner 0x0016CCE8. The script then pulls THE HERO IT WAS GIVEN into the move.
Both test players press Triangle in the same frame, so both heroes sent "Warp Snipe" and one boss held two
heroes; his script is written for one and never found its end. (With ONE hero the same press gives one capture
and the part ends: run x1.) And the thirty-sixth glue ran such a callback with "the player" = the held or the
NEARER hero, not the hero who sent it: one of the two captures ran with the twin as the player while player 1's
hero was the one pulled in. Luxord's trick is the same split (the grab takes the sender, the card / die took "the
player"). The forty-sixth glue (the nearer hero in every runner) did not change either fight (runs x9, lux9); it
is now built only with --playernear.
Now:
(1) rc_one (the call at 0x00178C7C): when the source is an object that is neither a hero nor a helper and it
    HOLDS THE OTHER HERO in a paired move at this moment, this hero's command does nothing. Otherwise the callback
    is sent, and the sender is noted (0x000E7C18) while it runs.
(2) ns_pre (the jump at 0x0016CCE8 comes here first): while a sender is noted and the callback's script belongs
    to such an object, the callback runs with THE SENDER as "the player" (the twin: the engine's player is the
    twin for that call; player 1's hero: as the game). No sender: the thirty-sixth glue's nc_trig as before.

'''
s = s.replace(a, hdr + a)
b = "[--no-playernear]"
assert s.count(b) == 1
s = s.replace(b, "[--playernear] [--no-sender]")
c = 'FORTY-SIXTH GLUE (option --no-playernear leaves it out; it needs the forty-fifth and replaces its routine):'
assert s.count(c) == 1
s = s.replace(c, 'FORTY-SIXTH GLUE (AN EXPERIMENT THAT DID NOT HELP; built only with the option --playernear; it needs the\nforty-fifth and replaces its routine):')
d = '    if "--no-playernear" not in sys.argv and "--no-scriptplayer" not in sys.argv:      # forty-sixth glue'
assert s.count(d) == 1
s = s.replace(d, '    if "--playernear" in sys.argv and "--no-scriptplayer" not in sys.argv:             # forty-sixth glue (experiment)')
i = s.index("def main():")
src = '''# ---- forty-seventh glue ------------------------------------------------------------------------------------
RC_AT = 0x000E9600
RC_END = 0x000E9800
V_SENDER = 0x000E7C18                              # the hero whose command's callback is running (0 = none)
RC_SRC = """
rc_one:                           # from 0x00178C7C (was jal 0x0016BAE8): a hero's command calls back its source object
    lui t7,0x000F                 # a0 = the source object, a1 = the hero
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,rc_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,rc_go
    nop
    beq a1,t6,rc_o                # the twin sends: the other hero is player 1's
    move t3,t4
    bne a1,t4,rc_go               # the sender is no hero: as the game
    move t3,t6
rc_o:
    beq a0,zero,rc_go
    srl t2,a0,22
    addiu t2,t2,-6
    bne t2,zero,rc_go             # the source is not an object
    nop
    beq a0,t4,rc_go               # the source is a hero or a helper (Limits, the heroes' own commands): as the game
    nop
    beq a0,t6,rc_go
    lw t2,0(a0)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,rc_go
    nop
    lw t9,0x140(a0)               # the first word of the source's motion part
    beq t9,zero,rc_send
    nop
    lw t2,0x240(t3)               # does the source hold the OTHER hero in a paired move?
    bne t2,t9,rc_send
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    beq t2,zero,rc_send
    nop
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
rc_send:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    jal 0x0016BAE8
    sw a1,0x7C18(t7)              # the sender, for the callback's "the player"
    lui t7,0x000E
    sw zero,0x7C18(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
rc_go:
    j 0x0016BAE8
    nop
ns_pre:                           # the jump at 0x0016CCE8 comes here first. a0 = the script, its object at +56
    lui t7,0x000E
    lw t3,0x7C18(t7)              # did a hero send this callback?
    beq t3,zero,ns_old
    lw t8,56(a0)                  # the object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,ns_old            # not an object
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,ns_old
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t8,t4,ns_old              # a hero's or a helper's own script: the thirty-sixth glue decides
    nop
    beq t8,t6,ns_old
    lw t2,0(t8)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,ns_old
    nop
    bne t3,t6,ns_body             # player 1's hero sent it: he is the engine's player already
    nop
    lw t4,-5816(t5)               # the twin sent it: this callback runs with the twin as "the player"
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal ns_body
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
ns_body:
    addiu sp,sp,-48               # the two instructions that sat at 0x0016CCE8
    j 0x0016CCF0
    sd s0,0(sp)
ns_old:
    j 0x%08X                      # the thirty-sixth glue's nc_trig
    nop
""" % NC_AT
RC_HOOK = (0x00178C7C, 0x0C05AEBA)                 # jal 0x0016BAE8


'''
s = s[:i] + src + s[i:]
e = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(e) == 1
step = '''    if "--no-sender" not in sys.argv and "--no-nearcb" not in sys.argv:    # forty-seventh glue (it sits on the thirty-sixth)
        labels, n = add_code(RC_AT, RC_END, RC_SRC, {}, "a hero's Reaction Command: the sender is the player; one object holds one hero")
        a, w0 = RC_HOOK
        hook_game(a, w0, jal(labels["rc_one"]), "a hero's command calls back its source: not while the source holds the other hero; the sender is noted")
        hook_base(NC_HOOK[0], (2 << 26) | ((NC_AT >> 2) & 0x3FFFFFF), (2 << 26) | ((labels["ns_pre"] >> 2) & 0x3FFFFFF),
                  "a callback: first the sender rule (ns_pre), then the thirty-sixth glue")
        n_glue += n + 1

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
