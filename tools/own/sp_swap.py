"""Special player objects with a second copy (seventh round, part 7e): make the ORIGINAL object the first one built.
The placement tool (lane F / lane J, order "before") writes the added copy in front of the original. For the
PLAYER placeholder that is right (lane E: the hero made from the placeholder stays the engine's player). A special
object placed directly (carpet Sora, light cycle, ...) has no placeholder: the first one built becomes the
engine's player, so the added copy would be player 1 and the game's own vehicle logic would run for player 2.
This tool exchanges the two records (tools/lane-e/ard_edit.py "swap") wherever a spawn point holds the same
special object twice in a row.

  python -I tools/own/sp_swap.py <builtArdDir> <outDir> <objHex,objHex,...> [room,room,...]
Writes only the room files it changed into <outDir> (use it as --extra of tools/lane-s1/build_disc.py, or copy
the files over the built ones). Prints one line per exchange.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
EDIT = ROOT / "tools" / "lane-e" / "ard_edit.py"
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
objs = {int(x, 16) for x in sys.argv[3].split(",")}
rooms = sys.argv[4].split(",") if len(sys.argv) > 4 else ["al05", "al14", "tr02", "po06", "eh22", "nm10"]
out.mkdir(parents=True, exist_ok=True)
tmp = out / "_dump.txt"
total = 0
for room in rooms:
    ard = src / (room + ".ard")
    subprocess.run([str(DOTNET), str(KH2TOOL), "ard-dump", str(ard), str(tmp)], check=True, capture_output=True)
    edits, group, sp, ents = [], None, None, []

    def flush():
        for i in range(len(ents) - 1):
            if ents[i][1] in objs and ents[i + 1][1] == ents[i][1]:
                edits.append("swap:%s:%d:%d:%d" % (group, sp, ents[i][0], ents[i + 1][0]))
                print("%s %s spawn point %d: object %04X records %d and %d exchanged" % (room, group, sp, ents[i][1], ents[i][0], ents[i + 1][0]))

    for line in tmp.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"==== entry (\S+)\s+type (\S+)", line)
        if m:
            if group is not None and sp is not None:
                flush()
            group, sp, ents = (m.group(1) if m.group(2) == "AreaDataSpawn" else None), None, []
            continue
        if group is None:
            continue
        m = re.match(r"\s+spawnpoint (\d+):", line)
        if m:
            if sp is not None:
                flush()
            sp, ents = int(m.group(1)), []
            continue
        m = re.match(r"\s+\[(\d+)\] obj 0x([0-9A-Fa-f]{4})", line)
        if m and sp is not None:
            ents.append((int(m.group(1)), int(m.group(2), 16)))
    if group is not None and sp is not None:
        flush()
    if edits:
        subprocess.run([sys.executable, "-I", str(EDIT), str(ard), str(out / (room + ".ard"))] + edits, check=True)
        total += len(edits)
tmp.unlink(missing_ok=True)
print("%d exchanges" % total)
