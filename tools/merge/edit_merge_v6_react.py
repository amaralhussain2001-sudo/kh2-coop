"""One-off: add the sixth glue to tools/merge/merge_v6.py (the twin's action registers with the twin's own
control object)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "REACT_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock]
''', '''SIXTH GLUE: THE SECOND HERO'S ACTION REGISTERS WITH HIS OWN CONTROL OBJECT.
What was there (lane S1 row TTR-10; VERIFIED again, tests h1-dusk-p1 / h1-dusk-p2): in the Old Mansion fight
where the Dusk cannot be damaged, the story goes on after player 1's attacks (scene by frame 8900) and never
after player 2's. The same bit-coded search (tests h2-plbit0..6: the scene came in variants 0, 3 and 4 = index 25)
found routine 0x00189E18(acting object, command, argument): for a hero (flag 0x80 at +0x588) with flag 0x4000 at
+0x160 it builds a target record and, ONLY IF the acting object is the engine's player, hands the command to
that player's control object (0x001BD418 with object+0xB44); any other hero goes a side way (0x00189EE8).
Now the twin counts as "the player" of this routine (hook 0x00189E3C, routine react_own at 0x000F48E0), so his
command goes to his own control object (lane G's S2).

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-react]
''')
rep('''
HOOKS = (''', '''
REACT_AT = 0x000F48E0
REACT_END = 0x000F4900
REACT_SRC = """
react_own:                        # hook 0x00189E3C (j). The load at 0x00189E40 runs in its delay slot, so s0 = the
    lui t6,0x000F                 # engine's player here. s1 = the acting object
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    bne s1,t6,ro_go
    daddu s3,a1,zero              # the instruction that sat at 0x00189E3C
    daddu s0,s1,zero              # the twin acts: he is "the player" here (his own control object, object+0xB44)
ro_go:
    j 0x00189E44
    nop
"""
REACT_HOOK = (0x00189E3C, 0x00A0982D, "a hero's action is handed to a control object: the twin's own for the twin")

HOOKS = (''')
rep('''    out.mkdir(parents=True, exist_ok=True)
    head = [''', '''    if "--no-react" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(REACT_AT, REACT_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert REACT_AT + 4 * len(code) <= REACT_END, "react glue too long"
        for i, w in enumerate(code):
            a = REACT_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's action registers with his own control object)"
        a, orig, what = REACT_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DF0E948), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["react_own"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (control object): " + what
        n_glue += len(code) + 1

    out.mkdir(parents=True, exist_ok=True)
    head = [''')
p.write_text(t, encoding="utf-8")
print("ok")
