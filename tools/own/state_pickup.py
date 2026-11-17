"""Helper for docs/STATE.md (eighth round):
  python -I tools/own/state_pickup.py new <pickupFile> <owedFile>   the section "PICK UP HERE" is replaced by a new
        one (the old one stays as "Older pick-up note of build 12"); @OWED@ in the new text = the owed file
  python -I tools/own/state_pickup.py owed <owedFile>               only the block "STILL OWED ..." (up to the next
        empty line) of the PICK UP HERE section is replaced
  python -I tools/own/state_pickup.py head <headFile>               only the heading line "## PICK UP HERE (rewritten
        ...)" is replaced by the one line in headFile
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = P.read_text(encoding="utf-8")
mode = sys.argv[1]
if mode == "new":
    new = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").rstrip("\n")
    owed = pathlib.Path(sys.argv[3]).read_text(encoding="utf-8").rstrip("\n")
    old_head = r"## PICK UP HERE (rewritten 2026-11-13 night: BUILD 12 IS IN `dist\`; the eighth round works down the register and the job list)"
    assert t.count(old_head) == 1, t.count(old_head)
    assert "@OWED@" in new and "## PICK UP HERE (rewritten 2026-11-14" not in t
    t = t.replace(old_head, new.replace("@OWED@", owed) + "\n\n"
                  "## Older pick-up note of build 12 (written 2026-11-13 night; its register, the test habits T1 to T5 and the old job list)")
elif mode == "owed":
    owed = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").rstrip("\n")
    a = t.index("## PICK UP HERE (rewritten 2026-11-1")       # (the head's date: 2026-11-14, since build 18 2026-11-15)
    b = t.index("\nSTILL OWED", a) + 1
    assert b < t.index("\n## ", a + 5)
    e = t.index("\n\n", b)
    t = t[:b] + owed + t[e:]
elif mode == "head":                       # (2026-11-16) only the heading line "## PICK UP HERE (rewritten ...)" is replaced
    head = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").strip("\n")
    assert head.startswith("## PICK UP HERE (rewritten ") and "\n" not in head
    a = t.index("## PICK UP HERE (rewritten 2026-11-1")
    e = t.index("\n", a)
    t = t[:a] + head + t[e:]
else:
    raise SystemExit(__doc__)
P.write_text(t, encoding="utf-8")          # the default on this PC writes CRLF, as the file always was
print("STATE.md:", mode, "done,", t.count("\n"), "lines")
