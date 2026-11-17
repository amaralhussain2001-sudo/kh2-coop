"""One-off: the SIXTY-THIRD GLUE of tools/merge/merge_v7.py (--ownkey), sixth form (ninth round, part 91).
Seen in runs kdC / keC / srC (candidates v101 / v102, the Storm Rider mission mu08 79 with two different
Keyblades): THE MISSION NEVER LEFT ITS OPENING SCENE (the same still picture to the end of the run; in sync, no
fault line). With the same Keyblade for both (run srA) it runs exactly as build 19 (run srB). Found by switching
one routine off per run (`tools/own/make_reword.py`, runs srG / srH / srI): it is kb_fix: it ended and rebuilt
the twin's weapon in a step of the field WHILE THE SCENE PLAYED (the room's second hero is built first there).
Now:
 kb_after (the end of lane E's e_wrap, 0x000F03C0, was jr ra): kb_fix is called at the moment a player object
   is built and the two heroes are sorted out: while the room is built, before any scene or fight.
 kb_tick calls kb_fix only while no story event runs (0x0035037C = 0) and no event holds the camera
   (0x0033CC38 = 0).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey6.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "kb_after" in s:
    raise SystemExit("already there")
a = '''kt_go:
    addiu sp,sp,-16
    sd ra,0(sp)
    jal kb_fix
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    j TICK_NEXT
    move a0,zero
'''
assert s.count(a) == 1
b = '''kt_go:
    lui t7,0x0035
    lw t6,0x037C(t7)              # a story event runs: the twin's weapon is not touched now
    bne t6,zero,kt_x
    lui t7,0x0034
    lw t6,-13256(t7)              # 0x0033CC38: an event holds the camera
    bne t6,zero,kt_x
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal kb_fix
    nop
    ld ra,0(sp)
    addiu sp,sp,16
kt_x:
    j TICK_NEXT
    move a0,zero

kb_after:                         # jump at the end of lane E's e_wrap (0x000F03C0, was jr ra): a player object is built, the two heroes are sorted out. v0 = the new object
    addiu sp,sp,-32
    sd ra,0(sp)
    sd v0,8(sp)
    jal kb_fix                    # the twin gets HIS Keyblade now, while the room is built
    nop
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
'''
s = s.replace(a, b)
a = '''        hook_base(0x000F0344, jal(0x00179FD0), jal(labels["kb_fact"]), "lane E's call of the player factory: noted while it runs")
'''
assert s.count(a) == 1
b = a + '''        hook_base(0x000F03C0, 0x03E00008, jmp2(labels["kb_after"]), "the end of lane E's e_wrap: the twin gets his Keyblade as soon as the heroes are sorted out")
'''
s = s.replace(a, b)
a = "weapon and files only; kb_fix (each step): the twin's first hand gets HIS Keyblade as soon as its files are loaded"
assert s.count(a) == 1
s = s.replace(a, "weapon and files only; kb_fix (when a player object is built, kb_after at 0x000F03C0; and each step while no scene" + NL + "plays): the twin's first hand gets HIS Keyblade as soon as its files are loaded")
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
