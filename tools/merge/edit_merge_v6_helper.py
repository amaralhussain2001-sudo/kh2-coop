"""One-off: add the tenth glue to tools/merge/merge_v6.py (the second helper goes with the second hero)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "HELPER_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--react]
''', '''TENTH GLUE: THE SECOND HELPER GOES WITH THE SECOND HERO.
What was there (lane H, and again test l2-mu68-base: both helpers 350-950 units from player 1's hero and
1,600-2,800 from the twin): Donald, Goofy and the guests follow and help the engine's player only; their code
reads that pointer in many places. The user's rule: one helper each.
Now: the helpers' class (class table 0x00345C08) gets its update method (+0x0C, 0x0017DC98) through routine
helper_upd (0x000F4E80): for the helper in party place 2, while a twin is there, the engine's player pointer
holds the twin for the length of that helper's update. So everything that helper asks about "the player" in his
own update (where to go, whom to help) means the second hero. The helper in party place 1 and every other
object: unchanged.

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-helper] [--react]
''')
rep('''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''', '''HELPER_AT = 0x000F4E80
HELPER_END = 0x000F4F00
HELPER_SRC = """
helper_upd:                       # the helpers' update method (class table 0x00345C08 + 0x0C). a0 = the helper
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,hu_plain
    lui t5,0x0035
    lw t4,-31168(t5)              # 0x00348640: the party table's place 2 (the second helper)
    bne a0,t4,hu_plain
    nop
    lw t4,-5816(t5)               # the engine's player
    beq t4,zero,hu_plain
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal 0x0017DC98                # his update, with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
hu_plain:
    j 0x0017DC98
    nop
"""
HELPER_WORD = (0x00345C14, 0x0017DC98, "the helpers' class table: update method through helper_upd")

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''')
rep('''    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''',
    '''    if "--no-helper" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(HELPER_AT, HELPER_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HELPER_AT + 4 * len(code) <= HELPER_END, "helper glue too long"
        for i, w in enumerate(code):
            a = HELPER_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second helper goes with the second hero)"
        a, orig, what = HELPER_WORD
        assert a not in words, "address already used: %08X" % a
        assert struct.unpack_from("<I", elf.data, off + a - va)[0] == orig, "class table word is not the update method"
        words[a] = labels["helper_upd"]
        order.append(a)
        origin[a] = "glue hook (helpers): " + what
        n_glue += len(code) + 1

    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''')
p.write_text(t, encoding="utf-8")
print("ok")
