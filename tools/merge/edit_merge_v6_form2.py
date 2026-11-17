"""One-off: ninth glue of tools/merge/merge_v6.py, second version: the old body's end method runs BEFORE the new
body is built and lane E's rule clears the twin pointer there, so "the twin is changing" is noted at that call."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "form_end" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''Now (hook at that call, routine form_wrap at 0x000F4C40): when the old body is the twin
''', '''The old body's end method (jalr at 0x001B6810, class method +0x20) runs first; there the merged build's rule for
a twin that ends releases his control object and clears the twin pointer. So "the old body is the twin" is noted
at that call (routine form_end, flag V_FT2) and used at the constructor call.
Now (hook at the constructor call, routine form_wrap at 0x000F4C40): when the old body was the twin
''')
rep(''' - after the constructor the new body is the twin (lane E's pointer), and the engine's player, the last-built
''', ''' - the new body's slot is marked if it is not (the twin's slot had gone: stats loaded once more, as lane D does);
 - after the constructor the new body is the twin (lane E's pointer), and the engine's player, the last-built
''')
a = t.index('V_FT = 0x000F47C8')
b = t.index('FORM_HOOK = (0x001B6850')
t = t[:a] + '''V_FT = 0x000F47C8                 # 1 while the twin's new body is being built (a form change)
V_FT2 = 0x000F47CC                # 1 from the old body's end to the constructor call, when the old body is the twin
FORM_SRC = """
form_end:                         # hook 0x001B6810 (was: jalr t7, the old body's end method). a0 = the old body
    lui t5,0x000F
    lw t4,0x05CC(t5)              # the twin (lane E's pointer, 0 = none)
    xor t4,t4,a0
    sltiu t4,t4,1                 # 1 = the old body is the twin
    jr t7                         # the end method; it returns into the form-change routine
    sw t4,%lo(V_FT2)(t5)
form_wrap:                        # hook 0x001B6850 (was: jal 0x001D0980, the player constructor; the instruction
    lui t7,0x000F                 # after it has run). s1 = the new body's memory. The constructor's arguments
    lw t6,%lo(V_FT2)(t7)          # (a0-a3, t0, f12) stay untouched
    beq t6,zero,fw_plain
    sw zero,%lo(V_FT2)(t7)
    addiu sp,sp,-32
    sd ra,0(sp)
    li t6,1
    sw t6,%lo(V_FT)(t7)           # the slot search finds the twin's own slot now (form_d2)
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    jal 0x001D0980
    sd t4,8(sp)
    lui t7,0x000F
    sw zero,%lo(V_FT)(t7)
    sw s1,0x05CC(t7)              # the new body is the twin
    lw t3,0x48C(s1)               # his unit slot
    beq t3,zero,fw_role
    nop
    lw t2,0x250(t3)
    bltz t2,fw_role               # marked: it is his own slot, as before the change
    lui t1,0x8000
    or t2,t2,t1
    sw t2,0x250(t3)               # (his old slot was gone: this one becomes the marked one,
    move a0,t3
    jal 0x001A11E0                # and its stats are loaded once more as a marked slot: own HP / MP bytes)
    move a1,zero
fw_role:
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
FORM_END_HOOK = (0x001B6810, 0x01E0F809, "the old body's end method in a form change: note whether it is the twin")
''' + t[b:]
rep('''        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT})''',
    '''        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT, "V_FT2": V_FT2})''')
rep('''        a, old, what = FORM_D2
''', '''        a, orig, what = FORM_END_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["form_end"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        n_glue += 1
        a, old, what = FORM_D2
''')
p.write_text(t, encoding="utf-8")
print("ok")
