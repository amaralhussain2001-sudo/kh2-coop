"""One-off: tools/merge/merge_v7.py gets the FORTY-SECOND GLUE (when one of two Drive Forms ends, the helpers that
the OTHER hero's form still uses do not come back). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_helperback.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hb_back" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTY-SECOND GLUE (option --no-helperback leaves it out): WHEN ONE OF TWO DRIVE FORMS ENDS, THE HELPERS THAT THE
OTHER HERO'S FORM USES STAY AWAY (plan row 44).
What was there (run tf5, candidate v47, picture p1_f006700): player 1 is in Valor (Goofy), player 2 in Wisdom
(Donald). Player 2 reverts, and BOTH helpers stand there again while player 1 is still in Valor. Read in the
program: the form record's cleanup (0x001B6450 / 0x001B6518) calls 0x001C9B90 for a revert, which brings back
EVERY helper on the "away" list (0x01D49980, count 0x00351F30).
Now both calls go through hb_back: the game's call, then, while there is a twin, the game's own "send this form's
helpers away" (0x001C9860(form)) once for each hero who is still in a form. (The hero who reverted has form 0 by
then: his number is cleared when the revert is asked for.)

'''
s = s.replace(a, hdr + a)
b = "[--no-formbase]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-helperback]")
i = s.index("def main():")
src = '''# ---- forty-second glue -------------------------------------------------------------------------------------
HB_AT = 0x000E8D80
HB_END = 0x000E8E00
HB_SRC = """
hb_back:                          # from 0x001B649C and 0x001B6564 (was jal 0x001C9B90): a revert's cleanup
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001C9B90                # the game's call: every helper who was away comes back
    nop
    lui t5,0x000F
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,hb_out            # one hero: as the game
    nop
    lui t7,0x0033
    lbu a0,-4012(t7)              # player 1's form (the save's byte 0x0032F054)
    addiu t6,a0,-1
    sltiu t6,t6,6
    beq t6,zero,hb_two
    nop
    jal 0x001C9860                # he is still in a form: its helpers go away again
    nop
hb_two:
    lui t5,0x000F
    lbu a0,0x47E8(t5)             # the twin's form
    addiu t6,a0,-1
    sltiu t6,t6,6
    beq t6,zero,hb_out
    nop
    jal 0x001C9860
    nop
hb_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
HB_HOOKS = (
    (0x001B649C, 0x0C0726E4, "a revert's cleanup brings the helpers back: not those the other hero's form uses"),
    (0x001B6564, 0x0C0726E4, "(the second cleanup routine, the same call)"),
)


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-helperback" not in sys.argv:                                  # forty-second glue
        labels, n = add_code(HB_AT, HB_END, HB_SRC, {}, "when one of two Drive Forms ends, the other form's helpers stay away")
        for a, w0, what in HB_HOOKS:
            hook_game(a, w0, jal(labels["hb_back"]), what)
        n_glue += n + len(HB_HOOKS)

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
