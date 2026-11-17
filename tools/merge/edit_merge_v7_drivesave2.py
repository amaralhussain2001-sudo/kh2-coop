"""One-off: the seventy-second glue (--drivesave) is 77 words; its room 0x000EE800 .. 0x000EE900 holds 64. The room
becomes 0x000EE800 .. 0x000EEA00 (still free, inside this round's room). Run once:
  python -I tools/merge/edit_merge_v7_drivesave2.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
old = "DV_END = 0x000EE900\n"
assert s.count(old) == 1
s = s.replace(old, "DV_END = 0x000EEA00\n")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
