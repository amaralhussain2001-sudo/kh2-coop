"""Write out the script (BAR entry of type 3, 'Bdx') of mission files and decode it to text.

  python -I tools/lane-s1/extract_msn_ai.py <outDir> <MISSION> [<MISSION> ...]

Read-only on the game data (local/extract/kh2/msn/jp). The decoder is OpenKH's Bdxio (run only, nothing is
written in its folder).
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "lane-b75"))
import bar  # noqa: E402

BDXIO = r"C:\Users\PC FORCE\Desktop\openkh\Apps\OpenKh.Command.Bdxio.exe"
out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for name in sys.argv[2:]:
    path = ROOT / "local" / "extract" / "kh2" / "msn" / "jp" / (name + ".bar")
    blob = path.read_bytes()
    ents = bar.entries(blob)
    print(name, [(e.get("name"), e["type"], e["size"]) for e in ents])
    for i, e in enumerate(e for e in ents if e["type"] == bar.TYPE_BDX):
        bdx = out / ("%s_%d.bdx" % (name, i))
        txt = out / ("%s_%d.txt" % (name, i))
        bdx.write_bytes(blob[e["offset"]:e["offset"] + e["size"]])
        r = subprocess.run([BDXIO, "decode", str(bdx), str(txt)], capture_output=True)
        print("  ->", txt.name, "rc", r.returncode, r.stderr.decode(errors="replace")[:200])
