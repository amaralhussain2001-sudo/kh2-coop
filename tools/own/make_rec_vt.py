"""TEST ONLY: make_rec_vt.py's sister: a recorder at the entry of a routine that notes ONLY THE CALLS WHERE THE
OBJECT AT (register + 12) HAS A BAD CLASS TABLE (its first word is not in the program's data 0x0033xxxx-0x0037xxxx):
a freed object that somebody still points to (eighth round: the Keyblade change; routine 0x0017FE10, register a1).
In the notes "a0" is that object and "s3" is the register's own value. The routine's first two instructions must not depend on where they stand (give them as hex words).
  0x000F1D00  count of bad calls
  0x000F1D10  the first 8 bad calls, 0x20 bytes each: return address, a0, s0, s1, s2, s3, the game's counter,
              the word at s0 + 8 (if s0 looks like an object: its object-entry pointer)
  0x000F1E10  first bad call only: 0x1C0 bytes of the stack from sp (the callers' saved registers / return addresses)
Read it with tools/own/recbad_probe.py. Never part of the real patch.
  python -I tools/own/make_rec_vt.py <baseDir> <outDir> <hexAddress> <hexWord1> <hexWord2> [register=a0]
Memory 0x000F1C00-0x000F1FFF (the test recorders' block; not together with the other test kits that use it).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
hook, w1, w2 = (int(x, 16) for x in sys.argv[3:6])
REG = sys.argv[6] if len(sys.argv) > 6 else "a0"       # the register whose value is judged (a0, a1, ...)
SRC = """
rec:
    lw t7,12(@REG@)               # the object this record points to (word + 12)
    srl t6,t7,20
    beq t6,zero,rec_out           # none: not our case
    sltiu t6,t6,0x20
    beq t6,zero,rec_bad           # not a pointer at all
    nop
    lw t7,0(t7)                   # its class table: must lie in the program's data (0x0033xxxx .. 0x0037xxxx)
    srl t7,t7,16
    addiu t7,t7,-0x33
    sltiu t7,t7,5
    bne t7,zero,rec_out
    nop
rec_bad:
    lui t7,0x000F
    lw t6,0x1D00(t7)
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    sltiu t4,t6,8
    beq t4,zero,rec_out
    nop
    sll t6,t6,5
    addu t6,t6,t7
    sw ra,0x1D10(t6)
    lw t4,12(@REG@)
    sw t4,0x1D14(t6)              # the object with the bad class table
    sw s0,0x1D18(t6)
    sw s1,0x1D1C(t6)
    sw s2,0x1D20(t6)
    sw @REG@,0x1D24(t6)           # the record itself (an object's motion part = object + 0x140)
    lui t4,0x0035
    lw t4,-11076(t4)              # the game's counter 0x0034D4BC
    sw t4,0x1D28(t6)
    srl t4,s0,20
    beq t4,zero,rec_noobj
    sltiu t3,t4,0x20
    beq t3,zero,rec_noobj
    nop
    lw t4,8(s0)
    sw t4,0x1D2C(t6)
rec_noobj:
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
rec_out:
    nop
    j 0x%08X
    nop
""" % (hook + 8)
SRC = SRC.replace("@REG@", REG)
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
code, labels = assemble(AT, SRC, {})
i = (labels["rec_out"] - AT) // 4
code = [w if isinstance(w, int) else w[1] for w in code]
code[i], code[i + 2] = w1, w2
assert AT + 4 * len(code) <= 0x000F1D00, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_vt.py, routine %08X): for tests only." % hook]
words = [(AT + 4 * k, w) for k, w in enumerate(code)] + [(hook, (2 << 26) | (labels["rec"] >> 2)), (hook + 4, 0)]
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words")
