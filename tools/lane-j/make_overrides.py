"""Lane J: turn the "study" result into the placement override file that tools/lane-j/LaneJ twin-all reads.

  python -I tools/lane-j/make_overrides.py <study.csv> <manual.csv|-> <out overrides.csv>

study.csv   output of `LaneJ study` (one line per placement lane F could not prove)
manual.csv  optional hand-made lines in the override format; they win over the study result
Override format (one line per placement; the first eight columns are the key and equal the report columns):
  room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,twin_x,twin_y,twin_z,status,note
status: proven-ground | proven-drop | proven-free-space | seen (looked at in a test) | guess
"""
import csv
import pathlib
import sys

study, manual, out = sys.argv[1], sys.argv[2], sys.argv[3]
rows = {}
for r in csv.DictReader(open(study, encoding="utf-8")):
    if r["mode"] == "NOT PROVEN":
        continue
    key = (r["room"], r["group"], r["spawnpoint"], r["spawn_type"], r["spawn_arg"], r["player_x"], r["player_y"], r["player_z"])
    status = "proven-" + r["mode"].replace(" ", "-")
    note = (r["spot"] + "; " + r["note"]).replace(",", ";")
    rows[key] = [r["twin_x"], r["twin_y"], r["twin_z"], status, note]
if manual != "-":
    for line in pathlib.Path(manual).read_text(encoding="utf-8").splitlines()[1:]:
        c = line.split(",")
        if len(c) < 12 or c[0].startswith("#"):
            continue
        rows[tuple(c[:8])] = [c[8], c[9], c[10], c[11], " ".join(c[12:])]
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,twin_x,twin_y,twin_z,status,note\n")
    for key in sorted(rows):
        f.write(",".join(list(key) + rows[key]) + "\n")
print("override lines:", len(rows))
