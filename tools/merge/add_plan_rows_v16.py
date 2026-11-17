"""One-off: KH2-COOP-PLAN.md, TEST BUILD 23 (tenth round, 2026-11-16; docs/STATE.md part 130): a new row 55. The file keeps
its CRLF line ends. Run once:  python -I tools/merge/add_plan_rows_v16.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_bytes().decode("utf-8")
if "| 55 | TEST BUILD 23" in t:
    raise SystemExit("already there")
lines = t.split("\r\n")
ROW55 = ("| 55 | TEST BUILD 23 (tenth round, 2026-11-16) | Build 22 + ONE FIX: glue 66's shots' table (the Gummi flight's \"which "
         "ship fired\" byte per cannon shot, 4 KB) moved from 0x000EE800 to 0x000DF000 (`tools\\merge\\edit_merge_v7_gqtable.py`; "
         "patches\\merged-v17 differs from merged-v16 in two words). Build 22 had placed glues 72 to 75 (333 words) inside that table, so "
         "a cannon shot could change a byte of their code until the next frame; the builder now checks the table and the own pictures "
         "at the END of a build. Package 9d40745f3298 (disc TEST v5 unchanged), rehearsal p28 clean. Also verified: Load Game from the "
         "title screen gives player 2 his saved Drive gauge; a Drive Form through five doors in a row. Details: docs\\STATE.md, "
         "section \"Tenth round\", part 130. |")
out, done = [], False
for l in lines:
    out.append(l)
    if l.startswith("| 54 |"):
        out.append(ROW55)
        done = True
assert done
p.write_bytes("\r\n".join(out).encode("utf-8"))
print("plan: row 55 added")
