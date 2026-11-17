"""One-off repair of docs/STATE.md part 113 (2026-11-15): a path in the note was written with a Python "\r" escape, so
"tools\own\r9_chain60.sh" was split into two lines. Joins them again; keeps the file's line ends. Run once:
  python -I tools/own/state_fix113.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
b = p.read_bytes()
BS = bytes([92])
for nl in (b"\r\r\n", b"\r\n", b"\n", b"\r"):
    old = b"(`tools" + BS + b"own" + nl + b"9_chain60.sh`"
    if b.count(old) == 1:
        b = b.replace(old, b"(`tools" + BS + b"own" + BS + b"r9_chain60.sh`")
        p.write_bytes(b)
        print("joined (line end was %r); CRLF lines: %d, LF-only lines: %d" % (nl, b.count(b"\r\n"), b.count(b"\n") - b.count(b"\r\n")))
        break
else:
    raise SystemExit("not found")
