"""TEST ONLY: <base patch WITH the HP kit> + a RECORDER OF "A HERO WAS HURT" (plan row 41: can player 2 be hurt
while his Limit plays?). Never part of the real patch. The same on both PCs.

How: the player class's per-frame method (table word 0x0035241C) goes through hurt_tick first, then to whatever
was there (the HP kit's god_tick, which sets the HP to full again). So at the start of a hero's step "HP below
his most HP" means: he took damage since his last step. Such steps are counted for each hero, sorted by the
ACTION WORD OF HIS STEP BEFORE THE HIT (object + 0x154, kept at 0x000F1E08 / 0C): a table of up to 15 actions for each hero.
  0x000F1E00  hurt steps of player 1's hero         0x000F1E04  of the twin
  0x000F1E10  player 1's hero: 15 x (action, steps hurt in it, the game's counter at the first, HP at the newest)
  0x000F1F00  the twin: the same
Read it with tools/own/hurt_probe.py.
  python -I tools/own/make_hurtkit2.py <baseDir> <outDir>
Memory: routine 0x000F1D00-0x000F1DFF, values 0x000F1E00-0x000F1FEF (the test recorders' block; NOT together
with make_heapkit.py, make_revkit.py or a recorder kit).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1D00
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
assert old is not None, "the base has no patch at the table word (put the HP kit under this kit)"
SRC = """
hurt_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # player 1's hero
    lui t9,0x000F
    beq a0,t6,ht_go
    li t8,0
    lw t6,0x05CC(t9)              # the twin
    bne a0,t6,ht_old
    li t8,1
ht_go:
    beq a0,zero,ht_old
    nop
    lw t6,0x48C(a0)               # his unit slot
    beq t6,zero,ht_old
    nop
    lw t4,0(t6)                   # HP
    lw t5,4(t6)                   # most HP
    slt t0,t4,t5
    sll t5,t8,2
    addu t5,t5,t9
    beq t0,zero,ht_note           # full: not hurt since the last step
    nop
    lw t3,0x1E00(t5)              # this hero's hurt steps
    addiu t3,t3,1
    sw t3,0x1E00(t5)
    lw t1,0x1E08(t5)              # the action word of his LAST step (before the hit)
    sll t2,t8,4
    subu t2,t2,t8
    sll t2,t2,4                   # who x 0xF0
    addu t2,t2,t9
    li t3,15
ht_find:
    lw t0,0x1E14(t2)              # steps of this entry (0 = free)
    beq t0,zero,ht_new
    lw t5,0x1E10(t2)              # its action
    beq t5,t1,ht_hit
    addiu t3,t3,-1
    beq t3,zero,ht_note           # the table is full
    nop
    b ht_find
    addiu t2,t2,16
ht_new:
    sw t1,0x1E10(t2)
    lui t7,0x0035
    lw t5,-11076(t7)              # the game's counter
    sw t5,0x1E18(t2)
ht_hit:
    addiu t0,t0,1
    sw t0,0x1E14(t2)
    sw t4,0x1E1C(t2)
    b ht_note
    nop
ht_note:                          # remember the action of this step for the next one
    beq a0,zero,ht_old
    nop
    lui t7,0x0035
    lw t6,-5816(t7)
    lui t9,0x000F
    beq a0,t6,ht_n1
    li t8,0
    lw t6,0x05CC(t9)
    bne a0,t6,ht_old
    li t8,1
ht_n1:
    sll t5,t8,2
    addu t5,t5,t9
    lw t1,0x154(a0)
    andi t1,t1,0xFFFF
    sw t1,0x1E08(t5)
ht_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old)
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1E00, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_hurtkit2.py): a recorder of hurt steps, for tests only."]
for i, w in enumerate(code):
    s = "%08X" % (AT + 4 * i)
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["hurt_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words; the old method %08X)" % (len(code), old))
