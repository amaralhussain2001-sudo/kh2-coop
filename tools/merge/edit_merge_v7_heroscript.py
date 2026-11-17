"""One-off: tools/merge/merge_v7.py gets the FORTY-THIRD GLUE (the script that a paired move attaches to the TWIN
runs with the twin as "the player"). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_heroscript.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hs_tick" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-THIRD GLUE (option --no-heroscript leaves it out): THE SCRIPT THAT A PAIRED MOVE ATTACHES TO THE TWIN RUNS
WITH THE TWIN AS "THE PLAYER" (plan row 9, first step: the prompt in the right menu).
What was there (runs gp8 / gp9 and of270, the recorder at "offer a command"): in Shan-Yu's clash player 2's hero
is held, his Triangle presses count, but the prompt "Press" (command 270) sits in PLAYER 1'S menu. The first
offer's stack: the hero's own update (0x00178934 -> 0x00177510) runs the script attached to him for the move
(hero + 0xAEC) with 0x0016CD48, and that script calls the script routine 0x00174328, which offers the command to
the control object of the engine's player. That is player 1's hero, whoever the script is attached to.
Now the call at 0x00177510 goes through hs_tick: when the hero is the twin, the engine's player pointer holds the
twin for the length of that one call. Player 1's hero, or no twin: as the game.

'''
s = s.replace(a, hdr + a)
b = "[--no-helperback]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-heroscript]")
i = s.index("def main():")
src = '''# ---- forty-third glue --------------------------------------------------------------------------------------
HS_AT = 0x000E8E00
HS_END = 0x000E8E60
HS_SRC = """
hs_tick:                          # from 0x00177510 (was jal 0x0016CD48). s0 = the hero, a0 = the script attached to him
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne s0,t6,hs_plain            # player 1's hero (or no twin): as it is
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq t4,t6,hs_plain
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal 0x0016CD48                # the twin's attached script runs with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
hs_plain:
    j 0x0016CD48
    nop
"""
HS_HOOK = (0x00177510, 0x0C05B352)                 # jal 0x0016CD48


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-heroscript" not in sys.argv:                                  # forty-third glue
        labels, n = add_code(HS_AT, HS_END, HS_SRC, {}, "the script a paired move attaches to the twin runs with the twin as the player")
        a, w0 = HS_HOOK
        hook_game(a, w0, jal(labels["hs_tick"]), "a hero's attached script runs: the twin's with the twin as the player")
        n_glue += n + 1

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
