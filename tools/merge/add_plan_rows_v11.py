"""One-off: KH2-COOP-PLAN.md after test build 19 (eighth round): a status sentence at the end of row 39 and a new
row 51. Run once:  python -I tools/merge/add_plan_rows_v11.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
t = p.read_text(encoding="utf-8")
if "| 51 |" in t:
    raise SystemExit("already there")
ADD = {
    "| 39 |": (
        " **STATUS 2026-11-15, later (test build 19): a fault of builds 15 to 18 is cured: player 2's \"Items\" list "
        "was built from his copy of the record and kept items that were gone (he could take a Potion that was "
        "not there); glue 61 makes his list from the item places as they are. The item places themselves are "
        "still one set for both (own item places: still open).** |"),
}
lines = t.split("\n")
done = set()
for i, l in enumerate(lines):
    for k, text in ADD.items():
        if l.startswith(k):
            assert l.rstrip().endswith("|") and k not in done
            lines[i] = l.rstrip()[:-1].rstrip() + text
            done.add(k)
assert done == set(ADD), done
last = max(i for i, l in enumerate(lines) if l.startswith("| 50 |"))
row51 = ("| 51 | TEST BUILD 19 (eighth round, 2026-11-15) | Build 18 + glue 61 (`tools\\merge\\merge_v7.py --ownrec --ownmenu "
         "--together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner --ownabil --holdwatch "
         "--itemsync`; the own-screen option `--cannon1view`): player 2's \"Items\" list shows the item places as "
         "they are. Builds 17 and 18 were packaged, rehearsed and never given out; build 19 is the one the user "
         "gets after build 16. The disc file is still the one of build 12. Details and evidence: docs\\STATE.md, "
         "section \"Eighth round\", parts 84 to 86. |")
lines.insert(last + 1, row51)
p.write_text("\n".join(lines), encoding="utf-8")
print("plan: row 39 has its build 19 status, row 51 is added")
