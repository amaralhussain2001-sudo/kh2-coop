"""One-off: THE SEVENTY-FOURTH GLUE of tools/merge/merge_v7.py (--boxpick): PLAYER 2'S HERO PICKS UP A DROPPED ITEM BOX TOO
(tenth round; the user's words of 2026-11-16: "try to close everything now so the next patch should contain everything"; open item g).
READ (research of 2026-11-16, notes in the scratchpad's agentG folder): an item an enemy drops (a material, a fight item) is a
PRIZE_BOX object (class 0x003512E8, made by 0x001BF620(item, place)). Its step routine 0x001BF4E8 asks ONLY the engine's player
(0x0034E948 = player 1's hero): the tests 0x0019BA60(hero), no flag 0x02000000 at hero + 0x588, the box's own tests, then the touch
test 0x001A4FF8(hero, the box's place 0x0016C028(box), 0, 0); on a touch it ends with 0x001BF378(box, taker) = the game's take
(0x001A3018 where it goes, 0x001A3188 give; with the own bags (glue 71) a give counts as "the game gives": both bags get it).
Otherwise 0x001BFCA0(box) (a loop for PRIZE_BOX_NM only) and the "collect without touching" flags. So player 2's hero could never
take a dropped item; with the own bags the item still reached both bags when player 1 took it.
THE GLUE: bx_twin (0x001BF570, was jal 0x001BFCA0; its delay slot has set a0 = s1 = the box): when player 1's hero did not touch the
box, the same tests for player 2's hero (lane E's twin 0x000F05CC); on a touch the routine's own end runs with HIM as the taker
(0x001BF5D4: a0 = the box, a1 = s0 = the taker, j 0x001BF378); else the game's 0x001BFCA0 as before.
Code at 0x000EEE00 .. 0x000EEF00 (free, inside this round's room).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_boxpick.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--boxpick" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-FOURTH GLUE (built only with the option --boxpick): PLAYER 2'S HERO PICKS UP A DROPPED ITEM BOX TOO. The item box's
step routine 0x001BF4E8 asked only player 1's hero; bx_twin (at 0x001BF570) gives player 2's hero the same touch test when player
1's did not touch it, and lets him take the box with the game's own take 0x001BF378.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- seventy-fourth glue (only with --boxpick) ---------------------------------------------------------------
BX_AT = 0x000EEE00
BX_END = 0x000EEF00
BX_SRC = """
bx_twin:                          # from 0x001BF570 in the item box's step 0x001BF4E8 (was jal 0x001BFCA0): player 1's hero did not
    addiu sp,sp,-16               # touch the box (s1 = the box, s0 = player 1's hero, f20 = 0)
    sd ra,0(sp)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # player 2's hero (lane E's twin; 0 = none)
    beq t6,zero,bx_game
    nop
    sd t6,8(sp)
    jal 0x0019BA60                # the routine's first test, for him
    move a0,t6
    beq v0,zero,bx_game
    ld t6,8(sp)
    lw t7,0x588(t6)               # and its second (flag 0x02000000)
    lui t5,0x0200
    and t7,t7,t5
    bne t7,zero,bx_game
    nop
    jal 0x0016C028                # the box's place
    move a0,s1
    move a1,v0
    ld a0,8(sp)
    mtc1 zero,f12
    jal 0x001A4FF8                # does he touch it?
    mtc1 zero,f13
    beq v0,zero,bx_game
    nop
    ld s0,8(sp)                   # yes: the routine's own end, with him as the taker
    ld ra,0(sp)
    j 0x001BF5D4
    addiu sp,sp,16
bx_game:
    ld ra,0(sp)
    addiu sp,sp,16
    j 0x001BFCA0                  # as before
    move a0,s1
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--boxpick" in sys.argv:                                            # seventy-fourth glue (player 2 picks up item boxes)
        labels, n = add_code(BX_AT, BX_END, BX_SRC, {}, "player 2's hero picks up a dropped item box")
        assert game_word(0x001BF5D4) == 0x0220202D and game_word(0x001BF5EC) == 0x0806FCDE, "the item box's end is not as read"
        hook_game(0x001BF570, 0x0C06FF28, jal(labels["bx_twin"]), "an item box that player 1's hero did not touch: player 2's hero may")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
