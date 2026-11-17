"""TEST ONLY: <base patch> + a recorder at the entry of "offer a command to a control object's slot" (0x001BD418;
0x001BD3E0 jumps into it). For one command number (default 299 = Break Raid):
  0x000F1D00  count of offers
  0x000F1D10  ring of 16 x (control object, return address, the engine's player at that moment, frame counter)
  0x000F1E10  first offer only: 0x1C0 bytes of the stack from sp (the callers' saved registers and return addresses)
  0x000F1FD0  first offer only: a1 (slot), a3 (record), t0, t1, s0 .. s7
Memory 0x000F1C00-0x000F1FFF (lane G's spare block, zero in every recorded run). Never part of the real patch.
  python -I tools/own/make_rec_offer.py <baseDir> <outDir> [commandNumber]
"""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
cmd = int(sys.argv[3], 0) if len(sys.argv) > 3 else 299
SRC = """
rec:
    addiu t7,zero,%d
    bne a2,t7,rec_out
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    andi t6,t6,15
    sll t6,t6,4
    addu t6,t6,t7
    sw a0,0x1D10(t6)
    sw ra,0x1D14(t6)
    lui t4,%%hi(0x0034E948)
    lw t4,%%lo(0x0034E948)(t4)
    sw t4,0x1D18(t6)
    lui t4,%%hi(0x0034D4BC)
    lw t4,%%lo(0x0034D4BC)(t4)
    sw t4,0x1D1C(t6)
    addiu t4,zero,1
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
    sw a1,0x1FD0(t7)
    sw a3,0x1FD4(t7)
    sw t0,0x1FD8(t7)
    sw t1,0x1FDC(t7)
    sw s0,0x1FE0(t7)
    sw s1,0x1FE4(t7)
    sw s2,0x1FE8(t7)
    sw s3,0x1FEC(t7)
    sw s4,0x1FF0(t7)
    sw s5,0x1FF4(t7)
    sw s6,0x1FF8(t7)
    sw s7,0x1FFC(t7)
rec_out:
    addiu t7,zero,36
    j 0x001BD420
    addiu sp,sp,-64
""" % cmd
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_offer.py, command %d): for tests only." % cmd]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,001BD418,word,%08X" % ((2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,001BD41C,word,00000000")
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
