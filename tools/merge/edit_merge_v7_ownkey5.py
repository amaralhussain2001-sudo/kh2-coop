"""One-off: the SIXTY-THIRD GLUE of tools/merge/merge_v7.py (--ownkey), fifth form (ninth round, part 91).
Seen in run kdB (candidate v101: a save, a Game Over and "Continue" with two different Keyblades): after the
Continue the twin holds player 1's Keyblade, although the files of his own are loaded. Why: kb_fix tries once
for each twin OBJECT and Keyblade, and the twin's new body stood at the same address as the old one.
Now kb_fact forgets that note whenever a player object is built.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey5.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "a new body: kb_fix may try again" in s:
    raise SystemExit("already there")
a = '''    lui t7,0x000E
    addiu t6,zero,1
    jal 0x00179FD0
    sw t6,0x7E88(t7)              # a player object is being built
'''
assert s.count(a) == 1
b = '''    lui t7,0x000E
    addiu t6,zero,1
    sw zero,0x7E90(t7)            # a new body: kb_fix may try again
    jal 0x00179FD0
    sw t6,0x7E88(t7)              # a player object is being built
'''
s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
