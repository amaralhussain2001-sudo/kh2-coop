"""One-off: the forty-seventh glue's sender note gets a STEP STAMP (0x000E7C1C = the game's counter when the note
was written); the callback runner honours the note only in that same step. So a callback that never comes back
(a room change inside it) cannot leave a stale sender behind. The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_sender3.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "0x7C1C" in s:
    raise SystemExit("already there")
a = '''rc_send:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    jal 0x0016BAE8
    sw a1,0x7C18(t7)              # the sender, for the callback's "the player"
'''
assert s.count(a) == 1
s = s.replace(a, '''rc_send:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t2,-11076(t5)              # the game's counter: the note holds for this step only
    sw t2,0x7C1C(t7)
    jal 0x0016BAE8
    sw a1,0x7C18(t7)              # the sender, for the callback's "the player"
''')
a = '''    lw t3,0x7C18(t7)              # did a hero send this callback?
    beq t3,zero,ns_old
    lw t8,56(a0)                  # the object
'''
assert s.count(a) == 1
s = s.replace(a, '''    lw t3,0x7C18(t7)              # did a hero send this callback?
    beq t3,zero,ns_old
    lw t2,0x7C1C(t7)              # ... in this very step?
    lui t1,0x0035
    lw t1,-11076(t1)
    bne t2,t1,ns_old
    lw t8,56(a0)                  # the object
''')
a = "V_SENDER = 0x000E7C18                              # the hero whose command's callback is running (0 = none)"
assert s.count(a) == 1
s = s.replace(a, a + "\n#                                                    0x000E7C1C = the game's counter when that note was written")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
