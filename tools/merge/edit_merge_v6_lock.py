"""One-off: add the fifth glue to tools/merge/merge_v6.py (the twin's attack uses the twin's own lock-on target)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "LOCK_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize]
''', '''FIFTH GLUE: THE SECOND HERO'S ATTACK USES HIS OWN LOCK-ON TARGET.
What was there (VERIFIED, tests g1-grand-base, g3-grand-near, g4-grand-twinplayer, g5-plbit0..6): in the
Grandstander job player 2's swings never reached the ball's script as hits (its hit and landing counters stayed 0
and the job stalled); with the engine's player pointer set to the twin they did. A bit-coded search over the 119
loads of that pointer found the one place: routine 0x001874A0 (called from the attack motion's event handler at
0x0018958C for a hero, flag 2 at object+0x588). It asks whether the attacking hero is at, or within a distance
of, the target in the lock-on manager of THE ENGINE'S PLAYER (object+0xB40). Now, when the attacker is the twin,
the twin's own lock-on manager is used (hook 0x001874BC, routine lock_own at 0x000F48C0).
NOT changed: the sister routine 0x00187420 (called from 0x00189AB8; the search showed no effect on the ball).

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock]
''')
rep('''
HOOKS = (''', '''
LOCK_AT = 0x000F48C0
LOCK_END = 0x000F4900
LOCK_SRC = """
lock_own:                         # hook 0x001874BC (j). The instruction at 0x001874C0 runs in its delay slot, so
    lui t6,0x000F                 # s0 = the engine's player here. a0 = the attacking hero
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    bne a0,t6,lo_go
    daddu s1,a0,zero              # the instruction that sat at 0x001874BC
    daddu s0,a0,zero              # the twin attacks: his own lock-on manager (object+0xB40)
lo_go:
    j 0x001874C4
    nop
"""
LOCK_HOOK = (0x001874BC, 0x0080882D, "an attacking hero's target test: the twin's own lock-on manager for the twin")

HOOKS = (''')
rep('''    out.mkdir(parents=True, exist_ok=True)
    head = [''', '''    if "--no-lock" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(LOCK_AT, LOCK_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert LOCK_AT + 4 * len(code) <= LOCK_END, "lock glue too long"
        for i, w in enumerate(code):
            a = LOCK_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's attack uses his own lock-on target)"
        a, orig, what = LOCK_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DF0E948), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["lock_own"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (lock-on): " + what
        n_glue += len(code) + 1

    out.mkdir(parents=True, exist_ok=True)
    head = [''')
p.write_text(t, encoding="utf-8")
print("ok")
