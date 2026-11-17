"""One-off: the FIFTY-EIGHTH GLUE of tools/merge/merge_v7.py (--ownabil), second form, after the runs ab7 / ab8
(candidate v90, eighth round part 80): the game's "give an ability" put Once More into the hero's list and player
2's switch followed, BUT THE TWIN'S VIEW T KEPT THE OLD LIST until his next stat load (T is a copy). Player 1's
hero reads his list live; the twin must not come later.
Now ab_add also writes the new place into T when T shows this record.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownabil2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "aa_nt:" in s:
    raise SystemExit("already there")
old = '''    bne t2,zero,aa_out
    lui t8,0x0033
    lhu t1,@MARK@(t8)
    addiu t2,zero,0x5032
    bne t1,t2,aa_out              # his switches are not made yet: they will be made from the hero's
'''
new = '''    bne t2,zero,aa_out
    lw t1,0x7E20(t5)              # the record the twin's view T shows
    bne t1,t0,aa_nt
    ori t1,t5,0x7D00              # T
    sll t3,t6,1
    addu t1,t1,t3
    sh t7,0x54(t1)                # the view has the new ability at once, with the switch the game gave
aa_nt:
    lui t8,0x0033
    lhu t1,@MARK@(t8)
    addiu t2,zero,0x5032
    bne t1,t2,aa_out              # his switches are not made yet: they will be made from the hero's
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
a = "GA_END = 0x000EBF00"
assert s.count(a) == 1
s = s.replace(a, "GA_END = 0x000EBF40")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
