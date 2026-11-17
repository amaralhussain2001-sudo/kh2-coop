"""TEST ONLY (ninth round, job 6: a score for each player in the Gummi flight): <base patch> + A LOG OF EVERY HIT OF
A PLAYER'S SHOT ON AN ENEMY. The question: does a shot's record say which ship fired it.
The recorder sits at the start of the flight module's "an enemy takes a hit" 0x01F26998(enemy, hit record). The
module is loaded at run time, so the two patch lines that put the jump there are CONDITIONAL: only while the word
0x01F18014 says "the flight module" (0x636A). Each call is noted in a ring of 4:
  0x000F1D00  count of calls
  0x000F1D10  4 x 176 bytes: the number, the return address, a0 (the enemy), a1 (the hit record), s0, s1, s2, s3
              of the caller, then 36 words from (a1 - 72) = the shot object when the record sits at shot + 72
Read it with tools/own/gshot_probe.py.
  python -I tools/own/make_rec_gshot.py <baseDir> <outDir>
Memory 0x000F1C40-0x000F1CEF for the routine (behind the Gummi launch kit's routine; never with the HP kit), the ring at 0x000F1D00."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
AT = 0x000F1C40
SRC = """
rec:                              # jump from 0x01F26998: a0 = the enemy, a1 = the hit record
    lui t7,0x000F
    lw t0,0x1D00(t7)
    addiu t1,t0,1
    sw t1,0x1D00(t7)
    andi t0,t0,3
    sll t2,t0,7
    sll t3,t0,5
    addu t2,t2,t3
    sll t3,t0,4
    addu t2,t2,t3                 # x 176
    addiu t3,t7,0x1D10
    addu t2,t2,t3                 # the entry
    sw t1,0(t2)
    sw ra,4(t2)
    sw a0,8(t2)
    sw a1,12(t2)
    sw s0,16(t2)
    sw s1,20(t2)
    sw s2,24(t2)
    sw s3,28(t2)
    addiu t3,a1,-72
    addiu t4,t2,32
    addiu t5,zero,36
rl:
    lw t6,0(t3)
    addiu t3,t3,4
    sw t6,0(t4)
    addiu t5,t5,-1
    bne t5,zero,rl
    addiu t4,t4,4
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)
"""
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1CF0          # (0x000F1CF0: the launch kit's latch)
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
lines.append("comment=TEST KIT (tools/own/make_rec_gshot.py): for tests only.")
for i, w in enumerate(code):
    lines.append("patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w))
j = (2 << 26) | ((labels["rec"] >> 2) & 0x3FFFFFF)
lines.append("patch=1,EE,E002636A,extended,01F18014")       # only while the flight module is in memory: the next two lines
lines.append("patch=1,EE,21F26998,extended,%08X" % j)
lines.append("patch=1,EE,21F2699C,extended,00000000")
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
