"""One-off edit of tools/merge/make_all.py: usage text, two symbols, glue section split into parts (for --v2)."""
import pathlib
import sys

p = pathlib.Path(sys.argv[1])
t = p.read_text()


def rep(old, new):
    global t
    assert t.count(old) == 1, "expected exactly one: " + old[:70]
    t = t.replace(old, new)


rep('''  python -I tools/merge/make_all.py [outDir] [--check] [--without NAME ...]

Default outDir: patches/merged-v1. Writes SLPM-66675_F266B00B.pnach and listing.txt (every word with its meaning).
--check     also compares the unchanged routines word-for-word with the source lanes' delivered patch files.
--without   leave a section out (names: base, identity, exits, ownhp). 'glue' goes with identity + ownhp.
''', '''  python -I tools/merge/make_all.py [outDir] [--v2] [--check] [--without NAME ...] [--keep-base]

Default outDir: patches/merged-v1 (with --v2: patches/merged-v2). Writes SLPM-66675_F266B00B.pnach and listing.txt
(every word with its meaning).
--v2        merged build 2 = build 1 + SECTION commands (lane G) - SECTION base (no longer needed with lane G;
            --keep-base keeps it) + two more glue routines (see GLUE).
--check     also compares the unchanged routines word-for-word with the source lanes' delivered patch files.
--without   leave a section out (names: base, identity, exits, ownhp, commands). 'glue' goes with identity + ownhp.
''')
rep('''  SECTION glue      this lane: makes lane D's "who gets the fresh slot" follow lane E's roles instead of the
                    build order.                                       cave 0x000F0C00-0x000F0CBF, var 0x000F0DF0
''', '''  SECTION commands  (--v2) lane G: the hero on controller 2 gets its own control object S2 (command menu state,
                    cursor, shortcut mode, command request, lock-on). Routines unchanged at lane G's addresses
                    0x000F0800-0x000F0AD3; S2's data is 0x000F1000-0x000F1AFF (reserved, must be zero at boot).
  SECTION glue      this lane: makes lane D's "who gets the fresh slot" follow lane E's roles instead of the
                    build order; with --v2 it also moves a twin that was built first onto S2 and releases S2 when
                    a twin goes away.                                  cave 0x000F0C00-0x000F0DEF, var 0x000F0DF0
''')
rep('''    "ABIL_END": 0x001C3060,       # original tail call of LOAD_STATS
''', '''    "ABIL_END": 0x001C3060,       # original tail call of LOAD_STATS
    "CO_DETACH": 0x001D69D0,      # release a control object from its hero (also clears party slot 0)
    "PARTY_SET": 0x0013DDC0,      # party table: slot a0 = object a1 (slot 0 = HUD owner)
''')

a = t.index('GLUE_AT = 0x000F0C00')
b = t.index('def jal(t):')
old_glue = t[a:b]
# cut the old single text into its three routines
i_wrap = old_glue.index('m_wrap:')
i_slot = old_glue.index('m_slot:')
head = old_glue[:old_glue.index('GLUE_SRC = """')]
getpad = old_glue[old_glue.index('m_getpad:'):i_wrap].rstrip() + "\n"
wrap1 = old_glue[i_wrap:i_slot].rstrip() + "\n"
slot = old_glue[i_slot:old_glue.rindex('"""')].rstrip() + "\n"

wrap2 = '''m_wrap:                           # hook 0x0016F0F4 (was: jal 0x00179FD0; lane E hooked the same word)
    addiu sp,sp,-32
    sd ra,0(sp)
    jal e_wrap                    # lane E: call the factory, then apply the identity rule
    nop
    lui t7,%hi(V_BUILD)
    sw zero,%lo(V_BUILD)(t7)      # the factory is done
    lui t5,%hi(V_ISP1)
    lw t6,%lo(V_ISP1)(t5)
    beq t6,zero,m_w_out           # a twin was built after the hero: lane E already attached the hero again
    lw t4,%lo(V_OLD)(t5)
    beq t4,zero,m_w_out           # the hero is the first player object of the room
    nop
    beq t4,v0,m_w_out
    nop
    sd v0,8(sp)                   # v0 = player 1's hero, t4 = the earlier object, now the twin on controller 2
    jal ATTACH                    # attach the twin again: lane G's attach gives it S2
    move a0,t4
    jal ATTACH                    # then the hero again: camera target, trigger owner, HUD owner and S are its
    ld a0,8(sp)
    ld v0,8(sp)
m_w_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
'''
dtor = '''m_dtor:                           # hook 0x00178294 (was: jal 0x001781E8; lane E hooked the same word). a0 = dying object
    lui t5,%hi(V_TWIN)
    lw t4,%lo(V_TWIN)(t5)
    bne t4,a0,m_dt_go             # not the twin: lane E's routine decides
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    beq t6,zero,m_dt_go           # no engine player left: lane E does the game's full detach (releases S2 too)
    nop
    beq t6,a0,m_dt_go
    nop
    lw t3,0xB3C(a0)               # the twin's control object
    beq t3,zero,m_dt_go
    lui t2,0x01C6
    addiu t2,t2,-2768             # S
    beq t3,t2,m_dt_go             # the twin still uses S: nothing of its own to release
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd t6,16(sp)
    jal CO_DETACH                 # release the twin's own control object, as the game does for S
    move a0,t3
    ld a1,16(sp)
    jal PARTY_SET                 # party slot 0 (HUD owner) back to player 1's hero
    move a0,zero
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
m_dt_go:
    j e_dtor                      # lane E's rule (keeps the hero registered, clears the twin's pointers)
    nop
'''
notes = '''# --v2 only. With lane G a hero's control object is chosen when it ATTACHES, by its controller at that moment. A
# twin that was built first attached as "controller 1" (to S) and only became the twin, on controller 2, when the
# hero arrived. So in that case m_wrap attaches the twin once more (lane G then gives it S2) and then the hero once
# more, so that camera target, trigger owner, HUD owner and S end on the hero.
# Lane E lets a twin die without the game's detach so that player 1's hero stays registered. With lane G the twin
# owns a control object (S2) that has to be released: m_dtor does it with the game's routine, which also clears
# party slot 0 (the HUD owner), so that is given back to the hero.
'''
new_glue = (head + 'GLUE_GETPAD = """\n' + getpad + '"""\nGLUE_WRAP_V1 = """\n' + wrap1 + '"""\nGLUE_SLOT = """\n' + slot +
            '"""\n' + notes + 'GLUE_WRAP_V2 = """\n' + wrap2 + '"""\nGLUE_DTOR = """\n' + dtor + '"""\n\n\n')
t = t[:a] + new_glue + t[b:]
p.write_text(t)
print("glue split into GLUE_GETPAD, GLUE_WRAP_V1, GLUE_SLOT, GLUE_WRAP_V2, GLUE_DTOR")
