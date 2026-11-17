"""One-off: tools/merge/merge_v7.py, thirty-fifth glue, SECOND VERSION (after runs tf3 / tfpm of the eighth round).
The first version let the game mark the form files "may be thrown out" and then asked for the other hero's form
again. That does not keep the files in use: a form's WEAPON files are asked for with the keep-number 5002, and for
that number the game's request (0x00170400) makes a NEW entry when it finds the name under another number, so the
entry the other hero's Keyblade object really uses stays marked and is thrown out (run tfpm: the motion resource
of player 1's Keyblade W_EX010 is destroyed, class table 0x00347B88, and his Valor body's update calls into it).
Second version: the game's call 0x00170320(5000) is simply NOT MADE while the other hero is in a Drive Form (at
the form task) or while any hero is in one (at King Mickey's file request). The next form change with nobody else
in a form makes it as before.
Run once:  python -I tools/merge/edit_merge_v7_formfiles2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "fk_form" in s:
    raise SystemExit("already there")
a = s.index('FK_SRC = """')
b = s.index("FK_HOOKS = (")
c = s.index(")\n", s.index("FK_HOOKS = (")) + 2
new_src = '''FK_SRC = """
fk_form:                          # from 0x001B66F8 (was jal 0x00170320; a0 = 5000 from the delay slot). s2 = the form
    lui t5,0x000F                 # record: its first word is the body that changes
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fk_do             # one hero: as the game
    nop
    lw t6,0(s2)
    bne t6,t4,fk_twin             # player 1's hero changes: is the twin in a form?
    nop
    lui t7,0x0033
    b fk_ask
    lbu t6,-4012(t7)              # the twin changes: player 1's form (the save's byte 0x0032F054)
fk_twin:
    lbu t6,0x47E8(t5)             # the twin's own form (ninth glue)
fk_ask:
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fk_do             # the other hero is in no form: the game's call
    nop
    jr ra                         # he is: his files stay as they are
    nop
fk_mickey:                        # from 0x001D0080 (King Mickey's files are asked for)
    lui t5,0x000F
    lw t4,0x05CC(t5)
    beq t4,zero,fk_do
    nop
    lbu t6,0x47E8(t5)             # the twin's form
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fk_skip
    lui t7,0x0033
    lbu t6,-4012(t7)              # player 1's form
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fk_do
    nop
fk_skip:
    jr ra
    nop
fk_do:
    j 0x00170320                  # the game's call: the files kept for forms may now be thrown out
    nop
"""
FK_HOOKS = (
    (0x001B66F8, 0x0C05C0C8, "fk_form", "the form task lets the form files go: not while the other hero is in a form"),
    (0x001D0080, 0x0C05C0C8, "fk_mickey", "King Mickey's files are asked for: the form files stay while a hero is in a form"),
)
'''
s = s[:a] + new_src + s[c:]
old = '''        for a, w0, what in FK_HOOKS:
            hook_game(a, w0, jal(labels["fk_keep"]), what)
'''
assert s.count(old) == 1
s = s.replace(old, '''        for a, w0, label, what in FK_HOOKS:
            hook_game(a, w0, jal(labels[label]), what)
''')
old = '''Now both calls go through fk_keep: the game's call first, then, while there is a twin, the files of player 1's
form (the save's byte 0x0032F054) and of the twin's form (his own byte 0x000F47E8) are asked for again with the
game's own request 0x0016EF28(form), which gives a loaded file its keep-number back. With one hero: as the game.
'''
assert s.count(old) == 1
s = s.replace(old, '''Now (second version, after runs tf3 / tfpm: asking for the files again made NEW entries and did not keep the ones in
use) the game's call is simply NOT MADE while the other hero is in a Drive Form (fk_form, at the form task) or
while any hero is in one (fk_mickey, at King Mickey's file request). With one hero: as the game.
''')
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
