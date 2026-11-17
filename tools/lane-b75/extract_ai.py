"""Write out the AI script (BAR entry of type 3, 'Bdx') of every object file and decode it to text.

  python -I tools/lane-b75/extract_ai.py <extractedGameDir> <objentry.txt> <outDir> <Bdxio.exe>

Read-only on the game data. One .bdx and one .txt per object model that has a script.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
import bar  # noqa: E402

game, objtxt, out, bdxio = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
pat = re.compile(r"^0x([0-9A-F]+) type (\S+)\s+model (\S+)\s")
models = []
for line in open(objtxt, encoding="utf-8", errors="replace"):
    m = pat.match(line)
    if m:
        models.append((int(m.group(1), 16), m.group(2), m.group(3)))
done = no_file = no_ai = failed = 0
for obj, typ, model in models:
    path = os.path.join(game, "obj", model + ".mdlx")
    if not os.path.isfile(path):
        no_file += 1
        continue
    blob = open(path, "rb").read()
    try:
        ents = [e for e in bar.entries(blob) if e["type"] == bar.TYPE_BDX]
    except ValueError:
        no_ai += 1
        continue
    if not ents:
        no_ai += 1
        continue
    e = ents[0]
    bdx = os.path.join(out, model + ".bdx")
    txt = os.path.join(out, model + ".txt")
    if not os.path.isfile(txt):
        with open(bdx, "wb") as f:
            f.write(blob[e["offset"]:e["offset"] + e["size"]])
        r = subprocess.run([bdxio, "decode", bdx, txt], capture_output=True)
        if r.returncode != 0 or not os.path.isfile(txt):
            failed += 1
            continue
    done += 1
print("objects", len(models), "with AI script decoded", done, "no object file", no_file, "no AI entry", no_ai, "decode failed", failed)
