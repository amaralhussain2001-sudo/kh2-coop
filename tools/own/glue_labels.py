"""Read-only: the addresses of the labels of one glue of tools/merge/merge_v7.py (for test kits that switch a
routine off, and for reading a listing).
  python -I tools/own/glue_labels.py <PREFIX> [label ...]      PREFIX = the glue's names in the builder: KB, GO, GA ...
  (the glue's source is <PREFIX>_SRC, its address <PREFIX>_AT; symbols it needs from outside are set to 0)"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "merge"))
sys.argv, argv = [sys.argv[0]], sys.argv
import merge_v7 as m  # noqa: E402
from asm import assemble, AsmError  # noqa: E402

pre = argv[1]
src, at = getattr(m, pre + "_SRC"), getattr(m, pre + "_AT")
syms = {}
for _ in range(20):
    try:
        code, labels = assemble(at, src, syms)
        break
    except AsmError as e:
        mm = re.search(r"unknown symbol or number: (\w+)", str(e))
        if not mm:
            raise
        syms[mm.group(1)] = 0
want = argv[2:]
for k in sorted(labels, key=lambda k: labels[k]):
    if k in syms:
        continue
    if not want or k in want:
        print("%08X %s" % (labels[k], k))
print("(%d words; outside symbols set to 0: %s)" % (len(code), ", ".join(sorted(syms)) or "none"))
