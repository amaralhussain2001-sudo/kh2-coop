"""TEST ONLY: <base patch> + a RECORDER OF THE COMMAND-ROW JUDGE (plan row 44: why is the other hero's Drive row dim
while one hero is in a form?). Never part of the real patch. The same on both PCs.

The game judges a row of the command menu with 0x001BC2A8(command entry, hero): result 0 = lit, 5 = dim (other
values: other states). The kit notes the two arguments at the entry and, at the routine's "jr ra" (0x001BC388),
writes for each hero a table of the commands judged (up to 14 command ids each):
  0x000F1E00  player 1's hero: 14 x (command id, newest result, calls, calls that gave "not lit")
  0x000F1EE0  the twin:        the same
and the state at the newest judged call for each hero (block 0x000F1FC0 hero, 0x000F1FE0 twin):
  +00 the word 0x0034F240   +04 the hero's body form (object + 0xB50)   +08 his control object's dim mask (+0xAB0)
  +0C the lock word 0x00351EB8   +10 the lock word 0x00351EC0   +14 hero + 0x588   +18 the save's form byte
  +1C the game's counter
Read it with tools/own/rowrec_probe.py.
  python -I tools/own/make_rowrec.py <baseDir> <outDir>
Memory: routines 0x000F1C00-0x000F1DF7, values 0x000F1E00-0x000F1FFF, the two noted arguments 0x000F1DF8 / FC
(the test recorders' block; NOT together with the HP, kill, heap, hurt or revenge kits). Hooks: 0x001BC2A8, 0x001BC388.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
SRC = """
re_in:                            # from 0x001BC2A8 (its first instruction ran in the delay slot)
    sd s1,8(sp)                   # the routine's second instruction
    lui t7,0x000F
    sw a0,0x1DF8(t7)
    sw a1,0x1DFC(t7)
    j 0x001BC2B0
    nop
re_out:                           # from 0x001BC388 (its "jr ra"; the stack is already put back)
    lui t9,0x000F
    lw t0,0x1DF8(t9)              # the command entry
    lw t1,0x1DFC(t9)              # the hero
    beq t0,zero,re_ret
    nop
    beq t1,zero,re_ret
    nop
    lui t7,0x0035
    lw t6,-5816(t7)               # player 1's hero
    beq t1,t6,re_go
    li t8,0
    lw t6,0x05CC(t9)              # the twin
    bne t1,t6,re_ret
    li t8,1
re_go:
    lhu t2,0(t0)                  # command id
    sll t3,t8,5
    addu t3,t3,t9                 # state block: 0x1FC0 + who x 0x20
    lui t7,0x0035
    lw t4,-3520(t7)               # 0x0034F240
    sw t4,0x1FC0(t3)
    lw t4,0xB50(t1)
    sw t4,0x1FC4(t3)
    lw t4,0xB44(t1)               # his control object
    beq t4,zero,re_noc
    move t5,zero
    lw t5,0xAB0(t4)
re_noc:
    sw t5,0x1FC8(t3)
    lw t4,7864(t7)                # 0x00351EB8
    sw t4,0x1FCC(t3)
    lw t4,7872(t7)                # 0x00351EC0
    sw t4,0x1FD0(t3)
    lw t4,0x588(t1)
    sw t4,0x1FD4(t3)
    lui t7,0x0033
    lbu t4,-4012(t7)              # the save's form byte 0x0032F054
    sw t4,0x1FD8(t3)
    lui t7,0x0035
    lw t4,-11076(t7)              # the game's counter
    sw t4,0x1FDC(t3)
    sll t3,t8,5
    sll t4,t8,8
    subu t3,t4,t3                 # who x 0xE0
    addu t3,t3,t9
    li t5,14
re_find:
    lw t4,0x1E08(t3)              # calls of this entry (0 = free)
    beq t4,zero,re_new
    lw t6,0x1E00(t3)              # its command id
    beq t6,t2,re_hit
    addiu t5,t5,-1
    beq t5,zero,re_ret
    nop
    b re_find
    addiu t3,t3,16
re_new:
    sw t2,0x1E00(t3)
re_hit:
    addiu t4,t4,1
    sw t4,0x1E08(t3)
    sw v0,0x1E04(t3)
    beq v0,zero,re_ret
    nop
    lw t4,0x1E0C(t3)
    addiu t4,t4,1
    sw t4,0x1E0C(t3)
re_ret:
    jr ra
    nop
"""
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1DF8, len(code)


def jmp(target):
    return 0x08000000 | ((target >> 2) & 0x03FFFFFF)


used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_rowrec.py): a recorder of the command-row judge, for tests only."]
words = [(AT + 4 * i, w) for i, w in enumerate(code)]
words += [(0x001BC2A8, jmp(labels["re_in"])), (0x001BC2AC, 0x27BDFFD0),       # j re_in / addiu sp,sp,-48
          (0x001BC388, jmp(labels["re_out"]))]                                # j re_out (addiu sp,sp,48 stays behind it)
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words)" % len(code))
