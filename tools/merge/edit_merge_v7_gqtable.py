"""ONE-OFF EDIT (tenth round, 2026-11-16; RUN ONCE, never again): GLUE 66's SHOTS' TABLE MOVES TO 0x000DF000.

What was wrong (READ in merge_v7.py, found by the Gummi research agent): gq_init writes one byte per cannon shot (the ship
that fired it) at 0x000EE800 + ((shot >> 4) & 0xFFF), so the table spans 0x000EE800 .. 0x000EF7FF. Build 22 placed glues
72 (0x000EE800), 73 (0x000EEA00), 74 (0x000EEE00) and 75 (0x000EEF00) there: 333 patch words. A cannon shot whose index
falls on that code changes one byte of it until the next vsync rewrites the patch, and gq_hit then reads a code byte as
"the ship that fired". Glue 77 (0x000EF000, left out of build 22) crashed that way: lw t3,0x40(a0) at 0x000EF170 became
lw t3,1(a0). The builder's clash check of glue 66 ran in the middle of the build (before glues 71 .. 75) and only covered
the own pictures, not the table.

The fix: every "ori t3,t7,0xE800" (t7 = 0x000E0000) becomes "addiu t3,t7,-4096" = 0x000DF000 (same length, no other word
moves). 0x000C0000 .. 0x000DFFFF holds no patch word in build 22 and was all zero in the merge_v7 header's zero check
(0x00096000 .. 0x000EFFFF). And a check at the END of the build: no patch word in the table nor in the own pictures.
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
F = ROOT / "tools" / "merge" / "merge_v7.py"
BAK = ROOT / "local" / "merge_v7-before-gqtable.py"

src = F.read_text(encoding="utf-8")
assert "GQ_TAB = 0x000DF000" not in src, "already run"
assert not BAK.exists(), "backup exists: already run?"
shutil.copyfile(F, BAK)

OLD = "ori t3,t7,0xE800"
NEW = "addiu t3,t7,-4096"
assert src.count(OLD) == 6, src.count(OLD)
src = src.replace(OLD, NEW)

A = 'GQ_OWN_AT = 0x000EA210 '
assert src.count(A) == 1
src = src.replace(A, ('GQ_TAB = 0x000DF000                                # the shots\' table (ship 1 / 2 per shot, '
                      '4 KB; was 0x000EE800 .. build 22, where glues 72 .. 75 lie)\n') + A)

B = '    body = ["patch=1,EE,%08X,word,%08X" % (a, words[a]) for a in order]\n'
assert src.count(B) == 1
src = src.replace(B, (
    '    if "--ship2score" in sys.argv:                                         # checked at the END (later glues too)\n'
    '        assert 0x000E0000 - 4096 == GQ_TAB\n'
    '        tab = [a for a in words if GQ_TAB <= a < GQ_TAB + 0x1000]\n'
    '        assert not tab, "the sixty-sixth glue\'s shots\' table lies on patch words: %08X .." % min(tab)\n'
    '        clash = [a for a in gq_own if a in words]\n'
    '        assert not clash, "the sixty-sixth glue\'s own pictures lie on patch words: %08X .." % clash[0]\n') + B)

F.write_text(src, encoding="utf-8")
print("done: 6 table uses moved to 0x000DF000, end check added; backup", BAK)
