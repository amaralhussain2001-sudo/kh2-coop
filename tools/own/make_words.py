"""TEST ONLY: <base patch> + plain program words (for small test switches). Never part of the real patch.
  python -I tools/own/make_words.py <baseDir> <outDir> "<what it is>" ADDR=WORD [ADDR=WORD ...]      (hex)
Known switches:
  001AF07C=00000000   King Mickey's roll always wins (the "bc1f" after the compare with the game's random number)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
NAME = "SLPM-66675_F266B00B.pnach"
base, out, what = ROOT / sys.argv[1], ROOT / sys.argv[2], sys.argv[3]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
used = {l.split(",")[2].upper() for l in text if l.startswith("patch=")}
add = ["comment=TEST SWITCH (tools/own/make_words.py): %s. For tests only." % what]
for pair in sys.argv[4:]:
    a, w = (int(x, 16) for x in pair.split("="))
    s = "%08X" % a
    assert s not in used, s + " is already patched by the base"
    add.append("patch=1,EE,%s,word,%08X" % (s, w))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text + add) + "\n", encoding="utf-8")
print("written", out / NAME, len(add) - 1, "words")
