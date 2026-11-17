"""TEST ONLY: <base patch> + a RECORDER OF THE "REVENGE" COUNT (plan row 40, eighth round). Never part of the real
patch. The same on both PCs.

What the game does (read in the program): routine 0x00185CB8(target object, hit record) adds the attack's
revenge value (attack entry = hit record + 0x20, byte + 0x2A) to the target's counter (float at object + 0xAF0),
then calls 0x001D6020. The counter runs down again in 0x00185C78. The hit record's attacker is at + 0x10
(HYPOTHESIS from 0x0018C960: the source record's word + 8).

The kit counts the calls by attacker and keeps the highest counter value (block 0x000F1FC0, read it with
sweepm_probe.py RANGES=000F1FC0:20):
  +00 calls with player 1's hero as the attacker   +04 the twin   +08 anybody else
  +0C the highest counter ever (float bits)        +10 the target that had it
  +14 the newest counter (float bits)              +18 its target      +1C the amount added by the newest hit
  python -I tools/own/make_revkit.py <baseDir> <outDir>
Memory: routine 0x000F1C80-0x000F1CFF, values 0x000F1FC0-0x000F1FDF (the test recorders' block; fits beside
make_godkit.py and make_heapkit.py). Hook: 0x00185CE8 (the call of 0x001D6020).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C80
RV = 0x000F1FC0
HOOK = 0x00185CE8
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
SRC = """
rk:
    lui t5,%hi(RV)
    addiu t5,t5,%lo(RV)
    lw t6,0x10(s1)                # the attacker of this hit
    lui t7,0x0035
    lw t7,-5816(t7)               # player 1's hero
    beq t6,t7,rk_who
    li t8,0
    lui t7,0x000F
    lw t7,0x05CC(t7)              # the twin
    beq t6,t7,rk_who
    li t8,4
    li t8,8
rk_who:
    addu t7,t5,t8
    lw t6,0(t7)
    addiu t6,t6,1
    sw t6,0(t7)
    mfc1 t6,f0                    # the counter after this hit
    lw t7,0x0C(t5)
    sltu t9,t7,t6
    beq t9,zero,rk_1
    nop
    sw t6,0x0C(t5)
    sw a0,0x10(t5)
rk_1:
    sw t6,0x14(t5)
    sw a0,0x18(t5)
    lw t6,0x20(s1)
    lbu t6,42(t6)
    sw t6,0x1C(t5)
    j 0x001D6020
    nop
"""
code, labels = assemble(AT, SRC, {"RV": RV})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1D00, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_revkit.py): a recorder of the revenge count, for tests only."]
words = [(AT + 4 * i, w) for i, w in enumerate(code)] + [(HOOK, 0x0C000000 | (labels["rk"] >> 2))]
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words)" % len(code))
