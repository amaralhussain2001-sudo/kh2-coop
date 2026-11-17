"""One-off: tools/merge/merge_v7.py gets the FORTIETH GLUE (a helper that the TWIN'S Drive Form uses stays away
when a room is built). The record of the edit; run once:  python -I tools/merge/edit_merge_v7_helperform.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "hf_either" in s:
    raise SystemExit("already there")
a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FORTIETH GLUE (option --no-helperform leaves it out): A HELPER WHOM THE TWIN'S DRIVE FORM USES STAYS AWAY WHEN A
ROOM IS BUILT (register G5, "Final Form after a room change"; plan row 44).
What was there (run ffd3, build 12, picture p2_f006260): player 2 goes through a door in Final Form (which uses
Donald and Goofy). In the new room he is still in Final Form, and BOTH HELPERS STAND THERE AGAIN. Read in the
program: when a helper is put into a room, routine 0x0017E4xx asks 0x001C9958(form, the helper's kind) with the
save's form byte (0x0032F054 = player 1's form) and sends him away when that form uses him. The twin's own form
number (0x000F47E8, ninth glue) is not asked.
Now the call at 0x0017E488 goes through hf_either: the game's question for player 1's form, then, when the answer
is no and there is a twin, the same question for the twin's form.

'''
s = s.replace(a, hdr + a)
b = "[--no-thinkheld]"
assert s.count(b) == 1
s = s.replace(b, b + " [--no-helperform]")
i = s.index("def main():")
src = '''# ---- fortieth glue -----------------------------------------------------------------------------------------
HF_AT = 0x000E89A0
HF_END = 0x000E89E0
HF_SRC = """
hf_either:                        # from 0x0017E488 (was jal 0x001C9958). a0 = player 1's form, a1 = the helper's kind
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a1,8(sp)
    jal 0x001C9958                # does player 1's form use this helper?
    nop
    bne v0,zero,hf_out
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,hf_out
    nop
    lbu a0,0x47E8(t7)             # the twin's own form (ninth glue)
    jal 0x001C9958                # does the twin's?
    ld a1,8(sp)
hf_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
HF_HOOK = (0x0017E488, 0x0C072656)                 # jal 0x001C9958


'''
s = s[:i] + src + s[i:]
c = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(c) == 1
step = '''    if "--no-helperform" not in sys.argv:                                  # fortieth glue
        labels, n = add_code(HF_AT, HF_END, HF_SRC, {}, "a helper whom the twin's Drive Form uses stays away when a room is built")
        a, w0 = HF_HOOK
        hook_game(a, w0, jal(labels["hf_either"]), "a helper enters a room: is he used by player 1's form or by the twin's")
        n_glue += n + 1

'''
s = s.replace(c, step + c)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
