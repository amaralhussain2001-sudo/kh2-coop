"""Merge lane: one compact line per probe from a test's probe.txt.

  python -I tools/merge/psum.py <test-out-dir> [--every N]
Columns: frame, room, battle flag, then per hero: role letters (P = engine player, C = camera target, H = HUD owner,
t = lane E's twin), object address, controller, x / y / z, HP, MP, slot number + M (marked) or p (plain).
"""
import pathlib
import re
import sys

d = pathlib.Path(sys.argv[1])
every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
rows, cur = [], None
for line in (d / "probe.txt").read_text(encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"f(\d+) room (\w+) battle (\d+) \| engine player (\w+) .*? twin save bytes HP (\d+) MP\+1 (\d+) \| record HP (\d+) MP (\d+)", line)
    if m:
        cur = {"f": int(m.group(1)), "room": m.group(2), "btl": m.group(3), "heroes": [],
               "save": (m.group(5), m.group(6)), "rec": (m.group(7), m.group(8)), "notes": []}
        rows.append(cur)
        continue
    m = re.match(r"\s+control objects: S2 built (\w+), S2.player (\w+), S2.pad (\w+), menu on screen shows (\w+)", line)
    if m and cur:
        cur["notes"].append("S2 %s player %s %s, menu %s" % (m.group(1), m.group(2), m.group(3), m.group(4)))
        continue
    m = re.match(r"\s+hero (\w+) pos \(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\) (\w+)\s+slot (\d+) HP (-?\d+)/(\d+) MP (-?\d+)/(\d+) (\w+) id (-?\d+)\s+\[(.*?)\](?: ctl (\S+) act (\w+))?", line)
    if m and cur:
        roles = m.group(13)
        tag = ("P" if "ENGINE-PLAYER" in roles else "") + ("C" if "CAMERA" in roles else "") + \
              ("H" if "HUD" in roles else "") + ("t" if "twin" in roles else "")
        cur["heroes"].append("%-4s %s %s (%6.0f %5.0f %6.0f) HP %2s MP %3s s%s%s%s" % (
            tag or "-", m.group(1), m.group(5), float(m.group(2)), float(m.group(3)), float(m.group(4)),
            m.group(7), m.group(9), m.group(6), "M" if m.group(11) == "MARKED" else "p",
            (" ctl " + m.group(14)) if m.group(14) else ""))
        continue
    if cur and ("SET" in line or "REDIRECT" in line or "failed" in line):
        cur["notes"].append(line.strip())
    elif "read failed" in line:
        rows.append({"f": -1, "room": "?", "btl": "?", "heroes": [], "save": ("?", "?"), "rec": ("?", "?"), "notes": [line.strip()]})
for i, r in enumerate(rows):
    if i % every and i != len(rows) - 1:
        continue
    print("f%06d %s b%s | %s | twin bytes %s/%s rec %s/%s%s" % (
        r["f"], r["room"], r["btl"], " | ".join(r["heroes"]) or "(no hero object)", r["save"][0], r["save"][1],
        r["rec"][0], r["rec"][1], (" ## " + "; ".join(r["notes"])) if r["notes"] else ""))
