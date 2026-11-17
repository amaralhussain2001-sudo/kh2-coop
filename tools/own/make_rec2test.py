"""TEST ONLY (plan row 39, feasibility): <base patch> + "THE TWIN'S UNIT SLOT READS A SECOND CHARACTER RECORD".
Never part of the real patch. The same on both PCs.

What is known (lane D): a unit slot holds a pointer to its character record at slot + 0x244; the game's "load
stats from the record" 0x001A11E0(slot, 0) reads through it. Sora's record is at 0x0032E020 (save + 0x24F0,
0x114 bytes). Today the twin's slot points at that same record.
The kit: once a step (from the player class's per-frame method, table word 0x0035241C, chained), when the twin
has a slot whose record pointer is still Sora's record:
  the first time: Sora's record is copied to record B (0x000F1E00, 0x114 bytes) and the edits given on the command
  line are written into B;  then the twin's slot gets the pointer to B and 0x001A11E0(slot, 0) loads his stats.
So after that the twin's most HP, stats and (if the game reads them through the slot) abilities come from B.
  python -I tools/own/make_rec2test.py <baseDir> <outDir> [OFF=HEXBYTES ...]
  OFF = hex offset inside the record, HEXBYTES = bytes written there (05=3C  54=9F81A081)
  Record: +0 Keyblade (short), +4 HP, +5 most HP, +6 MP, +7 most MP, +8 AP, +9 Strength, +A Magic, +B Defense,
  +F level, +10 / +11 / +12 counts of armour / accessory / item places, +14 armour, +24 accessories (HYPOTHESIS),
  +34 items, +54 abilities (shorts, 0x8000 = switched on).
Memory: routine 0x000F1C00-0x000F1CFF, record B 0x000F1E00-0x000F1F13, "B is made" 0x000F1F20, the edit list
0x000F1D00.. (the test recorders' block; NOT together with the other test kits that use it).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
AT = 0x000F1C00
EDITS = 0x000F1D00
B = 0x000F1E00
FLAG = 0x000F1F20
TABLE_WORD = 0x0035241C
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
edits = []
for a in sys.argv[3:]:
    off, hx = a.split("=")
    data = bytes.fromhex(hx)
    for i, b in enumerate(data):
        edits.append((int(off, 16) + i, b))
assert len(edits) <= 60
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
assert old is not None
SRC = """
r2_tick:
    lui t7,0x0035
    lw t6,-5816(t7)               # the engine's player: once a step
    bne a0,t6,r2_old
    nop
    lui t9,0x000F
    lw t0,0x05CC(t9)              # the twin
    beq t0,zero,r2_old
    nop
    lw t1,0x48C(t0)               # his unit slot
    beq t1,zero,r2_old
    nop
    lw t2,0x244(t1)               # its character record
    lui t3,0x0033
    addiu t3,t3,-8160             # Sora's record 0x0032E020
    bne t2,t3,r2_old              # already B (or not a Sora slot)
    nop
    lw t4,0x1F20(t9)
    bne t4,zero,r2_set            # B is made
    nop
    addiu t5,t9,0x1E00            # copy Sora's record to B
    addiu t6,t3,0x114
r2_copy:
    lw t7,0(t3)
    sw t7,0(t5)
    addiu t3,t3,4
    bne t3,t6,r2_copy
    addiu t5,t5,4
    addiu t5,t9,0x1D00            # the edit list: (offset, byte) words, offset 0xFFFF = the end
r2_edit:
    lhu t6,0(t5)
    ori t7,zero,0xFFFF
    beq t6,t7,r2_made
    nop
    lbu t7,2(t5)
    addu t6,t6,t9
    sb t7,0x1E00(t6)
    b r2_edit
    addiu t5,t5,4
r2_made:
    li t4,1
    sw t4,0x1F20(t9)
r2_set:
    addiu t5,t9,0x1E00
    sw t5,0x244(t1)
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    move a0,t1
    jal 0x001A11E0                # load the slot's stats from its record
    move a1,zero
    ld ra,0(sp)
    ld a0,8(sp)
    addiu sp,sp,16
r2_old:
    j @OLD@
    nop
""".replace("@OLD@", "0x%08X" % old)
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= EDITS, len(code)
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_rec2test.py %s): a second character record for the twin, for tests only."
       % " ".join(sys.argv[3:])]
words = [(AT + 4 * i, w) for i, w in enumerate(code)]
words += [(EDITS + 4 * i, off | (b << 16)) for i, (off, b) in enumerate(edits)]
words.append((EDITS + 4 * len(edits), 0xFFFF))
for a, w in words:
    s = "%08X" % a
    assert s not in used, s
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["r2_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "(%d words, %d edit bytes; the old method %08X)" % (len(code), len(edits), old))
