"""One-off helper for docs/STATE.md after test build 16: the head line of "PICK UP HERE", two numbers in its first
paragraph, and the block "WHAT THE USER HAS NOW" are written anew (the block's new text comes from a file).
The block "STILL OWED" is done by state_pickup.py owed <file>.
  python -I tools/own/state_pickup16.py <hasNowFile>
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = P.read_text(encoding="utf-8")
head_old = "## PICK UP HERE (rewritten 2026-11-14 13:30: BUILD 15 IS IN `dist\\`; next jobs: plan row 9's second half, then the five vehicle items)"
head_new = "## PICK UP HERE (rewritten 2026-11-14 19:20: BUILD 16 IS IN `dist\\`; next jobs: the three one-hero small games, the other bosses of plan row 9, the rest of row 39)"
assert t.count(head_old) == 1, t.count(head_old)
t = t.replace(head_old, head_new)
a = t.index(head_new)
for old, new in (("(parts 1 to 60: every result of this round with", "(parts 1 to 73: every result of this round with"),
                 ("`..\\KH2-COOP-PLAN.md` (rows 39 to 48)", "`..\\KH2-COOP-PLAN.md` (rows 9, 35, 36 and 39 to 49)")):
    i = t.index(old, a)
    assert i - a < 1500, old
    t = t[:i] + new + t[i + len(old):]
b = t.index("\nWHAT THE USER HAS NOW (VERIFIED 2026-11-14 13:28):", a) + 1
e = t.index("\n\n", b)
assert e < t.index("\nTHE USER'S STANDING INSTRUCTIONS", a)
new_block = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").rstrip("\n")
t = t[:b] + new_block + t[e:]
P.write_text(t, encoding="utf-8")          # the default on this PC writes CRLF, as the file always was
print("STATE.md: pick-up head and 'what the user has now' are build 16's,", t.count("\n") + 1, "lines")
