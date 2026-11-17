"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue), SEVENTH form, after the runs
tg16, tg17, tg18 (candidate v69: the second hero stands 70 units beside the first and pushes the same way; in sync,
0 fault lines). In the clash camera's picture, which looks from the side, the two heroes then stand one before the
other and one hides the other. Now the second hero is put 55 units to the side AND 55 units behind the first
(behind = away from the boss), so both are in the picture.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together7.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "55 units behind" in s:
    raise SystemExit("already there")
old = '''    lui t2,0x428C                 # 70.0
    mtc1 t2,f6
    mul.s f2,f1,f6
    mul.s f3,f0,f6
    lwc1 f4,0x70(t8)
    lwc1 f5,0x78(t8)
    add.s f4,f4,f2                # x: the first hero's + 70 * his direction's z
    sub.s f5,f5,f3                # z: the first hero's - 70 * his direction's x
'''
new = '''    lui t2,0x425C                 # 55.0: 55 units to the side and 55 units behind the first hero
    mtc1 t2,f6
    sub.s f2,f1,f0
    add.s f3,f0,f1
    mul.s f2,f2,f6
    mul.s f3,f3,f6
    lwc1 f4,0x70(t8)
    lwc1 f5,0x78(t8)
    add.s f4,f4,f2                # x: the first hero's + 55 * (his direction's z - x)
    sub.s f5,f5,f3                # z: the first hero's - 55 * (his direction's x + z)
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
