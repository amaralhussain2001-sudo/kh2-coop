"""Helper for docs/STATE.md (ninth round): the PICK UP HERE section gets a new heading line, a new first paragraph
(the text between the heading and the block "STILL OWED ...") and a new block "WHAT THE USER HAS NOW ..." (up to the
next empty line). The block "STILL OWED" itself is rewritten with tools/own/state_pickup.py owed <file>.
  python -I tools/own/state_pickup3.py <headingFile> <firstParagraphFile> <hasNowFile>
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = P.read_text(encoding="utf-8")
head, intro, has = (pathlib.Path(a).read_text(encoding="utf-8").strip("\n") for a in sys.argv[1:4])
assert head.startswith("## PICK UP HERE (") and "\n" not in head
assert has.startswith("WHAT THE USER HAS NOW") and "\n\n" not in has and "\n\n" not in intro
a = t.index("## PICK UP HERE (")
b = t.index("\nSTILL OWED", a) + 1
assert b < t.index("\n## ", a + 5)
t = t[:a] + head + "\n\n" + intro + "\n\n" + t[b:]
a = t.index("## PICK UP HERE (")
c = t.index("\nWHAT THE USER HAS NOW", a) + 1
assert c < t.index("\n## ", a + 5)
e = t.index("\n\n", c)
t = t[:c] + has + t[e:]
P.write_text(t, encoding="utf-8")          # the default on this PC writes CRLF, as the file always was
print("STATE.md: the pick-up heading, its first paragraph and WHAT THE USER HAS NOW are new,", t.count("\n"), "lines")
