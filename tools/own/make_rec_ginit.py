"""TEST ONLY (ninth round, job 6): <base patch> + A LOG OF EVERY START-UP OF A CANNON SHOT in the Gummi flight
(0x01F536D0(shot, ...), the class 0x01F81458). The question: which of the caller's registers or inputs says
which ship fires (run gq1: the shots do not start up while the ship's "fire" 0x01F1EE00 runs).
As make_rec_gshot.py: the two patch lines that put the jump into the module are conditional on the word
0x01F18014 = 0x636A. A ring of 4:
  0x000F1D00  count
  0x000F1D10  4 x 176 bytes: the number, ra, a0 .. a3, t0, t1, s0 .. s7, then 4 words at a3 (a place), then 24 words
              from the stack (the caller's frame: sp + 0 ..)
Read it with tools/own/ginit_probe.py.
  python -I tools/own/make_rec_ginit.py <baseDir> <outDir>
Memory 0x000F1C40-0x000F1CEF (behind the Gummi launch kit's routine), the ring at 0x000F1D00."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
AT = 0x000F1C40
SRC = """
rec:                              # jump from 0x01F536D0: a0 = the shot
    lui t7,0x000F
    lw t4,0x1D00(t7)
    addiu t5,t4,1
    sw t5,0x1D00(t7)
    andi t4,t4,3
    sll t2,t4,7
    sll t3,t4,5
    addu t2,t2,t3
    sll t3,t4,4
    addu t2,t2,t3                 # x 176
    addiu t3,t7,0x1D10
    addu t2,t2,t3                 # the entry
    sw t5,0(t2)
    sw ra,4(t2)
    sw a0,8(t2)
    sw a1,12(t2)
    sw a2,16(t2)
    sw a3,20(t2)
    sw t0,24(t2)
    sw t1,28(t2)
    sw s0,32(t2)
    sw s1,36(t2)
    sw s2,40(t2)
    sw s3,44(t2)
    sw s4,48(t2)
    sw s5,52(t2)
    sw s6,56(t2)
    sw s7,60(t2)
    lw t6,0(a3)
    sw t6,64(t2)
    lw t6,4(a3)
    sw t6,68(t2)
    lw t6,8(a3)
    sw t6,72(t2)
    sw sp,76(t2)
    addiu sp,sp,-208              # the two instructions that sat at 0x01F536D0
    j 0x01F536D8
    sd s3,152(sp)
"""
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1CF0, len(code)
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
used = set()
for l in lines:
    if l.startswith("patch=1,EE,"):
        try:
            used.add(int(l.split(",")[2], 16) & 0x0FFFFFFC)
        except ValueError:
            pass
for i in range(len(code)):
    assert AT + 4 * i not in used, "the base patch writes %08X" % (AT + 4 * i)
lines.append("comment=TEST KIT (tools/own/make_rec_ginit.py): for tests only.")
for i, w in enumerate(code):
    lines.append("patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w))
j = (2 << 26) | ((labels["rec"] >> 2) & 0x3FFFFFF)
lines.append("patch=1,EE,E002636A,extended,01F18014")       # only while the flight module is in memory: the next two lines
lines.append("patch=1,EE,21F536D0,extended,%08X" % j)
lines.append("patch=1,EE,21F536D4,extended,00000000")
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
