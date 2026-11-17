"""One-off (after a review, STATE part 131): the read-me of build 23 says exactly what the door tests showed, not more.
"stays right" becomes what ran: five doors in a row with one hero's form (player 1's or player 2's) and four with both heroes in a
form, without a fault. Only the read-me changes (the package id changes with it).
  python -I tools/package/edit_package_v23b.py          (run ONCE; it refuses a second run)
"""
import pathlib

README = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
OLD = """    ALSO TESTED NOW, NOTHING TO CHANGE: Load Game FROM THE TITLE SCREEN gives player 2 his own saved Drive gauge
    (build 22 too); a Drive Form through five doors in a row stays right for player 1 and player 2."""
NEW = """    ALSO TESTED NOW: Load Game FROM THE TITLE SCREEN gives player 2 his own saved Drive gauge (build 22 too). Doors in a
    Drive Form: five doors in a row with one hero in a form (player 1's or player 2's), and four with both heroes in a
    form, ran without a fault (build 22 too)."""
t = README.read_text(encoding="utf-8")
if NEW in t:
    raise SystemExit("already done")
assert t.count(OLD) == 1, t.count(OLD)
README.write_text(t.replace(OLD, NEW), encoding="utf-8")
print("read-me: the door sentence is exact")
