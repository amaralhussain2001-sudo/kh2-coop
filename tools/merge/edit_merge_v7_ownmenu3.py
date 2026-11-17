"""One-off: plan row 39 stage 1a, three safety points for the glues 48 / 49 (after the runs om3, om4, om5):
 (1) only a HERO's slot (status id 1 = Sora, 14 = Roxas, as lane D's D6 tells them) gets player 2's places; any
     other body of the twin (King Mickey ...) reads a plain copy of its record;
 (2) the record whose places change places for player 2's menu is the HERO's record (0x000E7E28, noted when a
     hero's slot of the twin loads), not "the last record the twin read";
 (3) the flag "player 2's menu is open" is cleared when a save file is loaded into the save data (the copy at
     0x00240B84) and when the save data are made new (0x00105770): after a soft reset it cannot stay set.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownmenu3.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "or_load" in s:
    raise SystemExit("already there")


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)


rep('''    lw t3,0x7E24(t5)              # player 2's menu is open: the places have changed places in the source already
    bne t3,zero,tl_use
    nop
''', '''    lw t3,0x254(a0)               # whose slot: only a hero (1 = Sora, 14 = Roxas) has places of player 2's
    addiu t2,zero,1
    beq t3,t2,tl_hero
    addiu t2,zero,14
    bne t3,t2,tl_use              # another body (King Mickey ...): the plain copy
    nop
tl_hero:
    sw a1,0x7E28(t5)              # the hero's record: the one the pause menu edits
    lw t3,0x7E24(t5)              # player 2's menu is open: the places have changed places in the source already
    bne t3,zero,tl_use
    nop
''')
rep('''    lw t4,0x7E20(t5)              # the record the twin's view shows (Sora's, Roxas's ...)
    beq t4,zero,os_out''', '''    lw t4,0x7E28(t5)              # the hero's record (Sora's, Roxas's)
    beq t4,zero,os_out''')
rep('''    lw t2,0x7E20(t3)
    beq t2,zero,mo_go             # the twin has no view yet''', '''    lw t2,0x7E28(t3)
    beq t2,zero,mo_go             # no hero record noted yet''')
rep('''ms_go:
    j 0x000F4740                  # the second glue's pad_both
    move a0,zero
"""''', '''ms_go:
    j 0x000F4740                  # the second glue's pad_both
    move a0,zero
or_load:                          # from 0x00240B84 (was j 0x002FDD68): a save file is copied into the save data
    lui t7,0x000E
    j 0x002FDD68
    sw zero,0x7E24(t7)            # nobody's menu is open
or_new:                           # from 0x00105770 (was jal 0x002FD310): the save data are made new
    lui t7,0x000E
    j 0x002FD310
    sw zero,0x7E24(t7)
"""
RM_LOAD = (0x00240B84, 0x080BF75A)                 # j 0x002FDD68
RM_NEW = (0x00105770, 0x0C0BF4C4)                  # jal 0x002FD310''')
rep('''        hook_base(a, w0, jal(labels["ms_tick"]), "the field looks for START: first, has player 2's menu gone? (then the second glue's pad_both)")
        n_glue += n + 1
''', '''        hook_base(a, w0, jal(labels["ms_tick"]), "the field looks for START: first, has player 2's menu gone? (then the second glue's pad_both)")
        a, w0 = RM_LOAD
        hook_game(a, w0, (2 << 26) | ((labels["or_load"] >> 2) & 0x3FFFFFF), "a save file goes into the save data: the menu flag is cleared")
        a, w0 = RM_NEW
        hook_game(a, w0, jal(labels["or_new"]), "the save data are made new: the menu flag is cleared")
        n_glue += n + 3
''')
rep('''The slot's pointer (slot + 0x244) is set to T. Everything else is common: Keyblade, abilities, item places.
''', '''The slot's pointer (slot + 0x244) is set to T. Everything else is common: Keyblade, abilities, item places.
Only a HERO's slot (status id 1 = Sora, 14 = Roxas) gets player 2's places; any other body of the twin (King
Mickey) reads a plain copy. The hero's record is noted at 0x000E7E28 for the forty-ninth glue.
''')
rep('''The bag is common: both players equip from the same stock.
''', '''The bag is common: both players equip from the same stock.
The flag is also cleared when a save file is copied into the save data (0x00240B84) and when the save data are
made new (0x00105770), so it cannot stay set over a reset.
''')
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
