"""One-off: the --nearest experiment of tools/merge/merge_v6.py, second version: a hero who is down (HP 0) is
never the one that is taken."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v6.py"
t = p.read_text(encoding="utf-8")
if "nr_twin" in t:
    raise SystemExit("already there")
a = t.index('NEAR_SRC = """')
b = t.index("REACT_AT = 0x000F4A00", a)
t = t[:a] + '''NEAR_SRC = """
near_think:                       # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,nr_body
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nr_body
    nop
    beq a0,t4,nr_body             # the heroes think as themselves
    nop
    beq a0,t6,nr_body
    lw t3,0(a0)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nr_body             # a helper: unchanged
    nop
    lw t3,0x48C(t6)               # the twin's unit slot
    beq t3,zero,nr_body
    nop
    lw t3,0(t3)
    beq t3,zero,nr_body           # the twin is down (HP 0): player 1's hero
    nop
    lw t2,0x48C(t4)
    beq t2,zero,nr_dist
    nop
    lw t2,0(t2)
    beq t2,zero,nr_twin           # player 1's hero is down: the twin
    nop
nr_dist:
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
    lwc1 f2,0x70(t4)
    lwc1 f3,0x78(t4)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # distance to player 1's hero, squared
    lwc1 f4,0x70(t6)
    lwc1 f5,0x78(t6)
    sub.s f4,f4,f0
    sub.s f5,f5,f1
    mul.s f4,f4,f4
    mul.s f5,f5,f5
    add.s f4,f4,f5                # distance to the twin, squared
    c.lt.s f4,f2
    bc1f nr_body                  # player 1's hero is nearer (or as near): as it is
    nop
nr_twin:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nr_body                   # this object thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nr_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
"""

''' + t[b:]
old = "the engine's player pointer holds the twin for the length of that call."
assert t.count(old) >= 1
t = t.replace("is nearer to it than player 1's hero (flat distance, positions at object+0x70 / +0x78),\nthe engine's player pointer holds the twin for the length of that call.",
              "is nearer to it than player 1's hero (flat distance, positions at object+0x70 / +0x78),\nthe engine's player pointer holds the twin for the length of that call. A hero who is down (HP 0 in his unit\nslot) is never taken: the other one is, whatever the distance.")
p.write_text(t, encoding="utf-8")
print("ok")
