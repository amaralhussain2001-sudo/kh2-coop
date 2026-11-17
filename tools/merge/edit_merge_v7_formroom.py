"""One-off: THE SEVENTY-FIFTH GLUE of tools/merge/merge_v7.py (--formroom): IN A NEW ROOM PLAYER 2'S DRIVE FORM FILES ARE ASKED FOR
AGAIN, AS PLAYER 1'S ARE (tenth round; the user's words of 2026-11-16: "try to close everything now"; open item e, part 92).
READ (research of 2026-11-16, draft in the scratchpad's agentE folder; the key words checked by me): a new room's files are asked
for by 0x00169178 (from the map loader at 0x00104C38); for the PLAYER placeholder (object 566) 0x0016ED50 asks for the body, then,
when the save byte 0x0032F054 (player 1's form) is not 0, ends with "j 0x0016EF28" at 0x0016EEE4 = 0x0016EB48(0x001D1438(form),
5000, 4, 7); when it is 0 it returns by the branch at 0x0016EED0. Before that the old room's files were marked "may be thrown out"
(0x00170018: 5000 -> 29000, 5001 / 5002 -> 15001 / 15002). Nobody asked for player 2's form files again (his form 0x000F47E8),
so in the new room they kept the numbers of 10000 and more: they are laid out last and are the first to be thrown out when the
pool has no room (seen as numbers in run f8D of part 92; the throw-out itself was never seen).
THE GLUE: 0x0016EED0 (the "no form" return) becomes a nop, so both cases reach 0x0016EEE4, whose jump now goes to fr_room (a0 =
player 1's form, the caller's frame already given back): player 1's form as before (0x0016EF28) when it is not 0, then, when two
heroes have been built once (0x000F47EC) and player 2 is in a form other than player 1's, his form's files with the game's own
request 0x0016EB48(0x001D1438(form), base, 4, 7), base = his number base of the forty-first glue (0x000E7C08; 0 = 5000). A file
found by name with a number of 10000 or more takes the new number (0x00170400), so his files get back the numbers they had.
Code at 0x000EEF00 .. 0x000EEF80 (free, inside this round's room).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_formroom.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--formroom" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-FIFTH GLUE (built only with the option --formroom): IN A NEW ROOM PLAYER 2'S DRIVE FORM FILES ARE ASKED FOR AGAIN, AS
PLAYER 1'S. The room's request for the player placeholder (0x0016ED50) ends in fr_room (jump at 0x0016EEE4; the "no form" return
at 0x0016EED0 is a nop): player 1's form as before, then player 2's form with his own number base (forty-first glue), so his
files are not left as files "that may be thrown out".

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- seventy-fifth glue (only with --formroom) ---------------------------------------------------------------
FR_AT = 0x000EEF00
FR_END = 0x000EEF80
FR_SRC = """
fr_room:                          # from 0x0016EEE4 (was j 0x0016EF28) in 0x0016ED50: a0 = player 1's form (0 = none); the caller's
    addiu sp,sp,-16               # frame is already given back, ra = its caller's
    sd ra,0(sp)
    beq a0,zero,fr_twin
    sd a0,8(sp)
    jal 0x0016EF28                # player 1's form, as before (number 5000)
    nop
fr_twin:
    lui t5,0x000F
    lw t4,0x47EC(t5)              # two heroes built in one room once
    beq t4,zero,fr_out
    lbu a0,0x47E8(t5)             # player 2's form (0 = none)
    beq a0,zero,fr_out
    ld t6,8(sp)
    beq a0,t6,fr_out              # the same form as player 1's: asked for already
    lui t3,0x000E
    lw a1,0x7C08(t3)              # his number base (forty-first glue; 0 = 5000)
    bne a1,zero,fr_ask
    nop
    addiu a1,zero,5000
fr_ask:
    sd a1,8(sp)
    jal 0x001D1438                # the form's object number
    nop
    move a0,v0
    ld a1,8(sp)
    addiu a2,zero,4
    jal 0x0016EB48                # the game's own request
    addiu a3,zero,7
fr_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--formroom" in sys.argv:                                           # seventy-fifth glue (player 2's form files in a new room)
        assert "--no-formbase" not in sys.argv, "--formroom needs the forty-first glue's number base (0x000E7C08)"
        labels, n = add_code(FR_AT, FR_END, FR_SRC, {}, "player 2's form files are asked for in a new room")
        hook_game(0x0016EED0, 0x1080FFD1, 0x00000000, "the room's form request: no early return when player 1 is in no form")
        hook_game(0x0016EEE4, 0x0805BBCA, (2 << 26) | ((labels["fr_room"] >> 2) & 0x3FFFFFF), "the room's form request: player 2's form too")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
