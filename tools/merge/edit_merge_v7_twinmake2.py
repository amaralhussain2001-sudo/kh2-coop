"""One-off: the FIFTY-SIXTH GLUE of tools/merge/merge_v7.py (--twinmake), second form, after the run one3 (candidate
v85): the second hero was made in the carpet escape and on the sidecar, but NOT at the toy cannon ("P2 none").
Why: gw_tick asked that the engine's player be the last-built hero of the main player class (0x00352400); the toy
cannon is a class of its own (constructor 0x001CF698) and never stands there.
Now gw_tick takes the engine's player (0x0034E948) alone.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_twinmake2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
old = '''    bne t6,zero,wk_go             # there is one
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,wk_go
    lw t3,-5816(t5)               # the engine's player
    bne t3,t4,wk_go
    nop
    lw t2,8(t4)
'''
new = '''    bne t6,zero,wk_go             # there is one
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player (the toy cannon is no hero of the main class: 0x00352400 is not asked)
    beq t4,zero,wk_go
    nop
    lw t2,8(t4)
'''
if new in s:
    raise SystemExit("already there")
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
