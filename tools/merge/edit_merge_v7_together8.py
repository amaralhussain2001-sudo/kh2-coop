"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue), EIGHTH form: two more rules for
"who makes a pair" (th_new), so that only a move a boss FORCES on a hero takes the other hero along:
 (1) the object whose script hooks must be an object that is neither a hero nor a helper (a Limit that hooks a
     script onto a hero is the heroes' own business);
 (2) a NEW pair is not made when the hook is the answer to a hero's own Reaction Command (the forty-seventh glue
     notes the sender for the length of the callback): a hero's own command never pulls the other hero in. Inside
     a living pair the answers (Shan-Yu's push and takedown) are copied as before.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together8.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "tn_far" in s:
    raise SystemExit("already there")
old = '''    bne t2,zero,tn_out            # a hero's own hooked script hooks: each hero's script does that for itself
    nop
'''
new = old + '''    ld t2,8(sp)
    lw t9,56(t2)                  # the object whose script hooks
    srl t2,t9,22
    addiu t2,t2,-6
    bne t2,zero,tn_out            # not an object
    nop
    beq t9,t4,tn_out              # a hero's or a helper's own script (a Limit ...): as the game
    nop
    beq t9,t6,tn_out
    lw t2,0(t9)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,tn_out
    nop
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
old = '''tn_first:
    or t1,t1,t0
    bne t1,zero,tn_out            # no pair yet, and he is busy in something else
    nop
'''
new = old + '''    lw t2,0x7C18(t7)              # the forty-seventh glue's note: is this the answer to a hero's command?
    beq t2,zero,tn_far
    lw t2,0x7C1C(t7)
    lw t1,-11076(t5)
    beq t2,t1,tn_out              # yes: a hero's own command never pulls the other hero in
    nop
tn_far:
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
