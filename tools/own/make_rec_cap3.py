"""TEST ONLY (ninth round, job 4: the Groundshaker's lost hold): <base patch> + A LOG OF EVERY PAIRED-MOVE CAPTURE.
The recorder sits INSIDE the game's capture routine (0x00180380, behind the build's own jump at 0x00180378, so it
works together with the fiftieth glue) and notes each call in a ring of 8:
  0x000F1D00  count of captures
  0x000F1D10  8 x 32 bytes: the game's counter, the return address, the captor's motion part, the victim, the
              move (0xFC .. 0xFF), the hero whose command's callback is running (0x000E7C18, the forty-seventh
              glue's note; 0 = none), the object of the running script, the engine's player
Read it with tools/own/cap_log_probe.py, which polls the ring and writes every capture as a line.
  python -I tools/own/make_rec_cap3.py <baseDir> <outDir>
Memory 0x000F1F00-0x000F1FFF for the routine (the HP kit's block 0x000F1C00 stays free), the ring at 0x000F1D00."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1F00
HOOK = 0x00180380                 # sd s0,0(sp) / mov.s f20,f12
SRC = """
rec:
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    andi t6,t6,7                  # a ring of 8 (16 would reach into this routine: edit_cap_ring8.py)
    sll t6,t6,5
    addu t6,t6,t7
    lui t4,%hi(0x0034D4BC)
    lw t5,%lo(0x0034D4BC)(t4)
    sw t5,0x1D10(t6)
    sw ra,0x1D14(t6)
    sw a0,0x1D18(t6)
    sw a1,0x1D1C(t6)
    sw a2,0x1D20(t6)
    lui t5,0x000E
    lw t5,0x7C18(t5)
    sw t5,0x1D24(t6)
    lw t5,-10076(t4)              # 0x0034D8A4: the running script
    beq t5,zero,rec_s
    nop
    lw t5,56(t5)
rec_s:
    sw t5,0x1D28(t6)
    lw t5,-5816(t4)               # 0x0034E948: the engine's player
    sw t5,0x1D2C(t6)
    sd s0,0(sp)
    j 0x00180388
    mov.s f20,f12
"""
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F2000
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_cap3.py): a log of every paired-move capture. For tests only."]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, w) for i, w in enumerate(code)]
add.append("patch=1,EE,%08X,word,%08X" % (HOOK, (2 << 26) | (labels["rec"] >> 2)))
add.append("patch=1,EE,%08X,word,00000000" % (HOOK + 4))
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
