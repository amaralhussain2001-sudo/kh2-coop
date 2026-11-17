"""Test button script maker: an existing script's lines (without its end line) + one button pressed every N frames.
  python -I tools/own/make_mash.py <out.txt> <baseScript or -> <BUTTON> <from> <to> <every> [<BUTTON> <from> <to> <every> ...]
"""
import pathlib
import sys

out, base = pathlib.Path(sys.argv[1]), sys.argv[2]
rows = []
if base != "-":
    for l in pathlib.Path(base).read_text(encoding="utf-8").splitlines():
        if l.strip() and not l.startswith("#") and not l.startswith("999999"):
            parts = l.split()
            rows.append((int(parts[0]), l))
a = sys.argv[3:]
for i in range(0, len(a), 4):
    b, f0, f1, ev = a[i], int(a[i + 1]), int(a[i + 2]), int(a[i + 3])
    rows += [(f, "%d 4 %s" % (f, b)) for f in range(f0, f1, ev)]
rows.sort(key=lambda r: r[0])
text = "# made by tools/own/make_mash.py %s\n" % " ".join(sys.argv[2:]) + "\n".join(r[1] for r in rows) + "\n999999 1 \n"
out.write_text(text, encoding="utf-8")
print(out, len(rows), "lines")
