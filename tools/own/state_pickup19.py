"""One-off helper for docs/STATE.md after test build 19: the head line of "PICK UP HERE", one number in its first
paragraph, and the block "WHAT THE USER HAS NOW" are written anew (the block's new text comes from a file).
The block "STILL OWED" is done by state_pickup.py owed <file>.
  python -I tools/own/state_pickup19.py <hasNowFile>
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = P.read_text(encoding="utf-8")
head_old = "## PICK UP HERE (rewritten 2026-11-15: BUILD 18 IS IN `dist\\`; next jobs:"
head_new = "## PICK UP HERE (rewritten 2026-11-15: BUILD 19 IS IN `dist\\`; next jobs:"
assert t.count(head_old) == 1, t.count(head_old)
t = t.replace(head_old, head_new)
a = t.index(head_new)
for old, new in (("(parts 1 to 84: every result of this round with", "(parts 1 to 86: every result of this round with"),
                 ("`..\\KH2-COOP-PLAN.md` (rows 9, 35 to 37 and 39 to 50)", "`..\\KH2-COOP-PLAN.md` (rows 9, 35 to 37 and 39 to 51)")):
    i = t.index(old, a)
    assert i - a < 1500, old
    t = t[:i] + new + t[i + len(old):]
b = t.index("\nWHAT THE USER HAS NOW (VERIFIED 2026-11-15 01:25):", a) + 1
e = t.index("\n\n", b)
assert e < t.index("\nTHE USER'S STANDING INSTRUCTIONS", a)
new_block = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").rstrip("\n")
t = t[:b] + new_block + t[e:]
P.write_text(t, encoding="utf-8")          # the default on this PC writes CRLF, as the file always was
print("STATE.md: pick-up head and 'what the user has now' are build 19's,", t.count("\n") + 1, "lines")
