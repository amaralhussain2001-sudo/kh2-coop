"""One-off: tools/merge/merge_v7.py gets the THIRTY-EIGHTH GLUE (the command of a boss's paired move goes to the
hero who is held in it). The record of the edit; run once:  python -I tools/merge/edit_merge_v7_reactheld.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "ro2:" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''THIRTY-EIGHTH GLUE (option --no-reactheld leaves it out): THE COMMAND OF A BOSS'S PAIRED MOVE GOES TO THE HERO WHO
IS HELD IN IT (plan row 9, first step, second half).
What was there (run gp5, candidate v39, pictures p1_f017000 / p2_f017000): with the thirty-sixth glue Shan-Yu's
clash takes PLAYER 2'S hero when he is the one who fights, but the command "Press" still sits in PLAYER 1'S menu.
It is offered by a frame trigger of the BOSS'S motion: routine 0x00189E18(source object, command, argument) gives
it to the control object of the engine's player. The fifteenth glue (react_own, hook 0x00189E3C) hands the twin in
only when the twin himself is the source.
Now the hook goes to ro2: the twin is "the player" of that one offer when he is the source (as before) OR when he
is held in a paired move by the source (twin + 0x240 = the source, bit 0x4000 of + 0x160). Everything else: as it
was.

'''
s = s.replace(a, hdr + a)
b = "[--no-mickey | --mickey1]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-reactheld]")
i = s.index("def main():")
src = '''# ---- thirty-eighth glue ------------------------------------------------------------------------------------
RH_AT = 0x000E8800
RH_END = 0x000E8860
RH_SRC = """
ro2:                              # hook 0x00189E3C (was the fifteenth glue's jal react_own). s1 = the object whose
    lui t7,0x0035                 # motion offers the command. Out: s0 = "the player" of this offer
    lw s0,-5816(t7)               # the engine's player (the instruction that sat at 0x00189E40)
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,r2_out
    nop
    beq s1,t6,r2_twin             # the twin's own motion offers it (fifteenth glue)
    nop
    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,s1,r2_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,r2_out
    nop
r2_twin:
    move s0,t6
r2_out:
    jr ra
    nop
"""
RH_BASE_WORD = (0x00189E3C, 0x0C03D6E0)            # the base patch: jal react_own (0x000F5B80)


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\\n    head = ["
c = c.replace("\\n", "\n")
assert s.count(c) == 1
step = '''    if "--no-reactheld" not in sys.argv:                                   # thirty-eighth glue
        labels, n = add_code(RH_AT, RH_END, RH_SRC, {}, "the command of a paired move goes to the hero who is held in it")
        a, w0 = RH_BASE_WORD
        hook_base(a, w0, jal(labels["ro2"]), "a motion offers a command: the twin when he is the source or is held by the source")
        n_glue += n

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
