"""One-off helper for docs/STATE.md after test build 18: the head line of "PICK UP HERE", two numbers in its first
paragraph, and the block "WHAT THE USER HAS NOW" are written anew (the block's new text comes from a file).
The block "STILL OWED" is done by state_pickup.py owed <file>.
  python -I tools/own/state_pickup18.py <hasNowFile>
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = P.read_text(encoding="utf-8")
head_old = "## PICK UP HERE (rewritten 2026-11-14 19:20: BUILD 16 IS IN `dist\\`; next jobs: the three one-hero small games, the other bosses of plan row 9, the rest of row 39)"
head_new = "## PICK UP HERE (rewritten 2026-11-15: BUILD 18 IS IN `dist\\`; next jobs: the rest of plan row 39 (own Keyblade, item places, bag and wallet), the user's word on the bosses' holds, small things of the Gummi ship)"
assert t.count(head_old) == 1, t.count(head_old)
t = t.replace(head_old, head_new)
a = t.index(head_new)
for old, new in (("(parts 1 to 73: every result of this round with", "(parts 1 to 84: every result of this round with"),
                 ("`..\\KH2-COOP-PLAN.md` (rows 9, 35, 36 and 39 to 49)", "`..\\KH2-COOP-PLAN.md` (rows 9, 35 to 37 and 39 to 50)")):
    i = t.index(old, a)
    assert i - a < 1500, old
    t = t[:i] + new + t[i + len(old):]
b = t.index("\nWHAT THE USER HAS NOW (VERIFIED 2026-11-14 19:15):", a) + 1
e = t.index("\n\n", b)
assert e < t.index("\nTHE USER'S STANDING INSTRUCTIONS", a)
new_block = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").rstrip("\n")
t = t[:b] + new_block + t[e:]
old = ("  plays). Whether several at once are welcome again is his to say.")
assert t.count(old) == 1
t = t.replace(old, "  plays). 2026-11-14 23:50 HE SAID IT: \"btw i'm not going to play so you can run servel tasts or do whatever you\n"
                   "  want to finish your work faster\". So SEVERAL HIDDEN LANES AT ONCE ARE WELCOME WHILE HE DOES NOT PLAY (the\n"
                   "  sandboxes run-m, run-v3, run-v3b, run-v3c and the new run-x1 .. run-x6; `tools\\own\\reg_par8.sh` = the whole\n"
                   "  regression on eight of them in about 25 minutes). When he plays again: one hidden run at a time.")
P.write_text(t, encoding="utf-8")          # the default on this PC writes CRLF, as the file always was
print("STATE.md: pick-up head and 'what the user has now' are build 18's,", t.count("\n") + 1, "lines")
