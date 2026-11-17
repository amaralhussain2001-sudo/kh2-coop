"""One-off: tools/merge/merge_v7.py gets the FORTY-FIFTH GLUE (a script that asks for "the player" gets the hero
its object HOLDS, in every place a script can run). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_scriptplayer.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tp_player" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-FIFTH GLUE (option --no-scriptplayer leaves it out; it uses the hold memory of glues 36 / 39): A SCRIPT THAT
ASKS FOR "THE PLAYER" GETS THE HERO ITS OBJECT HOLDS, WHEREVER THE SCRIPT RUNS (job 10: Xigbar's sniper part,
Luxord's card trick; faults F10 / F11).
What was there (runs xig, xig2, xigdc, luxc of the eighth round): a boss's trick in several steps starts on the
twin (paired moves FC, FD, FF) and then never lets him go; in build 12 the same fights stop or hold him too. The
steps of such a trick are not all run from the boss's thinking (0x0016A950) or from a callback (0x0016CCE8), where
the glues 12 / 36 / 39 put the right hero into the engine's player pointer: scripts also run as their own threads
(trap_magic_start_thread) and from other runners (0x0016CD48 has eleven callers), and there the script call
trap_sysobj_player (0x00171068 -> 0x0016B0D0) answers "the engine's player" = player 1's hero.
Now the call inside that script routine (0x00171074) goes through tp_player: the game's answer first; then, while
there is a twin and the running script (0x0034D8A4) belongs to an object that is neither a hero nor a helper: the
hero that this object holds in a paired move now, or held less than 90 steps ago (the hold memory 0x000E7C0C),
is the answer. Nobody held: the game's answer stays (inside thinking and callbacks that is already the nearer
hero).

'''
s = s.replace(a, hdr + a)
b = "[--no-captureform]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-scriptplayer]")
i = s.index("def main():")
src = '''# ---- forty-fifth glue --------------------------------------------------------------------------------------
TP_AT = 0x000E92A0
TP_END = 0x000E9400
TP_SRC = """
tp_player:                        # from 0x00171074 (was jal 0x0016B0D0): a script asks for "the player"
    lui t5,0x0035
    lw v0,-5816(t5)               # the engine's player: the game's answer
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tp_out
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tp_out
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,tp_out
    nop
    lw t8,56(t8)                  # its object
    srl t3,t8,22
    addiu t3,t3,-6
    bne t3,zero,tp_out            # not an object
    nop
    beq t8,t4,tp_out              # a hero's own script: as it is
    nop
    beq t8,t6,tp_out
    lw t3,0(t8)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,tp_out              # a helper
    nop
    lw t9,0x140(t8)               # the first word of its motion part
    beq t9,zero,tp_out
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,tp_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,tp_ntw
    nop
tp_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,tp_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,tp_nh1
    nop
tp_mem:                           # nobody at this moment: whom did it hold a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,tp_out
    lw t2,-11076(t5)              # the game's counter
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,tp_out
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    bne t3,zero,tp_h1
    nop
tp_tw:
    jr ra
    move v0,t6
tp_h1:
    jr ra
    move v0,t4
tp_ntw:                           # the twin is held now: note it, he is the answer
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tp_tw
    sw t3,0x7C14(t7)
tp_nh1:                           # player 1's hero is held now
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tp_h1
    sw t3,0x7C14(t7)
tp_out:
    jr ra
    nop
"""
TP_HOOK = (0x00171074, 0x0C05AC34)                 # jal 0x0016B0D0


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-scriptplayer" not in sys.argv:                                # forty-fifth glue
        labels, n = add_code(TP_AT, TP_END, TP_SRC, {}, "a script that asks for the player gets the hero its object holds")
        a, w0 = TP_HOOK
        hook_game(a, w0, jal(labels["tp_player"]), "trap_sysobj_player: the hero the running script's object holds, else the game's answer")
        n_glue += n + 1

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
