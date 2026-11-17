"""One-off: room for the sixty-fifth glue's fifth form (--holdshared adds 14 words: 629 words, its range held 624). The sixty-ninth
glue (--ownwallet, 89 words, its range 0x000ED900 .. 0x000EDB00) starts 0x20 bytes later: glue 65's range ends at 0x000ED920,
glue 69's starts there. (Glue 69's code is the same; only its addresses move.)
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_holdshared2.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "HP_END = 0x000ED920" in s:
    raise SystemExit("already there")
for old, new in (("HP_END = 0x000ED900                                # (its code ends at 0x000ED8E0; 0x000ED900 .. 0x000EDC00 is the sixty-ninth glue's)\n",
                  "HP_END = 0x000ED920                                # (its code ends at 0x000ED8E0, with --holdshared at 0x000ED914; 0x000ED920 .. is the sixty-ninth glue's)\n"),
                 ("WW_AT = 0x000ED900\n", "WW_AT = 0x000ED920\n")):
    assert s.count(old) == 1, old
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
