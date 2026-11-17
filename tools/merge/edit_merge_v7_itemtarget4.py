"""One-off: the seventy-third glue's second form (edit_merge_v7_itemtarget3.py) is 194 words; the room 0x000EEA00 .. 0x000EED00
holds 192. The room becomes 0x000EEA00 .. 0x000EEE00 (still free, inside this round's room). Run once:
  python -I tools/merge/edit_merge_v7_itemtarget4.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
old = "II_END = 0x000EED00\n"
assert s.count(old) == 1
s = s.replace(old, "II_END = 0x000EEE00\n")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
