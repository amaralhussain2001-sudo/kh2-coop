"""One-off: KH2-COOP-PLAN.md, TEST BUILD 24 (tenth round, 2026-11-16; docs/STATE.md parts 134 to 137): a new row 56 and a note at the
end of row 35. The file keeps its CRLF line ends. Run once:  python -I tools/merge/add_plan_rows_v17.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_bytes().decode("utf-8")
if "| 56 | TEST BUILD 24" in t:
    raise SystemExit("already there")
lines = t.split("\r\n")
ROW56 = ("| 56 | TEST BUILD 24 (tenth round, 2026-11-16) | Build 23 + glue 78 (`--gummitag`): in the Gummi Ship the points of weapons "
         "other than the cannons go to the ship that fired (the firing ship is written into the weapon's hit values, which every shot "
         "copies; cannons keep glue 66's table). Package 98dad91e6e9e (disc TEST v5 unchanged), regression b33 clean, 40 fights rs8 as "
         "build 22, rehearsal p30 clean; the user's copy Desktop\\PS2-ONLINE-KH2-TEST-b24. Also answered: doors in a Drive Form keep a "
         "Keyblade copy per door in the ORIGINAL game too (one-hero disc), 16 doors never ran out of memory; the nine boss scripts in "
         "no room file: three unused by the game, six met in their makers' fights with two heroes. Details: docs\\STATE.md, section "
         "\"Tenth round\", parts 134 to 137. |")
ADD = {"| 35 |": (" **Build 24 (2026-11-16): glue 78 gives the points of the other weapons to the ship that fired (glue 77 stays out; "
                  "its crash came from lying inside glue 66's old table, part 130).** |")}
done, out = set(), []
for l in lines:
    for k, text in ADD.items():
        if l.startswith(k) and k not in done:
            assert l.rstrip().endswith("|")
            l = l.rstrip()[:-1].rstrip() + text
            done.add(k)
    out.append(l)
    if l.startswith("| 55 |"):
        out.append(ROW56)
        done.add("56")
assert done == set(ADD) | {"56"}, done
p.write_bytes("\r\n".join(out).encode("utf-8"))
print("plan: row 56 added, row 35 noted")
