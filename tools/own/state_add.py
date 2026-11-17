"""Append a block of text to the newest round of docs/STATE.md: it goes in just before the line "## Open items".
(Notes are written with the file tools into a text file first: no backslash trouble in shell commands.)
  python -I tools/own/state_add.py <textFile> [<marker line the text must go before>]
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
state = ROOT / "docs" / "STATE.md"
add = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").rstrip("\n") + "\n\n"
marker = sys.argv[2] if len(sys.argv) > 2 else "## Open items"
t = state.read_text(encoding="utf-8")
i = t.index("\n" + marker + "\n") + 1
first = add.split("\n", 1)[0]
if first and first in t:
    raise SystemExit("already in the state file: " + first[:80])
state.write_text(t[:i] + add + t[i:], encoding="utf-8")
print("added %d lines before '%s'" % (add.count("\n"), marker))
