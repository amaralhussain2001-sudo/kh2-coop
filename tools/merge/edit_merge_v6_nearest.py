"""One-off: add the experiment --nearest to tools/merge/merge_v6.py ("the player" of an object's own thinking is
the hero nearer to that object). It takes the place of the --helper experiment (same hook, 0x0016A950)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "near_think" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--helper] [--react]
''', '''TWELFTH GLUE, AN EXPERIMENT (option --nearest; not with --helper, it uses the same hook): FOR AN OBJECT'S OWN
THINKING "THE PLAYER" IS THE HERO NEARER TO IT.
Idea: many things are written against "the player" in the object's own script (the moving bag of the Seven
Wonders offers its jump-on command after asking trap_sysobj_player; boss scripts take the player for their
scripted moves). Routine near_think (0x000F4E80, jump at the entry of 0x0016A950 "an object thinks: its script
and its action list"): for an object that is neither a hero nor a helper (class table 0x00345C08), while a twin
is there, if the twin is nearer to it than player 1's hero (flat distance, positions at object+0x70 / +0x78),
the engine's player pointer holds the twin for the length of that call. So that object's script, the commands
it offers and the moves it starts mean the nearer hero. Not sticky: the choice is made again at every step.

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--helper] [--react] [--nearest]
''')
rep('''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''', '''NEAR_AT = 0x000F4E80
NEAR_END = 0x000F4F00
NEAR_SRC = """
near_think:                       # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,nr_body
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nr_body
    nop
    beq a0,t4,nr_body             # the heroes think as themselves
    nop
    beq a0,t6,nr_body
    lw t3,0(a0)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nr_body             # a helper: unchanged
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
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
    bc1f nr_body                  # player 1's hero is nearer (or as near): as it is
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nr_body                   # the twin is nearer: this object thinks with him as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nr_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
"""

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''')
rep('''    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''',
    '''    if "--nearest" in sys.argv:        # EXPERIMENT
        assert "--helper" not in sys.argv, "--nearest and --helper use the same hook"
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(NEAR_AT, NEAR_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert NEAR_AT + 4 * len(code) <= NEAR_END, "nearest glue too long"
        for i, w in enumerate(code):
            a = NEAR_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (an object thinks with the nearer hero as the player)"
        a, w0, w1, _what = HELPER_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["near_think"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (nearest): an object thinks"
        origin[a + 4] = "glue hook (nearest): its delay slot"
        n_glue += len(code) + 2

    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''')
p.write_text(t, encoding="utf-8")
print("ok")
