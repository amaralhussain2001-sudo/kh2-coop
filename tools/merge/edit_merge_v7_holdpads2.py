"""One-off: THE SIXTY-EIGHTH GLUE of tools/merge/merge_v7.py (--holdpads), second form (ninth round, job 3).
Seen in the runs xeJ / xeL / xeM (first form, candidate v114): the buttons of both controllers were one in a hold,
but player 1's stick still did not move Riku. Run xeM (tools/own/pads_probe2.py): the stick that MOVES a hero is
the four floats at record + 0x30 (x, y, 0, strength at + 0x3C); record + 0x20 is the other stick (the camera's).
The first form copied + 0x20. Now: the stick at + 0x30 of a record at rest takes the other record's; + 0x20 (the
cameras) stays apart.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdpads2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "the sticks that move a hero" in s:
    raise SystemExit("already there")

old = '''    lw t0,0x2C(t6)                # the left sticks' strengths
    lw t1,0x8C(t6)
    bne t0,zero,pm_l1
    nop
    ld t2,0x80(t6)                # controller 1's is at rest: it takes controller 2's
    ld t3,0x88(t6)
    sd t2,0x20(t6)
    b pm_ret
    sd t3,0x28(t6)
pm_l1:
    bne t1,zero,pm_ret
    nop
    ld t2,0x20(t6)                # controller 2's is at rest: it takes controller 1's
    ld t3,0x28(t6)
    sd t2,0x80(t6)
    b pm_ret
    sd t3,0x88(t6)
'''
assert s.count(old) == 1
s = s.replace(old, '''    lw t0,0x3C(t6)                # the sticks that move a hero (record + 0x30: x, y, 0, strength): their strengths
    lw t1,0x9C(t6)
    bne t0,zero,pm_l1
    nop
    ld t2,0x90(t6)                # controller 1's is at rest: it takes controller 2's
    ld t3,0x98(t6)
    sd t2,0x30(t6)
    b pm_ret
    sd t3,0x38(t6)
pm_l1:
    bne t1,zero,pm_ret
    nop
    ld t2,0x30(t6)                # controller 2's is at rest: it takes controller 1's
    ld t3,0x38(t6)
    sd t2,0x90(t6)
    b pm_ret
    sd t3,0x98(t6)
''')
old = '''records are made one after the game's update (buttons of either, without START; a left stick at rest takes the
other's); each record gets its own held word back before the next update.'''
assert s.count(old) == 1
s = s.replace(old, '''records are made one after the game's update (buttons of either, without START; a moving stick (record + 0x30) at
rest takes the other's; the camera sticks (+ 0x20) stay apart); each record gets its own held word back before
the next update.''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
