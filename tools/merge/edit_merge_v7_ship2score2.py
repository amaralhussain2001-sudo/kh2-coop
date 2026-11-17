"""One-off: THE SIXTY-SIXTH GLUE of tools/merge/merge_v7.py (--ship2score), second form (ninth round, job 6).
Runs gq1 / gq2 / gq3 (first form): nearly all points went to player 2, also when only player 1 fired. Why: a
cannon shot does NOT start up while the ship's "fire" 0x01F1EE00 runs (that routine runs for both ships every
step), so the shots had no number and "the ship that fired last" was always ship 2.
Measured with tools/own/make_rec_ginit.py (runs gi1 / gi2): at a cannon shot's start-up (0x01F536D0, called from
0x01F55160, return address 0x01F55168) the register t1 is the WEAPON that fires: a part of its ship, built
behind its ship (ship 1 0x01AB0870: weapons 0x01AB6620, 0x01AB7210; ship 2 0x01AB7280: weapons 0x01ABD030,
0x01ABDC20).
Now: gq_init gives a cannon shot the number 2 when its weapon stands behind ship 2's address, else 1. The hook
of "fire" is gone. A hit whose shot has no number (the other kinds of shots, a ship's own touch) is player 1's.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ship2score2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "the weapon that fires" in s:
    raise SystemExit("already there")

a = '''    (0x01F1EE00, 0x27BDFFD0, "gq_fire"),           # the ship's "fire"
'''
assert s.count(a) == 1
s = s.replace(a, "")

i = s.index("gq_fire:                          # 0x01F1EE00(a0 = a ship): the ship fires")
j = s.index("gq_hit:                           # 0x01F26998(a0 = an enemy, a1 = the hit record = the shot + 72)")
NEW = '''gq_init:                          # 0x01F536D0(a0 = a shot, ..., t1 = the weapon that fires): a cannon shot starts up
    lui t7,0x000E
    srl t4,a0,4
    andi t4,t4,0x0FFF
    ori t3,t7,0xE800              # the shots' table
    addu t4,t4,t3
    lui t6,0x01F5
    ori t6,t6,0x5168              # the cannon's own call of this routine
    bne ra,t6,gqn_w               # another caller: no number
    move t2,zero
    lui t5,0x000F
    lw t5,0x2604(t5)              # ship 2
    addiu t2,zero,1
    beq t5,zero,gqn_w
    sltu t6,t1,t5                 # the weapon stands in front of ship 2: it is ship 1's
    bne t6,zero,gqn_w
    nop
    addiu t2,zero,2
gqn_w:
    sb t2,0(t4)
    addiu sp,sp,-208              # the two instructions that sat at 0x01F536D0
    j 0x01F536D8
    sd s3,152(sp)

'''
s = s[:i] + NEW + s[j:]

a = '''gqh_last:
    lw t2,0x7EF4(t7)              # not known: the ship that fired last
'''
assert s.count(a) == 1
s = s.replace(a, '''gqh_last:
    addiu t2,zero,1               # not known (another kind of shot): player 1's
''')
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
