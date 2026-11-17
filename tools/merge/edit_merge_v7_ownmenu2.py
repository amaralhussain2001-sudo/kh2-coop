"""One-off: the forty-ninth glue's ms_tick no longer asks 0x00103428(0). Run om1 showed that the list it reads
(0x00369D98) is a fixed table (0 is always in it), so "player 2's menu has gone" was never seen and the places
stayed changed. The field's START look-out (0x00138538) is only reached when no menu is open (its three guards
before it: 0x00103B38, the word + 0xFC of 0x0014ABA8(), 0x002EE530), so reaching it with the flag set IS the
signal. The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownmenu2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
a = '''    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00103428                # is the main menu's module (0) still there?
    move a0,zero
    bne v0,zero,ms_keep
    nop
    jal ow_swap                   # gone: the places change back
    nop
    lui t3,0x000E
    jal ow_load
    sw zero,0x7E24(t3)
ms_keep:
    ld ra,0(sp)
    addiu sp,sp,16
'''
assert s.count(a) == 1, s.count(a)
s = s.replace(a, '''    addiu sp,sp,-16               # the field looks for START again, so the menu has gone (or never came):
    sd ra,0(sp)
    jal ow_swap                   # the places change back
    nop
    lui t3,0x000E
    jal ow_load
    sw zero,0x7E24(t3)
    ld ra,0(sp)
    addiu sp,sp,16
''')
a = ''' ms_tick (the call at 0x00138538, each step the field looks for START): when the flag is set and the main menu's
   module (0, asked with 0x00103428) is gone, the places change back, the flag is cleared and player 1's slot
   loads its stats again (and with it the twin's).'''
assert s.count(a) == 1
s = s.replace(a, ''' ms_tick (the call at 0x00138538, each step the field looks for START; it is not reached while a menu is open):
   when the flag is set the places change back, the flag is cleared and player 1's slot loads its stats again
   (and with it the twin's).''')
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
