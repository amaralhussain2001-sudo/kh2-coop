"""One-off: add the eighth glue to tools/merge/merge_v6.py (mission-gauge prizes are taken by either hero)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "GPRIZE_SRC" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--react]
''', '''EIGHTH GLUE: PRIZES THAT FILL A MISSION GAUGE ARE TAKEN BY EITHER HERO.
What was there (read 2026-11-11; the "second pickup routine" of the notes): routine 0x001A5990(prize, gauge
number, amount), the step routine of two prize classes (called from 0x001C7EA8 and 0x001D29A0, amount from the
tables 0x0036E030 / 0x0036E3C8). When THE ENGINE'S PLAYER reaches the prize (0x001C7950) it is collected
(0x001C79A0) and the amount goes into the mission's gauge (0x001D8D08). The twin was never asked, so player 2
could not collect such prizes (HYPOTHESIS for which missions use them: the morale orbs of the Land of Dragons
missions, script trap_obj_scatter_prize_mu, are the likely ones).
Now (jump at the routine's entry 0x001A5990, routine gprize at 0x000F4B00): both heroes are asked; every other
prize (bit 6 of its address, like the fourth glue) asks the twin first.

  python -I tools/merge/merge_v6.py [outDir] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--react]
''')
rep('''REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''', '''GPRIZE_AT = 0x000F4B00
GPRIZE_END = 0x000F4C00
GPRIZE_SRC = """
gprize:                           # jump at 0x001A5990 (the slot holds nop). a0 = the prize, a1 = the gauge's
    addiu sp,sp,-64               # number, f12 = the amount
    swc1 f20,48(sp)
    sd s0,0(sp)
    sd s1,8(sp)
    sd s2,16(sp)
    sd ra,24(sp)
    sd s3,32(sp)
    mov.s f20,f12
    move s1,a0
    move s2,a1
    lui t7,0x0035
    lw s0,-5816(t7)               # the engine's player
    lui t7,0x000F
    lw s3,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq s3,zero,gp_first
    andi t6,s1,0x40
    beq t6,zero,gp_first          # every other prize asks the twin first
    nop
    move t6,s0
    move s0,s3
    move s3,t6
gp_first:
    jal gp_one
    nop
    bne v0,zero,gp_got
    nop
    beq s3,zero,gp_out
    move s0,s3
    jal gp_one
    nop
    beq v0,zero,gp_out
    nop
gp_got:
    mov.s f12,f20
    move a0,s2
    ld s0,0(sp)
    ld s1,8(sp)
    ld s2,16(sp)
    ld ra,24(sp)
    ld s3,32(sp)
    lwc1 f20,48(sp)
    j 0x001D8D08                  # the amount goes into the mission's gauge
    addiu sp,sp,64
gp_out:
    ld s0,0(sp)
    ld s1,8(sp)
    ld s2,16(sp)
    ld ra,24(sp)
    ld s3,32(sp)
    lwc1 f20,48(sp)
    jr ra
    addiu sp,sp,64
gp_one:                           # s0 = a hero, s1 = the prize. v0 = 1 when he took it (the routine's own steps)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x0019BA60
    move a0,s0
    beq v0,zero,go_out
    nop
    lw t7,40(s1)
    andi t7,t7,0x1
    beq t7,zero,go_no
    mtc1 zero,f12
    move a0,s1
    move a1,s0
    jal 0x001C7950                # in reach?
    mov.s f13,f12
    beq v0,zero,go_out
    nop
    move a0,s1
    move a1,s0
    jal 0x001C79A0                # collected by this hero
    move a2,zero
    li v0,1
go_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
go_no:
    b go_out
    move v0,zero
"""
GPRIZE_HOOK = (0x001A5990, 0x27BDFFD0, "a prize that fills a mission gauge: either hero takes it")

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00''')
rep('''    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''',
    '''    if "--no-gprize" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(GPRIZE_AT, GPRIZE_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert GPRIZE_AT + 4 * len(code) <= GPRIZE_END, "gauge-prize glue too long"
        for i, w in enumerate(code):
            a = GPRIZE_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (prizes that fill a mission gauge: either hero)"
        a, orig, what = GPRIZE_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x3C0F0035), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["gprize"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (gauge prizes): " + what
        origin[a + 4] = "glue hook (gauge prizes): its delay slot"
        n_glue += len(code) + 2

    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)''')
p.write_text(t, encoding="utf-8")
print("ok")
