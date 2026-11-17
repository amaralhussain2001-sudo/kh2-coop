"""One-off: KH2-COOP-PLAN.md, TEST BUILD 22 (tenth round, 2026-11-16; docs/STATE.md parts 119 to 125): a new row 54, notes at the end
of rows 35 and 39. The file keeps its CRLF line ends. Run once:  python -I tools/merge/add_plan_rows_v15.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "KH2-COOP-PLAN.md"
b = p.read_bytes()
t = b.decode("utf-8")
if "| 54 | TEST BUILD 22" in t:
    raise SystemExit("already there")
lines = t.split("\r\n")
ROW54 = ("| 54 | TEST BUILD 22 (tenth round, 2026-11-16) | Build 21 + five glues (72 to 76; `tools\\merge\\merge_v7.py ... --ownbag "
         "--drivesave --itemtarget --boxpick --formroom --setposguard`): player 2's own Drive gauge in the save (72); a target choice "
         "for Potions / Hi-Potions / Ethers / Elixirs, the PARTY window shows both heroes, the first \"Sora\" is player 1, the last player "
         "2 (73); player 2 picks up the item boxes enemies drop (74); his Drive Form files are asked for again in a new room (75); "
         "trap_effect_set_pos skips an ended effect (76, the Fortuneteller's Clear Shot). Glue 77 (Gummi points of non-cannon weapons) "
         "faulted in its tests and is NOT in the build. Package 73330f051af3 (2026-11-16 10:46; disc TEST v5 unchanged); the user "
         "tests it while the last checks run. Details: docs\\STATE.md, section \"Tenth round\", parts 119 to 125. |")
ADD = {
    "| 35 |": (" **Build 22 (2026-11-16): glue 77 (the points of weapons other than cannons to the ship that fired) was tried and is left "
               "out: it faulted in its tests (STATE part 124); those points still go to player 1's number.** |"),
    "| 39 |": (" **Build 22 (2026-11-16): a target choice for single healing items (glue 73); an item an enemy drops is picked up by "
               "either hero and goes into both bags (glue 74).** |"),
}
done = set()
out = []
for l in lines:
    for k, text in ADD.items():
        if l.startswith(k) and k not in done:
            assert l.rstrip().endswith("|")
            l = l.rstrip()[:-1].rstrip() + text
            done.add(k)
    out.append(l)
    if l.startswith("| 53 |"):
        out.append(ROW54)
        done.add("54")
assert done == set(ADD) | {"54"}, done
p.write_bytes("\r\n".join(out).encode("utf-8"))
print("plan: row 54 added, rows 35 and 39 noted")
