"""TEST ONLY (ninth round, job 3): <base patch> + ONE "LET HIM GO" AT ONE MOMENT, in one of several ways, on player
1's hero or on the twin. The question: which calls free a hero from a captured motion that no script ends (the
mirror hero left behind at the Dark Thorn stayed in FC although the glue called "no motion" and "go idle").
The same on both PCs. Never part of the real patch.
  python -I tools/own/make_release_test.py <baseDir> <outDir> <sessionFrame> <variant> [p1|p2]
  variant 1: "no motion" 0x0017EFA0(hero + 320, 0), then "go idle" 0x0016BD60(hero, 0)      (the glues' way)
  variant 2: "go idle" alone                                                                (the script call "idle")
  variant 3: detach 0x001C0E60(hero) when he is attached, then variant 1
  variant 4: the held bit (hero + 0x160, 0x4000) and the captor word (hero + 0x240) cleared, then variant 1
  variant 5: "clear the motion queue and no motion" 0x0017F430(hero + 320, 0), the bit and the word cleared, "go idle"
  variant 6: variant 4, then the hero's action word (hero + 0x154) set to 0
  variant 7: "blow" 0x00186888(hero, a zero vector)                                        (the script call "blow")
  variant 8: detach when he is attached, then variant 7
  variant 9: the bits 0x4000 / 0x0080 / 0x0002 of hero + 0x160, the captor word and hero + 0x15C cleared, then variant 1
  variant 10: variant 9, then the action word set to 0
  variant 11: the same clearing, then "go idle" alone
  variant 12: "motion start 0", the clearing of variant 9, "go idle"
  variant 13: "motion start 16", then "blow" (the Dark Thorn's own throw)
  variant 14: the clearing of variant 9, then variant 13
How: the player class's per-frame method (table word 0x0035241C, chained after whatever is there): the first time
that hero is stepped at or past the frame.
Memory: 0x000F1E00-0x000F1EEF, "done" 0x000F1EF0 (the test block, as make_orphan.py: never both, and not with the
capture recorder)."""
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
frame, variant = int(sys.argv[3]), int(sys.argv[4])
who = sys.argv[5] if len(sys.argv) > 5 else "p1"
count = frame - 152
assert 0 < count < 0x8000 and 1 <= variant <= 14 and who in ("p1", "p2")
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
old = None
for i, l in enumerate(text):
    m = re.match(r"patch=1,EE,%08X,word,([0-9A-Fa-f]{8})" % TABLE_WORD, l)
    if m:
        old = int(m.group(1), 16)
        at_line = i
assert old is not None, "the base has no routine at the player class's per-frame word"
HERO = "    lui t3,0x0035\n    lw t3,0x2400(t3)              # player 1's hero\n" if who == "p1" else \
       "    lui t3,0x000F\n    lw t3,0x05CC(t3)              # the twin\n"
CLEAR = """    ld a0,8(sp)
    lw t2,0x160(a0)
    addiu t1,zero,-16385          # not 0x4000
    and t2,t2,t1
    sw t2,0x160(a0)               # the held bit
    sw zero,0x240(a0)             # the captor word
"""
NOMOTION = """    ld a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion"
    move a1,zero
"""
IDLE = """    ld a0,8(sp)
    jal 0x0016BD60                # "go idle"
    move a1,zero
"""
DETACH = """    jal 0x001C0CD8                # is he attached
    ld a0,8(sp)
    beq v0,zero,rt_na
    nop
    jal 0x001C0E60                # detach
    ld a0,8(sp)
rt_na:
"""
QUEUE = """    ld a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017F430                # clear the motion queue, then "no motion"
    move a1,zero
"""
BLOW = """    sd zero,16(sp)
    sd zero,24(sp)
    ld a0,8(sp)
    jal 0x00186888                # "blow" (the script call (1,129)): he is thrown off, here with no speed
    addiu a1,sp,16
"""
CLEAR2 = """    ld a0,8(sp)
    lw t2,0x160(a0)
    addiu t1,zero,-16515          # not 0x4082
    and t2,t2,t1
    sw t2,0x160(a0)               # the bits 0x4000, 0x0080, 0x0002
    sw zero,0x240(a0)             # the captor word
    sw zero,0x15C(a0)             # the motion part's word + 0x1C
"""
MSTART = """    ld a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017F488                # "motion start" (the script call (1,11))
    addiu a1,zero,@M@
"""
ACT0 = """    ld a0,8(sp)
    sw zero,0x154(a0)             # his action word
"""
BODY = {1: NOMOTION + IDLE, 2: IDLE, 3: DETACH + NOMOTION + IDLE, 4: CLEAR + NOMOTION + IDLE, 5: QUEUE + CLEAR + IDLE,
        6: CLEAR + NOMOTION + IDLE + ACT0, 7: BLOW, 8: DETACH + BLOW,
        9: CLEAR2 + NOMOTION + IDLE, 10: CLEAR2 + NOMOTION + IDLE + ACT0, 11: CLEAR2 + IDLE,
        12: MSTART.replace("@M@", "0") + CLEAR2 + IDLE, 13: MSTART.replace("@M@", "16") + BLOW,
        14: CLEAR2 + MSTART.replace("@M@", "16") + BLOW}[variant]
SRC = ("""
rt_tick:
    lui t7,0x000F
    lw t6,0x1EF0(t7)              # done already
    bne t6,zero,rt_old
    lui t5,0x0035
    lw t4,-11076(t5)              # 0x0034D4BC: the game's frame counter
    addiu t3,zero,@N@
    slt t3,t4,t3
    bne t3,zero,rt_old            # not yet
    nop
""" + HERO + """    bne a0,t3,rt_old              # only in that hero's own step
    nop
    addiu t3,zero,1
    sw t3,0x1EF0(t7)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
""" + BODY + """    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
rt_old:
    j @OLD@
    nop
""").replace("@OLD@", "0x%08X" % old).replace("@N@", str(count))
code, labels = assemble(AT, SRC, {})
code = [w if isinstance(w, int) else w[1] for w in code]
assert AT + 4 * len(code) <= 0x000F1EF0
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST KIT (tools/own/make_release_test.py %s): for tests only." % " ".join(sys.argv[3:])]
for i, w in enumerate(code):
    a = "%08X" % (AT + 4 * i)
    assert a not in used, a
    add.append("patch=1,EE,%s,word,%08X" % (a, w))
text[at_line] = "patch=1,EE,%08X,word,%08X" % (TABLE_WORD, labels["rt_tick"])
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print(out, "release variant %d on %s at session frame %d (%d words; the old method %08X)" % (variant, who, frame, len(code), old))
