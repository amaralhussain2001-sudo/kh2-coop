"""One-off repair of docs/STATE.md part 113 (2026-11-15), second: "patches" + a TAB (a Python escape of the path separator
and the letter t) back to the path "patches", backslash, "t". Keeps the line ends. Run once:
  python -I tools/own/state_fix113b.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
b = p.read_bytes()
old, new = b"patches" + bytes([9]), b"patches" + bytes([92]) + b"t"
n = b.count(old)
assert 0 < n <= 4, n
p.write_bytes(b.replace(old, new))
print("repaired", n)
