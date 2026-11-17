"""TEST ONLY (ninth round, item 1: the last Xemnas's "Reflect"): <base patch> + a recorder at the entry of "offer a command to a
control object's slot" (0x001BD418; 0x001BD3E0 jumps into it), for one command number, from one game counter on. As
make_rec_offer.py, but without the stack copy and in the block 0x000F1D00-0x000F1FFF (so it goes with the god kit, never
with make_rec_cap3.py, make_rec_at.py or make_rec_rc.py):
  0x000F1D00  offers noted (at most 16);  0x000F1D04  the first counter (a constant line);  0x000F1D08  all offers from then
  0x000F1D10  16 x 16 bytes: control object (a0), return address, the engine's player (0x0034E948), game counter
Code at 0x000F1F40. Never part of the real patch.
  python -I tools/own/make_rec_offer2.py <baseDir> <outDir> <command> <firstCounterDecimal>"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1F40
base, out, cmd, first = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3], 0), int(sys.argv[4])
SRC = """
rec:
    addiu t7,zero,%d
    bne a2,t7,rec_out
    lui t7,0x000F
    lui t4,0x0035
    lw t4,-11076(t4)
    lw t5,0x1D04(t7)
    sltu t5,t4,t5
    bne t5,zero,rec_out
    nop
    lw t6,0x1D08(t7)
    addiu t6,t6,1
    sw t6,0x1D08(t7)
    lw t6,0x1D00(t7)
    sltiu t5,t6,16
    beq t5,zero,rec_out
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    sll t6,t6,4
    addu t6,t6,t7
    sw a0,0x1D10(t6)
    sw ra,0x1D14(t6)
    lui t5,0x0035
    lw t5,-5816(t5)
    sw t5,0x1D18(t6)
    sw t4,0x1D1C(t6)
rec_out:
    addiu t7,zero,36
    j 0x001BD420
    addiu sp,sp,-64
""" % cmd
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F2000
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_offer2.py, command %d from counter %d): for tests only." % (cmd, first)]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,000F1D04,word,%08X" % first)
add.append("patch=1,EE,001BD418,word,%08X" % ((2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,001BD41C,word,00000000")
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
