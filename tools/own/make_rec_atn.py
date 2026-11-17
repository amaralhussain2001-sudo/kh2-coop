"""TEST ONLY: <base patch> + a recorder at the entry of any routine whose first two instructions do not depend on
where they stand (give them as hex words).
  0x000F1D00  count of calls
  0x000F1D10  ring of 16 x (return address, a0, a1, frame counter)
  0x000F1E10  first call only: 0x1C0 bytes of the stack from sp (the callers' saved registers and return addresses)
Memory 0x000F1C00-0x000F1FFF (lane G's spare block). Never part of the real patch.
  python -I tools/own/make_rec_atn.py <baseDir> <outDir> <hexAddress> <hexWord1> <hexWord2> <reg1> <reg2> <N>
reg1 / reg2: registers stored in the ring in place of a0 / a1 (for example s0 s2).
THIS COPY (make_rec_atn.py, eighth round): the stack is kept at call number N (1 = the first call, as the
original tool), so the callers of a LATER call can be read.
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
hook, w1, w2 = (int(x, 16) for x in sys.argv[3:6])
reg1, reg2, NCALL = sys.argv[6], sys.argv[7], int(sys.argv[8])
SRC = """
rec:
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    andi t6,t6,15
    sll t6,t6,4
    addu t6,t6,t7
    sw ra,0x1D10(t6)
    sw %s,0x1D14(t6)
    sw %s,0x1D18(t6)
    lui t4,%%hi(0x0034D4BC)
    lw t4,%%lo(0x0034D4BC)(t4)
    sw t4,0x1D1C(t6)
    addiu t4,zero,%d
    bne t5,t4,rec_out
    addiu t6,t7,0x1E10
    move t5,sp
    addiu t4,sp,0x1C0
rec_l:
    lw t8,0(t5)
    sw t8,0(t6)
    addiu t5,t5,4
    bne t5,t4,rec_l
    addiu t6,t6,4
rec_out:
    nop
    j 0x%08X
    nop
""" % (reg1, reg2, NCALL, hook + 8)
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
i = (labels["rec_out"] - AT) // 4
code[i], code[i + 2] = w1, w2
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_atn.py, routine %08X, stack of call %d): for tests only." % (hook, NCALL)]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,%08X,word,%08X" % (hook, (2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,%08X,word,00000000" % (hook + 4))
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
