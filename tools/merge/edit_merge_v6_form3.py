"""One-off: ninth glue of tools/merge/merge_v6.py, third version: variables moved (the first place overlapped the
first glue's 12 remembered bytes), the form-change record takes the changing hero's own slot, the second hero has
his own form number."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "form_build" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


rep('''Player 1's form change and one hero alone: unchanged (the constructor is called as before).
''', '''Player 1's form change and one hero alone: unchanged (the constructor is called as before).
Three more things belong to it (found with the frame-by-frame probe tools/own/drv_probe2.py, test k3-drvtrace):
 - THE RECORD'S SLOT. A form change is run by a record (0x20 bytes, pointer 0x00351184; made by 0x001B60E0 /
   0x001B6298). For a real form it asks for "Sora's slot" by id (jal 0x001A1658 at 0x001B6148 / 0x001B6300) and
   the form's gauge and clock are started on THAT slot (0x001B6AB8 -> 0x001A1CC0). That was player 1's slot: the
   twin's new body had no clock and changed back at once, and player 1's gauge showed a form. Now, when the body
   that changes is the twin, that search finds his own slot (routine form_slot, same flag V_FT).
 - THE FORM NUMBER. The game keeps ONE current form (save data 0x0032F054). A request for the form that is
   current is ignored (0x001B6B10), the number is written there on a request (0x001B6BB0) and cleared when a form
   ends (0x001B6C84), and a new room builds the player in it (0x0016F0D0). The second hero now has his own number
   (V_TFORM): asked for him in the request (form_cur), written for him (form_set, form_zero), and used for the
   first-built hero of a room (form_build), who becomes the second hero when player 1's hero is built after him
   (lane E's rule). The save data's number stays player 1's. "First-built = second hero" is used only after two
   heroes have been built in one room once (V_TFV); a hero alone always takes the save data's number.
 - Not changed: the other readers of the save data's number (0x0016E9C0, 0x0016EECC, 0x00198064, 0x001B6C44,
   0x00256110) mean player 1's hero's form.
''')
a = t.index('V_FT = 0x000F47C8')
b = t.index('FORM_END_HOOK = (0x001B6810')
t = t[:a] + '''V_FT = 0x000F47E0                 # 1 while a slot search must find the twin's own (marked) slot
V_FT2 = 0x000F47E4                # 1 from the old body's end to the constructor call, when the old body is the twin
V_TFORM = 0x000F47E8              # the second hero's own current form number (a byte; 0 = none)
V_TFV = 0x000F47EC                # 1 once two heroes have been built in one room
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
    bne t6,t5,fd_next             # normally only an unmarked slot is found; for the twin only his
    nop
    j 0x001A1520                  # found
    nop
fd_next:
    j 0x001A14C4                  # loop head
    nop
form_slot:                        # hooks 0x001B6148 and 0x001B6300 (were: jal 0x001A1658, "Sora's slot" for the
    lw t6,0(s0)                   # form-change record). s0 = the record, [s0] = the body that changes
    lui t7,0x000F
    lw t5,0x05CC(t7)
    bne t6,t5,fsl_plain
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    li t6,1
    jal 0x001A1658
    sw t6,%lo(V_FT)(t7)           # the twin changes: the record holds his own slot
    lui t7,0x000F
    sw zero,%lo(V_FT)(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
fsl_plain:
    j 0x001A1658
    nop
form_cur:                         # hook 0x001B6B30 (the next word is now a nop): "is the wanted form the current
    lui t7,0x0033                 # one?" s1 = the hero that asks. Out: t6 = his current form number
    lbu t6,-4012(t7)              # the save data's number: player 1's hero
    lui t5,0x000F
    lw t4,0x05CC(t5)
    bne s1,t4,fc_out
    nop
    lbu t6,%lo(V_TFORM)(t5)       # the twin: his own
fc_out:
    jr ra
    nop
form_set:                         # hook 0x001B6BAC (the word that sat there runs in the slot after it): the new
    lui t5,0x000F                 # form number is noted. s1 = the hero, s0 = the number
    lw t4,0x05CC(t5)
    beq s1,t4,fst_tw
    lui t6,0x0033
    jr ra
    sb s0,-4012(t6)               # player 1's hero: the save data, as before
fst_tw:
    jr ra
    sb s0,%lo(V_TFORM)(t5)
form_zero:                        # hook 0x001B6C78 (0x001B6C84 is now a nop): a hero's form ends. s0 = the hero.
    lui t5,0x000F                 # Keeps a0
    lw t4,0x05CC(t5)
    beq s0,t4,fz_tw
    lui t7,0x0033
    jr ra
    sb zero,-4012(t7)
fz_tw:
    jr ra
    sb zero,%lo(V_TFORM)(t5)
form_build:                       # hook 0x0016F0CC (0x0016F0D0 is now a nop): a room builds a player object from
    lui t7,0x0033                 # the PLAYER placeholder. Out: s0 = the form number to build it in
    lbu s0,-4012(t7)
    lui t6,0x0035
    lw t6,-5816(t6)               # the engine's player
    lui t5,0x000F
    beq t6,zero,fb_first
    li t4,1
    jr ra
    sw t4,%lo(V_TFV)(t5)          # a second hero is built in this room: this game has two
fb_first:
    lw t4,%lo(V_TFV)(t5)
    beq t4,zero,fb_out
    nop
    lbu s0,%lo(V_TFORM)(t5)       # the first-built hero becomes the second hero: his own form
fb_out:
    jr ra
    nop
"""
FORM_MORE = (                     # (address, word expected, word after it expected, routine, kind, what)
    (0x001B6148, 0x0C068596, 0x2405FFFF, "form_slot", "jal", "the form-change record asks for Sora's slot (first maker)"),
    (0x001B6300, 0x0C068596, 0x2405FFFF, "form_slot", "jal", "the form-change record asks for Sora's slot (second maker)"),
    (0x001B6B30, 0x3C0F0033, 0x91EEF054, "form_cur", "jal+nop", "a form is asked for: compared with the asking hero's own form"),
    (0x001B6BAC, 0xAE2F0108, 0xA1D03524, "form_set", "jal+move", "the new form number is noted: the twin's in his own place"),
    (0x001B6C78, 0x3C0F0033, 0x24040020, "form_zero", "jal", "a form ends: the twin's own number is cleared"),
    (0x0016F0CC, 0x3C0F0033, 0x91F0F054, "form_build", "jal+nop", "a room builds a player object: in that hero's own form"),
)
FORM_NOP = (0x001B6C84, 0xA1E0F054, "(the save data's number was cleared here; form_zero does it)")
''' + t[b:]
rep('''        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT, "V_FT2": V_FT2})''',
    '''        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT, "V_FT2": V_FT2, "V_TFORM": V_TFORM, "V_TFV": V_TFV})''')
rep('''        a, old, what = FORM_D2
''', '''        for a, w0, w1, routine, kind, what in FORM_MORE:
            assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<2I", elf.data, off + a - va)
            assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
            words[a] = (3 << 26) | ((labels[routine] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (form change): " + what
            n_glue += 1
            if kind == "jal+nop":
                words[a + 4] = 0
            elif kind == "jal+move":
                words[a + 4] = w0
            if kind != "jal":
                order.append(a + 4)
                origin[a + 4] = "glue hook (form change): the slot after it"
                n_glue += 1
        a, orig, what = FORM_NOP
        assert a not in words, "hook address already used: %08X" % a
        assert struct.unpack_from("<I", elf.data, off + a - va)[0] == orig
        words[a] = 0
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        n_glue += 1
        a, old, what = FORM_D2
''')
t = t.replace("FORM_END = 0x000F4D40", "FORM_END = 0x000F4E80")
p.write_text(t, encoding="utf-8")
print("ok")
