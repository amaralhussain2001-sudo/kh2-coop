"""One-off: the SIXTY-THIRD GLUE of tools/merge/merge_v7.py (--ownkey): its room is 0x000EC700 .. 0x000ECF00 now
(with kb_fix it has 476 words; the room of 384 was too small). The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_ownkey4.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
a = "KB_END = 0x000ECD00"
if a not in s:
    raise SystemExit("already there")
assert s.count(a) == 1
s = s.replace(a, "KB_END = 0x000ECF00")
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
