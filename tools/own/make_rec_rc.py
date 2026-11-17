"""TEST ONLY (ninth round, the user's item 1 of 2026-11-15 evening: do both controllers count in a boss hold?): <base patch> +
a recorder in front of the forty-seventh glue's rc_one (the game's call at 0x00178C7C: a hero's Reaction Command calls back
its source object). The patch's own line at 0x00178C7C (jal rc_one) is taken out and replaced by "jal rec"; rec notes the
call and jumps on to rc_one (nothing else changes).
  0x000F1D00  entries written (at most 16)
  0x000F1D04  the first game counter (0x0034D4BC) that is noted (a constant line of this kit)
  0x000F1D08  calls by player 1's hero from that counter on;   0x000F1D0C  calls by the twin
  0x000F1D10  16 x 32 bytes: counter, source (a0), hero (a1), the pair's named hero (0x000E7EA0), the other hero (+4),
              the captor (+8), the step of the last command sent (0x000E7C1C), the source's object number
Code at 0x000F1F18 (below 0x000F2000). Memory 0x000F1D00-0x000F1FFF: never with make_rec_cap3.py or make_rec_at.py.
Never part of the real patch.
  python -I tools/own/make_rec_rc.py <baseDir> <outDir> <firstCounterDecimal> [objectNumberHex]
With an object number only the commands whose SOURCE is such an object are counted and noted (0x000F1F14).
(Kits built before 2026-11-15 20:35 had no filter.)"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1F18
HOOK = 0x00178C7C
base, out, first = ROOT / sys.argv[1], ROOT / sys.argv[2], int(sys.argv[3])
objf = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xFFFFFFFF
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
key = "patch=1,EE,%08X,word," % HOOK
mine = [i for i, l in enumerate(text) if l.upper().startswith(key.upper())]
assert len(mine) == 1, mine
w = int(text[mine[0]].split(",")[4], 16)
assert w >> 26 == 3, hex(w)                      # a jal (the forty-seventh glue's)
rc_one = (w & 0x03FFFFFF) << 2
SRC = """
rec:
    lui t7,0x000F
    lui t4,0x0035
    lw t4,-11076(t4)
    lw t5,0x1D04(t7)
    sltu t5,t4,t5
    bne t5,zero,rec_go
    move t3,zero
    srl t2,a0,22
    addiu t2,t2,-6
    bne t2,zero,rec_f
    nop
    lw t2,8(a0)
    beq t2,zero,rec_f
    nop
    lw t3,0(t2)
rec_f:
    lw t2,0x1F14(t7)
    addiu t1,zero,-1
    beq t2,t1,rec_n
    andi t1,t3,0xFFFF
    bne t1,t2,rec_go
    nop
rec_n:
    lw t6,0x05CC(t7)
    bne a1,t6,rec_c
    addiu t5,zero,0x1D08
    addiu t5,zero,0x1D0C
rec_c:
    addu t5,t5,t7
    lw t6,0(t5)
    addiu t6,t6,1
    sw t6,0(t5)
    lw t6,0x1D00(t7)
    sltiu t5,t6,16
    beq t5,zero,rec_go
    addiu t5,t6,1
    sw t5,0x1D00(t7)
    sll t6,t6,5
    addu t6,t6,t7
    sw t4,0x1D10(t6)
    sw a0,0x1D14(t6)
    sw a1,0x1D18(t6)
    lui t5,0x000E
    lw t2,0x7EA0(t5)
    sw t2,0x1D1C(t6)
    lw t2,0x7EA4(t5)
    sw t2,0x1D20(t6)
    lw t2,0x7EA8(t5)
    sw t2,0x1D24(t6)
    lw t2,0x7C1C(t5)
    sw t2,0x1D28(t6)
    sw t3,0x1D2C(t6)
rec_go:
    j 0x%08X
    nop
""" % rc_one
code, labels = assemble(AT, SRC, {})
assert AT + 4 * len(code) <= 0x000F2000, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST RECORDER (tools/own/make_rec_rc.py %d): a hero's Reaction Command calls back its source. For tests only." % first]
add += ["patch=1,EE,%08X,word,%08X" % (AT + 4 * i, x) for i, x in enumerate(code)]
add.append("patch=1,EE,000F1D04,word,%08X" % first)
add.append("patch=1,EE,000F1F14,word,%08X" % objf)
for l in add[1:]:
    assert l.split(",")[2].upper() not in used, l
text[mine[0]] = "patch=1,EE,%08X,word,%08X" % (HOOK, (3 << 26) | (labels["rec"] >> 2))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(code), "words; rc_one at %08X" % rc_one)
