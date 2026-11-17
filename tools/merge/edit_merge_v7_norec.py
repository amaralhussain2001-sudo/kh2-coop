"""One-off: tools/merge/merge_v7.py gets the FIFTY-THIRD GLUE (built only with --norec; an experiment for the toy
cannon of the vehicle items): THE COMMAND MENU'S ITEM COUNT FOR A HERO WITHOUT A CHARACTER RECORD.
What was there (seventh round, part 7e, test sp-nm63 on the disc with a second toy cannon): 50 fault lines at pc
0x001BE9DC. Read: the routine 0x001BE9A0 (the command menu counts the hero's item places) asks 0x00177850 for the
hero's character record and reads the place count at record + 0x12. The toy cannon (object 0x03C8, kind PLAYER,
status 0, its own class 0x001CF698) has no record; for the engine's player the game never gets there, for a
second cannon as player 2's "hero" it does.
gn_cnt (the jump at 0x001BE9DC): no record = no item places (the routine's own way out for a count of 0).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_norec.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gn_cnt" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-THIRD GLUE (built only with the option --norec; an experiment): A HERO WITHOUT A CHARACTER RECORD HAS NO
ITEM PLACES. The command menu's count of the hero's item places (0x001BE9A0) reads record + 0x12 of the record
that 0x00177850 gives; a toy cannon (object 0x03C8) as player 2's "hero" has none (0): gn_cnt (the jump at
0x001BE9DC) takes the routine's own way out for a count of 0 then.

'''
s = s.replace(a, hdr + a)
b = " [--carpet2]"
assert s.count(b) == 1
s = s.replace(b, b + " [--norec]")

i = s.index("def main():")
src = '''# ---- fifty-third glue, an experiment (only with --norec) ---------------------------------------------------
GN_AT = 0x000EB800
GN_END = 0x000EB840
GN_SRC = """
gn_cnt:                           # jump at 0x001BE9DC (was lbu t6,18(v0) / andi t7,t6,0xFF). v0 = the hero's record
    beq v0,zero,gn_zero
    nop
    lbu t6,18(v0)
    j 0x001BE9E4
    andi t7,t6,0xFF
gn_zero:
    j 0x001BEAC0                  # no record: no item places (the way out of the routine for a count of 0)
    daddu s3,v0,zero              # (the instruction in the delay slot of the routine's own branch)
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--norec" in sys.argv:                                              # fifty-third glue, an experiment (a hero without a record)
        labels, n = add_code(GN_AT, GN_END, GN_SRC, {}, "EXPERIMENT: a hero without a character record has no item places")
        hook_game(0x001BE9DC, 0x904E0012, (2 << 26) | ((labels["gn_cnt"] >> 2) & 0x3FFFFFF), "the command menu counts the hero's item places: first, is there a record")
        hook_game(0x001BE9E0, 0x31CF00FF, 0, "(andi t7,t6,0xFF is done in gn_cnt)")
        n_glue += n + 2

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
