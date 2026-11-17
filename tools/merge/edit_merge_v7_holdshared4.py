"""One-off: THE SIXTY-FIFTH GLUE'S FIFTH FORM, THIRD PART (option --holdshared): THE LASER DOME IS NEVER "A HERO'S OWN MOVE"
(ninth round, the user's item 4 of 2026-11-15 evening; STATE part 110).
SEEN (run xsK on candidate v123, both players pressing): player 1 pressed one of the boss's green commands at counter 6728
(FC / FD, his own move, ended about 6770); the boss's laser dome took him at 6830 (move 0x106, sender none) while his "own
move" note (0x000E7EC4, forgotten only 45 idle steps after such a move) was still set. hp_form read that as "the victim is in
a move he started with his own command: it is his alone" and made no pair: player 2 stayed outside the whole dome.
NOW (only with --holdshared): at hp_form's hf_h a jump goes to hs_hf (the first routine of the co_two room, 0x000EE4C0):
when the move is 0x106 and the captor is the object 0x081F or 0x09CA (the shared mechanic), both "own move" notes (t8 /
t0) count as empty for this decision; then back to hf_h2 (the old test). Every other capture is decided as before.
Two words more in glue 65's range (its code with --holdshared ended at 0x000ED914, now 0x000ED91C; the range ends at
0x000ED920).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared4.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hs_hf" in s:
    raise SystemExit("already there")

a = """each player's own press counts (once a step, the forty-seventh glue's hp_rc).
"""
assert s.count(a) == 1
s = s.replace(a, a + """Its third part: the dome is never "a hero's own move": for that capture alone the own-move notes do not stop the pair
(hs_hf, the first routine of co_two's room; run xsK: the dome came 60 steps after player 1's own green command).
""")

a = '''CO_SRC = """
co_two:'''
assert s.count(a) == 1
s = s.replace(a, '''CO_SRC = """
hs_hf:                            # (--holdshared) from hp_form's hf_h (MUST stay the first routine: hp_form jumps to CO_AT)
    addiu t1,zero,0x106           # the shared mechanic (the laser dome) is never a hero's own move
    bne a3,t1,hs_back
    srl t2,a1,22
    addiu t2,t2,-6
    bne t2,zero,hs_back           # the captor is not an object
    nop
    lw t2,8(a1)                   # its object entry
    beq t2,zero,hs_back
    nop
    lw t2,0(t2)                   # its object number
    addiu t1,zero,0x081F
    beq t2,t1,hs_sh
    addiu t1,zero,0x09CA
    bne t2,t1,hs_back
    nop
hs_sh:
    move t8,zero                  # the victim's own-move note does not count for it
    move t0,zero                  # nor the other hero's
hs_back:
    j HF_H2
    nop
co_two:''')

a = '''if "--holdshared" in sys.argv:                     # (the sixty-fifth glue's fifth form: only a shared mechanic takes both heroes)
'''
assert s.count(a) == 1
i = s.index(a)
j = s.index("        HP_SRC = HP_SRC.replace(_o, _n)\n", i) + len("        HP_SRC = HP_SRC.replace(_o, _n)\n")
add = '''    _o = "hf_h:\\n    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone\\n"
    assert HP_SRC.count(_o) == 1
    HP_SRC = HP_SRC.replace(_o, "hf_h:\\n    j 0x000EE4C0                  # (--holdshared) hs_hf: the laser dome is never a hero's own move\\n    nop\\nhf_h2:\\n    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone\\n")
'''
s = s[:j] + add + s[j:]

a = '''            labels, n = add_code(CO_AT, CO_END, CO_SRC, {}, "a command offered to one hero of a hold's pair goes to the other hero's menu too")
'''
assert s.count(a) == 1
s = s.replace(a, '''            assert CO_AT == 0x000EE4C0                                     # (hp_form jumps there: hs_hf is CO_SRC's first routine)
            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"]},
                                 "the laser dome is never a hero's own move; a command offered to one hero of a hold's pair goes to the other hero's menu too")
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
