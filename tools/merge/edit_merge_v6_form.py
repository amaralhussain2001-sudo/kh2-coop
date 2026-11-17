"""One-off: add the ninth glue to tools/merge/merge_v6.py (the second hero's Drive Form change keeps him the twin)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "FORM_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--react]
''', '''NINTH GLUE: THE SECOND HERO CAN CHANGE HIS FORM (DRIVE) AND STAYS THE SECOND HERO.
What was there (VERIFIED, tests i7-drive-p2 and j2-drive-p1, roam disc with a Drive kit): player 1's Drive
(Limit Form) works: new body, own menu "Limit / Revert", two views stay. Player 2's Drive broke the game's
two-player state: after the change both screens showed ONE view of the new body. Reason (lane E's note, now
seen): a form change builds the new body directly with the constructor (jal 0x001D0980 at 0x001B6850, inside the
form-change routine; the old body is [s2]), not through the player factory, so none of the merged build's role
rules ran: the new body became the engine's player (camera, exits, HUD owner), shared PLAYER 1'S unit slot, and
when the old body ended the twin pointer was cleared.
Now (hook at that call, routine form_wrap at 0x000F4C40): when the old body is the twin
 - the search for "Sora's unit slot" finds the twin's own marked slot instead of player 1's (flag V_FT, read by
   form_d2, which replaces lane D's D2 at 0x001A1518: normally a marked slot is never found, during the twin's
   form change only the marked one is), so his HP, MP and Drive values go with him (the game's own write-back and
   load, through lane D's and the first glue's hooks);
 - after the constructor the new body is the twin (lane E's pointer), and the engine's player, the last-built
   pointer and the game's attach (camera target, trigger owner, HUD owner, control object S) are player 1's hero's
   again, exactly as lane E's rule does after the factory.
Player 1's form change and one hero alone: unchanged (the constructor is called as before).

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--react]
''')
rep('''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''', '''FORM_AT = 0x000F4C40
FORM_END = 0x000F4D00
V_FT = 0x000F47C8                 # 1 while the twin's new body is being built (a form change)
FORM_SRC = """
form_wrap:                        # hook 0x001B6850 (was: jal 0x001D0980, the player constructor; the instruction
    lw t6,0(s2)                   # after it has run). s2 = the form-change record, [s2] = the old body, s1 = the
    lui t7,0x000F                 # new body's memory. The constructor's arguments (a0-a3, t0, f12) stay untouched
    lw t5,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    bne t6,t5,fw_plain
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    li t6,1
    sw t6,%lo(V_FT)(t7)           # (V_FT is in the same 64 KB block as the twin pointer)
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    jal 0x001D0980
    sd t4,8(sp)
    lui t7,0x000F
    sw zero,%lo(V_FT)(t7)
    sw s1,0x05CC(t7)              # the new body is the twin
    ld t4,8(sp)
    lui t5,0x0035
    beq t4,zero,fw_done           # (no engine player before: nothing to give back)
    nop
    sw t4,-5816(t5)               # the engine's player is player 1's hero again
    sw t4,0x2400(t5)              # 0x00352400: the last-built object of the main player class
    lw t3,0x48C(t4)
    beq t3,zero,fw_att
    nop
    sw t4,0x25C(t3)               # his unit slot's back pointer
fw_att:
    jal 0x001781A8                # the game's attach for player 1's hero: camera target, trigger owner, HUD owner, S
    move a0,t4
fw_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
fw_plain:
    j 0x001D0980
    nop
form_d2:                          # replaces lane D's D2 (hook 0x001A1518, the find-slot-by-id loop). s0 = slot,
    bne t7,s1,fd_next             # s1 = wanted id, t7 = the slot's id
    lw t6,0x250(s0)
    lui t5,0x000F
    lw t5,%lo(V_FT)(t5)
    srl t6,t6,31                  # 1 = a marked slot (the twin's)
    bne t6,t5,fd_next             # normally only an unmarked slot is found; for the twin's new body only his
    nop
    j 0x001A1520                  # found
    nop
fd_next:
    j 0x001A14C4                  # loop head
    nop
"""
FORM_HOOK = (0x001B6850, 0x0C074260, "a form change builds the new body: the twin stays the twin")
FORM_D2 = (0x001A1518, 0x0803C057, "the slot search (lane D's D2): during the twin's form change his own slot is found")

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''')
rep('''    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''',
    '''    if "--no-form" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert FORM_AT + 4 * len(code) <= FORM_END, "form glue too long"
        for i, w in enumerate(code):
            a = FORM_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's form change)"
        a, orig, what = FORM_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DE70B38), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["form_wrap"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        a, old, what = FORM_D2
        assert words.get(a) == old, "lane D's D2 hook is not where it was: %08X" % words.get(a, 0)
        words[a] = (2 << 26) | ((labels["form_d2"] >> 2) & 0x3FFFFFF)
        origin[a] = "glue hook (form change; was lane D's D2): " + what
        n_glue += len(code) + 1

    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''')
p.write_text(t, encoding="utf-8")
print("ok")
