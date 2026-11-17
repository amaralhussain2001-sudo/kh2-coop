"""TEST ONLY: <base patch> + "a hero's HP is set to a low value at a given frame, once" (eighth round: who heals
player 2, Second Chance). The hero is found through his object (player 1's hero 0x0034E948, the twin 0x000F05CC),
so the kit works in every room (tools/own/make_healkit.py needs the slot address of one disc). After that frame
the game is free to heal or hurt him. The same on both PCs. Never part of the real patch.

How: the player class's per-frame method (table word 0x0035241C) goes through low_tick first (as make_killkit.py),
then to whatever was there.
  python -I tools/own/make_lowhp.py <baseDir> <outDir> who@sessionFrame=hp[,who@sessionFrame=hp...]
  who = hero | twin.   Example: twin@6000=3
Memory: 0x000F1C00-0x000F1CFF (the test recorders' block; not together with make_killkit.py or make_godkit.py).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
ents = []
for part in sys.argv[3].split(","):
    who, rest = part.split("@")
    frame, hp = rest.split("=")
    ents.append(((int(frame) - 152) & 0xFFFFFFFF, {"hero": 0, "twin": 1}[who], int(hp)))
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
if old is None:
    old = 0x00178758
    at_line = len(text)
    text.append("")
SRC = """
low_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # the engine's player: once a step
    bne a0,t6,lt_old
    nop
    lui t9,%hi(lt_table)
    addiu t9,t9,%lo(lt_table)
lt_loop:
    lw t0,0(t9)                   # the counter value of this entry (0 = the end)
    beq t0,zero,lt_old
    nop
    lui t7,0x0035
    lw t2,-11076(t7)              # the game's counter 0x0034D4BC
    subu t2,t2,t0
    sltiu t2,t2,2
    beq t2,zero,lt_next
    nop
    lw t4,4(t9)
    lui t7,0x0035
    lw t5,-5816(t7)               # 0 = player 1's hero
    beq t4,zero,lt_go
    nop
    lui t7,0x000F
    lw t5,0x05CC(t7)              # 1 = the twin
lt_go:
    beq t5,zero,lt_next
    nop
    lw t5,0x48C(t5)               # his unit slot
    beq t5,zero,lt_next
    nop
    lw t4,8(t9)
    sw t4,0(t5)                   # HP
lt_next:
    b lt_loop
    addiu t9,t9,12
lt_old:
    j @OLD@
    nop
lt_table:
""".replace("@OLD@", "0x%08X" % old)
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
for c, w, hp in ents:
    code += [c, w, hp]
code.append(0)
assert AT + 4 * len(code) <= 0x000F1D00, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_lowhp.py %s): for tests only." % sys.argv[3]]
for i, w in enumerate(code):
    s = "%08X" % (AT + 4 * i)
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["low_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, sys.argv[3], "(%d words; the old method %08X)" % (len(code), old))
