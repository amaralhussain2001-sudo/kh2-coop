"""One-off: tools/merge/merge_v7.py gets the SIXTY-FOURTH GLUE (built only with --bindname): AN OBJECT WHOSE FILES
HAVE ANOTHER NUMBER THAN THE OBJECT WAS GIVEN IS BOUND TO THEM BY THEIR NAME (register F8; ninth round, part 92).
What was there (found with the recorder tools/own/make_rec_bar0.py and the probe tools/own/bind_probe.py, runs
f8B / f8D): an object binds to its model file and its effect file with 0x001A9218: 0x001708F8(name, number).
The game gives every object the number its files were asked for with. With two heroes that does not always
hold: player 2's Drive Form body in a NEW ROOM has the number 29000 (his form files are kept from the room
before, nobody asks for them again), so the form's second Keyblade is bound with 29002 and finds nothing: its
model and effect pointers stay 0, and the object's script start (0x00169F98) then reads address 4: the ONE
fault line "pc 0x00168B38, address 4" of register F8 (in build 12 too). The Keyblade is drawn all the same.
bn_find (the two calls at 0x001A9238 and 0x001A9288, were jal 0x001708F8): when the file is not found with the
number (the answer is 0), it is looked up again by its name alone.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_bindname.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "bn_find" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''SIXTY-FOURTH GLUE (built only with the option --bindname): AN OBJECT IS BOUND TO ITS FILES BY THEIR NAME WHEN THE
NUMBER DOES NOT FIT (register F8). An object binds to its model and effect file with 0x001A9218 ->
0x001708F8(name, number). Player 2's Drive Form body in a new room has the number of files that nobody asked for
again (29000), so the form's second Keyblade found nothing, its file pointers stayed 0 and its script start read
address 4 (one fault line). bn_find (the calls at 0x001A9238 and 0x001A9288): not found with the number: by name.

'''
s = s.replace(a, hdr + a)
b = " [--ownkey]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--bindname]")

i = s.index("def main():")
src = '''# ---- sixty-fourth glue (only with --bindname) ---------------------------------------------------------------
BN_AT = 0x000ECF00
BN_END = 0x000ECF40
BN_SRC = """
bn_find:                          # calls at 0x001A9238 / 0x001A9288 (were jal 0x001708F8). a0 = the file's name, a1 = the number
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x001708F8
    nop
    bne v0,zero,bn_out
    nop
    ld a0,8(sp)
    jal 0x001708F8                # not there with this number: by its name alone
    addiu a1,zero,-1
bn_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--bindname" in sys.argv:                                           # sixty-fourth glue (an object is bound to its files by name when the number does not fit)
        labels, n = add_code(BN_AT, BN_END, BN_SRC, {}, "an object is bound to its files by their name when the number does not fit")
        hook_game(0x001A9238, jal(0x001708F8), jal(labels["bn_find"]), "an object binds to its model file: by name when the number finds nothing")
        hook_game(0x001A9288, jal(0x001708F8), jal(labels["bn_find"]), "an object binds to its effect file: by name when the number finds nothing")
        n_glue += n + 2

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
