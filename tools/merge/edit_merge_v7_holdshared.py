"""One-off: THE SIXTY-FIFTH GLUE of tools/merge/merge_v7.py, fifth form (option --holdshared, with --holdpair): ONLY A SHARED
MECHANIC TAKES BOTH HEROES (ninth round, the user's item 4 of 2026-11-15 evening: "For single-target attacks, prefer capturing
only the targeted player. For genuinely shared boss mechanics, both players should participate meaningfully."; STATE part 110).
READ / SEEN (part 110, `tools/own/cap_kinds.py` over the fifty fights on v115 and the last Xemnas runs): in every fight but
one, the boss's script takes ONE victim with a move and the glue's mirror added the second hero. Only the last Xemnas's
laser dome (move 262 = 0x106; B_EX170_LAST, object 0x081F, and its Data fight 0x09CA) is the game's own party move: the
script captures the player AND Riku with it and attaches Riku to the player (B_EX170_LAST.txt, around its line 8124);
each hero has his own "Reflect" there.
NOW (only with --holdshared): hp_form makes a pair only when the captor is 0x081F or 0x09CA and the move is 0x106. Every
other capture takes the hero the boss's script names, as the game (builds 13 to 19). What stays for every boss: the
stray capture of a free bystander is not made (the Groundshaker's cure), the hold note, the nets (the one-minute rule
and the mirror's 40 steps for a pair), the release that works. The capture hook passes the move to hp_form in a3; the
attach wrapper passes -1 (an attach never starts a pair any more).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--holdshared" in s:
    raise SystemExit("already there")

DOC = '''THE SIXTY-FIFTH GLUE'S FIFTH FORM (option --holdshared, with --holdpair): ONLY A SHARED MECHANIC TAKES BOTH HEROES. A pair is
made only for the last Xemnas's laser dome (captor 0x081F or 0x09CA, move 0x106: the game itself captures the player and
Riku with it). Every other boss capture takes the hero the script names, as the game; the stray capture of a free
bystander is still not made, and the nets stay.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

# the three source changes, made at the module level after HP_SRC (so every assembly of HP_SRC gets them)
c1_old = '''    ld a1,8(sp)
    addiu a1,a1,-320
    jal hp_form                   # is this the start of a hold that takes the other hero too
    ld a0,16(sp)
'''
c1_new = '''    ld a1,8(sp)
    addiu a1,a1,-320
    ld a3,24(sp)                  # (--holdshared) the move
    jal hp_form                   # is this the start of a hold that takes the other hero too
    ld a0,16(sp)
'''
c2_old = '''    ld a0,40(sp)
    jal hp_form
    ld a1,48(sp)
'''
c2_new = '''    ld a0,40(sp)
    addiu a3,zero,-1              # (--holdshared) an attach never starts a pair
    jal hp_form
    ld a1,48(sp)
'''
c3_old = '''    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command
    nop
    sw a0,0x7EA0(t7)              # A PAIR: the hero the script names, the other hero, the captor
'''
c3_new = '''    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command
    nop
    addiu t1,zero,0x106           # (--holdshared) ONLY A SHARED MECHANIC: the last Xemnas's laser dome
    bne a3,t1,hf_no
    lw t2,8(a1)                   # the captor's object entry
    beq t2,zero,hf_no
    nop
    lw t2,0(t2)                   # its object number
    addiu t1,zero,0x081F
    beq t2,t1,hf_sh
    addiu t1,zero,0x09CA
    bne t2,t1,hf_no
    nop
hf_sh:
    sw a0,0x7EA0(t7)              # A PAIR: the hero the script names, the other hero, the captor
'''
for old in (c1_old, c2_old, c3_old):
    assert s.count(old) == 1, old[:60]

a = '''HP_SRC = """'''
assert s.count(a) == 1
i = s.index(a)
j = s.index(NL + '"""', i + len(a)) + 1
j = s.index(NL, j) + 1
while s[j:].startswith("   .replace("):
    j = s.index(NL, j) + 1
s = s[:j] + '''
if "--holdshared" in sys.argv:                     # (the sixty-fifth glue's fifth form: only a shared mechanic takes both heroes)
    for _o, _n in ((%r, %r), (%r, %r), (%r, %r)):
        assert HP_SRC.count(_o) == 1
        HP_SRC = HP_SRC.replace(_o, _n)
''' % (c1_old, c1_new, c2_old, c2_new, c3_old, c3_new) + s[j:]

a = '''    if "--holdpair" in sys.argv:                                           # sixty-fifth glue (both heroes inside the same hold of a boss)
        assert "--together" in sys.argv, "--holdpair needs --together (the forty-seventh glue's pair exit)"
'''
assert s.count(a) == 1
s = s.replace(a, a + '''        assert "--holdpads" not in sys.argv or "--holdshared" not in sys.argv, "--holdshared leaves the sixty-eighth glue out: each hero keeps his own controller"
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
