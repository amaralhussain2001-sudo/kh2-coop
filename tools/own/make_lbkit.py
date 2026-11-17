"""TEST ONLY (tenth round, open item b): <base patch> + "the Large Body's Full Swing zones are on". The same on both PCs. Never
part of the real patch.
READ (research of 2026-11-16, files in the scratchpad's agent2 folder): the Large Body (object 0x0001, model M_EX060) offers
command 533 "Full Swing" through 8 reaction zones of its model (collision type 5, argument 533, group 6: 4 in front, 4 behind,
radius about 150). Group 6 is off by default (the model's mask 0x81); the motions 0x10 / 0x12 (the knock-back of a grounded
Large Body after a hit with reaction 7 or 11, e.g. a combo finisher) switch it on. A script that only presses Triangle never
brings that state about (part 114).
THE KIT: the group test 0x0019BD08(object, group) answers "on" for group 6 of a Large Body (object + 8 = its object entry, whose
first word is 0x0001); everything else goes to the game's routine. So a hero who stands at a Large Body's front or back is
offered Full Swing at any time. Memory 0x000F1C80-0x000F1CFF (the low kit's place: do not use together with make_lowkit.py).
  python -I tools/own/make_lbkit.py <baseDir> <outDir>
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C80
HOOK, HOOK_WORD = 0x0019BD08, 0x27BDFFE0
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
SRC = """
lb_grp:                           # from 0x0019BD08 (j): a0 = the object, a1 = the collision group
    addiu t7,zero,6
    bne a1,t7,lb_game
    nop
    lw t7,8(a0)                   # its object entry
    lui t6,0x0010
    sltu t6,t7,t6
    bne t6,zero,lb_game
    lui t6,0x0200
    sltu t6,t7,t6
    beq t6,zero,lb_game
    nop
    lw t7,0(t7)                   # the object number
    addiu t6,zero,1
    bne t7,t6,lb_game             # not the Large Body
    nop
    jr ra
    addiu v0,zero,1               # group 6 on: the Full Swing zones
lb_game:
    addiu sp,sp,-32               # the instruction that sat at the hook
    j 0x0019BD0C
    nop
"""
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1D00
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
assert "%08X" % HOOK not in used, "the hook word is already patched"
add = ["comment=TEST KIT (tools/own/make_lbkit.py): the Large Body's Full Swing zones are on. For tests only."]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
add.append("patch=1,EE,%08X,word,%08X" % (HOOK, (2 << 26) | ((labels["lb_grp"] >> 2) & 0x3FFFFFF)))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words at %08X; hook %08X, game word %08X)" % (len(code), AT, HOOK, HOOK_WORD))
