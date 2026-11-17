"""One-off: the forty-seventh glue's rule "an object that holds one hero does not take the other hero's command"
also counts the hero it held LESS THAN 90 STEPS AGO (the hold memory of the glues 36 / 39). Reason: run cap10
(Shan-Yu, both players press): the four stray calls of the third clash were still there; between two pushes
the held bit is off for a moment. The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_sender2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "rc_mem" in s:
    raise SystemExit("already there")
a = '''    lw t2,0x240(t3)               # does the source hold the OTHER hero in a paired move?
    bne t2,t9,rc_send
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    beq t2,zero,rc_send
    nop
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
rc_send:'''
assert s.count(a) == 1
b = '''    lw t2,0x240(t3)               # does the source hold the OTHER hero in a paired move?
    bne t2,t9,rc_mem
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    beq t2,zero,rc_mem
    nop
rc_drop:
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
rc_mem:                           # not at this moment: did it hold the other hero less than 90 steps ago?
    lui t7,0x000E
    lw t2,0x7C0C(t7)
    bne t2,t9,rc_send             # the memory is about another object
    lw t2,-11076(t5)              # the game's counter
    lw t1,0x7C14(t7)
    subu t2,t2,t1
    sltiu t2,t2,90
    beq t2,zero,rc_send
    lw t2,0x7C10(t7)              # 1 = the twin was held, 2 = player 1's hero
    addiu t1,zero,1
    beq t3,t6,rc_who              # the other hero is the twin: the memory must say 1
    nop
    addiu t1,zero,2
rc_who:
    beq t2,t1,rc_drop
    nop
rc_send:'''
s = s.replace(a, b)
a = '''(1) rc_one (the call at 0x00178C7C): when the source is an object that is neither a hero nor a helper and it
    HOLDS THE OTHER HERO in a paired move at this moment, this hero's command does nothing. Otherwise the callback'''
assert s.count(a) == 1
s = s.replace(a, '''(1) rc_one (the call at 0x00178C7C): when the source is an object that is neither a hero nor a helper and it
    HOLDS THE OTHER HERO in a paired move at this moment, or held him less than 90 steps ago (the hold memory of
    the glues 36 / 39), this hero's command does nothing. Otherwise the callback''')
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
