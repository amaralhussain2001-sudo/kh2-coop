"""TEST ONLY: <base patch> with some of ITS OWN patch words changed (make_words.py adds new words and refuses an
address the base patches; this one replaces the base's word there). For switching one routine of a glue off in a
test. Never part of the real patch.
  python -I tools/own/make_reword.py <baseDir> <outDir> "<what it is>" ADDR=WORD [ADDR=WORD ...]      (hex)"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
NAME = "SLPM-66675_F266B00B.pnach"
base, out, what = ROOT / sys.argv[1], ROOT / sys.argv[2], sys.argv[3]
text = (base / NAME).read_text(encoding="utf-8").rstrip("\n").split("\n")
for a in sys.argv[4:]:
    addr, word = a.split("=")
    addr, word = addr.upper().zfill(8), word.upper().zfill(8)
    hit = [i for i, l in enumerate(text) if l.startswith("patch=1,EE,%s,word," % addr)]
    assert len(hit) == 1, "%s: the base has %d lines for it" % (addr, len(hit))
    text[hit[0]] = "patch=1,EE,%s,word,%s" % (addr, word)
text.append("comment=TEST SWITCH (tools/own/make_reword.py %s): %s. For tests only." % (" ".join(sys.argv[4:]), what))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(text) + "\n", encoding="utf-8")
print(out, len(sys.argv) - 4, "words changed")
