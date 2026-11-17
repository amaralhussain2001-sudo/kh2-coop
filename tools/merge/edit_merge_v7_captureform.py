"""One-off: tools/merge/merge_v7.py gets the FORTY-FOURTH GLUE (Luxord's "turn the hero into a card / a die" takes
the hero his trick is played on, and brings THAT hero back). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_captureform.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "cf_who" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-FOURTH GLUE (option --no-captureform leaves it out): A BOSS'S "CAPTURE FORM" (LUXORD'S CARD AND DIE) TAKES
THE HERO THE TRICK IS PLAYED ON (job 10 of the eighth round, fault F11).
What was there (runs luxc / lux2, in build 12 too): in Luxord's story fight player 2's hero is pulled into a
paired move at the start (FC, then FE) and stays in FE for the whole fight. Read in the program: the script calls
trap_player_capture_form (0x001741E0 -> 0x001B6BD8(hero, object)) and trap_player_capture_form_end (0x00174210 ->
0x001B6C20(hero)) take the hero from 0x001D14A0 = the last-built hero object (0x00352400), which is always player
1's hero; the paired moves of the same trick take "the player" of the script (the nearer hero, twelfth glue). So
the twin was held, PLAYER 1'S hero was turned into the card, and the twin's hold never ended. And 0x001B6C20
gives the body back in "the current form" of the save data, which is player 1's number.
Now:
(1) cf_who (the call at 0x001741EC): while there is a twin, the hero is the one who is HELD in a paired move when
    only one of the two is; otherwise the engine's player (the script's own "player"); no twin: as the game.
(2) cf_end_who (the call at 0x00174218): the hero who IS in a capture form (body form 12): the twin when only he
    is, the engine's player when both are; otherwise as the game.
(3) cf_form (the jump at 0x001B6C54): when the body that comes back is the twin's, the form number is his own
    (0x000F47E8).

'''
s = s.replace(a, hdr + a)
b = "[--no-heroscript]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-captureform]")
i = s.index("def main():")
src = '''# ---- forty-fourth glue -------------------------------------------------------------------------------------
CF_AT = 0x000E9180
CF_END = 0x000E92A0
CF_SRC = """
cf_who:                           # from 0x001741EC (was jal 0x001D14A0): which hero is turned into the card / the die
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    lui t5,0x0035
    beq t6,zero,cf_game           # one hero: as the game
    lw t4,0x2400(t5)              # player 1's hero (the last-built hero object)
    beq t4,zero,cf_game
    nop
    lw t3,0x160(t6)
    andi t3,t3,0x4000             # is the twin held in a paired move?
    lw t2,0x160(t4)
    andi t2,t2,0x4000             # is player 1's hero?
    beq t3,t2,cf_eng              # both or none: the script's own player
    nop
    bne t3,zero,cf_tw             # only the twin
    nop
    jr ra                         # only player 1's hero
    move v0,t4
cf_tw:
    jr ra
    move v0,t6
cf_eng:
    lw v0,-5816(t5)               # the engine's player
    bne v0,zero,cf_ret
    nop
cf_game:
    lui t5,0x0035
    lw v0,0x2400(t5)
cf_ret:
    jr ra
    nop
cf_end_who:                       # from 0x00174218 (was jal 0x001D14A0): which hero comes back from the card / the die
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lui t5,0x0035
    beq t6,zero,cf_game
    lw t4,0x2400(t5)
    beq t4,zero,cf_game
    nop
    lw t3,0xB50(t6)
    addiu t3,t3,-12
    bne t3,zero,cf_game           # the twin is in no capture form: the game's hero
    nop
    lw t2,0xB50(t4)
    addiu t2,t2,-12
    bne t2,zero,cf_tw             # only the twin is
    nop
    b cf_eng                      # both are: the script's own player
    nop
cf_form:                          # from 0x001B6C54 (was j 0x001B6298; a1 = the body that comes back, a2 = the form
    lui t7,0x000F                 # number of the save data = player 1's)
    lw t6,0x05CC(t7)
    bne a1,t6,cf_go
    nop
    lbu a2,0x47E8(t7)             # the twin's own form number
cf_go:
    j 0x001B6298
    nop
"""
CF_HOOKS = (
    (0x001741EC, 0x0C074528, "jal", "cf_who", "trap_player_capture_form: the hero the trick is played on"),
    (0x00174218, 0x0C074528, "jal", "cf_end_who", "trap_player_capture_form_end: the hero who is in the capture form"),
    (0x001B6C54, 0x0806D8A6, "j", "cf_form", "a body comes back from a capture form: the twin in his own form number"),
)


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-captureform" not in sys.argv:                                 # forty-fourth glue
        labels, n = add_code(CF_AT, CF_END, CF_SRC, {}, "a boss's capture form takes the hero the trick is played on")
        for a, w0, kind, label, what in CF_HOOKS:
            hook_game(a, w0, ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF), what)
        n_glue += n + len(CF_HOOKS)

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
