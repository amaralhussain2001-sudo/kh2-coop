"""Lane R: what do the area-event kinds other than exits (1) and event triggers (3) hold in the room data?

  python -I tools/lane-r/kinds.py <ardDir> <objentry.txt> <outTxt>
For each kind: rooms, number of spawn points, and the object types / most common objects of their entities.
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-e"))
from ard import bar_entries, spawn_points  # noqa: E402

ard_dir, objfile, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
objs = {}
for line in objfile.read_text(errors="replace").splitlines():
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = (m.group(2), m.group(3))

per = collections.defaultdict(lambda: dict(rooms=collections.Counter(), sps=0, types=collections.Counter(),
                                           models=collections.Counter(), groups=collections.Counter(), noact=0))
for f in sorted(ard_dir.glob("*.ard")):
    data = f.read_bytes()
    for typ, name, off, size in bar_entries(data):
        if typ != 12 or size == 0:
            continue
        try:
            sps = spawn_points(data[off:off + size])
        except Exception:  # noqa: BLE001
            continue
        for sp in sps:
            k = sp["type"]
            d = per[k]
            d["rooms"][f.stem] += 1
            d["sps"] += 1
            d["groups"][name[:1]] += 1
            if not sp["acts"]:
                d["noact"] += 1
            for e in sp["ents"]:
                t, mdl = objs.get(e["obj"], ("?", "%04X" % e["obj"]))
                d["types"][t] += 1
                d["models"][mdl] += 1
lines = []
for k in sorted(per):
    d = per[k]
    lines.append("KIND %d: %d spawn points in %d rooms (%d without any volume); group name starts: %s" % (
        k, d["sps"], len(d["rooms"]), d["noact"], dict(d["groups"].most_common(6))))
    if len(d["rooms"]) <= 12:
        lines.append("   rooms: " + ", ".join("%s x%d" % rc for rc in sorted(d["rooms"].items())))
    else:
        lines.append("   rooms (top): " + ", ".join("%s x%d" % rc for rc in d["rooms"].most_common(10)))
    lines.append("   entity object types: " + ", ".join("%s %d" % tc for tc in d["types"].most_common(8)))
    lines.append("   most common objects: " + ", ".join("%s %d" % mc for mc in d["models"].most_common(12)))
    lines.append("")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
