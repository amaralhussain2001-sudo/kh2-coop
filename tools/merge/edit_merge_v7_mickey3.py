"""One-off: tools/merge/merge_v7.py, thirty-seventh glue, third version (after run mkH of the eighth round: the
Hydra's room, two Mickeys; the game stopped at the rescue's end with "pc 0x00179F10, address 0x7F8" = the game's
"put the hero back on his feet" called with NO hero).
Why: the rescue's end routine is called ONCE FOR EACH Mickey when the end comes through the paired move 253 (each
Mickey's own script calls it). The first call ends both Mickeys (mk_end); the second call then ran the game's
routine with an empty parking place. Now a call that finds the parking place empty does nothing but the "is the
twin still down" part.
Run once:  python -I tools/merge/edit_merge_v7_mickey3.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "this rescue was ended already" in s:
    raise SystemExit("already there")
old = '''me_one:
    jalr s3                       # one Mickey: the game's routine as it is
    move a0,s0
'''
assert s.count(old) == 1
s = s.replace(old, '''me_one:
    lui t5,0x0035
    lw t4,-5812(t5)               # the game's parking place
    beq t4,zero,me_fill           # nobody is parked: this rescue was ended already (the other Mickey's own call)
    nop
    jalr s3                       # one Mickey: the game's routine as it is
    move a0,s0
''')
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
