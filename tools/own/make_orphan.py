"""TEST ONLY: <base patch> + ONE STRAY CAPTURE at one moment (eighth round, part 83): the game's capture routine
0x00180378 is called once for player 1's hero with a boss of the room as the captor, WITHOUT any script that
would end it. That is the state the Groundshaker fault left a hero in (a captured motion nobody tracks); with it
the "no hero is held for ever" rule can be tested on purpose. The same on both PCs. Never part of the real patch.

How: the player class's per-frame method (table word 0x0035241C, chained after whatever is there, the HP kit
too): the first time player 1's hero is stepped at or past the frame AND the boss object (found by its object
number with the game's 0x0016B740) is there: 0x00180378(boss + 320, hero, move, time 0).

  python -I tools/own/make_orphan.py <baseDir> <outDir> <sessionFrame> <hexBossObjectNumber> <hexMove>
  (the Groundshaker is object 0x0459; a move is 0xFC .. 0xFF)
Memory: 0x000F1E00-0x000F1EEF, "done" 0x000F1EF0, the captor found 0x000F1EF4 (the test block; the HP kit sits at
0x000F1C00 and can be in the base; NOT together with the recorders, which use 0x000F1E10).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1E00
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
frame, boss, move = int(sys.argv[3]), int(sys.argv[4], 16), int(sys.argv[5], 16)
count = frame - 152
assert 0 < count < 0x8000 and 0 < boss < 0x8000 and 0xFC <= move <= 0xFF
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
assert old is not None, "the base has no routine at the player class's per-frame word"
SRC = """
or_tick:
    lui t7,0x000F
    lw t6,0x1EF0(t7)              # done already
    bne t6,zero,or_old
    lui t5,0x0035
    lw t4,-11076(t5)              # 0x0034D4BC: the game's frame counter
    addiu t3,zero,@N@
    slt t3,t4,t3
    bne t3,zero,or_old            # not yet
    nop
    lw t3,-5816(t5)               # only in the step of player 1's hero
    bne a0,t3,or_old
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x0016B740                # the game's "find the object with this number"
    addiu a0,zero,@ID@
    beq v0,zero,or_done           # the boss is not there: again at the next step
    ld a1,8(sp)                   # the victim = player 1's hero
    lui t7,0x000F
    addiu t3,zero,1
    sw t3,0x1EF0(t7)
    sw v0,0x1EF4(t7)
    addiu a0,v0,320               # the captor's motion part
    addiu a2,zero,@MOVE@
    mtc1 zero,f12
    jal 0x00180378                # the capture, with no script behind it
    nop
or_done:
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
or_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old).replace("@N@", str(count)).replace("@ID@", str(boss)).replace("@MOVE@", str(move))
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1EF0
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_orphan.py %s): for tests only." % " ".join(sys.argv[3:])]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["or_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "one stray capture (move %02X) by object %04X on player 1's hero at session frame %d (%d words; the old method %08X)" % (move, boss, frame, len(code), old))
