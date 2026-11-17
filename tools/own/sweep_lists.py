"""Make the list files for the second pass of the mission sweep (tools/own/sweep1.sh) from the first pass's logs:
  type 1 list  the programs with a number below 50 (the world's table does not know them: jump by room);
  type 2 lists every other mission that has no result yet, or whose session did not close (Game Over + Continue
               on the jump disc, or the 200-second limit).
  python -I tools/own/sweep_lists.py <workers>      -> local/sweep/list-x0.txt .. list-x<N-1>.txt (type 2),
                                                        local/sweep/list-y.txt (type 1)
Logs read: local/sweep/*.log (the last line of a mission wins)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SW = ROOT / "local" / "sweep"
n = int(sys.argv[1])
done = {}
for log in sorted(SW.glob("*.log")):
    for line in log.read_bytes().decode("utf-8", "replace").replace(chr(13) + " | ", " | ").splitlines():   # (a list file with CR LF leaves a CR behind the party word)
        parts = line.split(" | ")
        head = parts[0].split()
        if len(head) >= 5 and len(parts) >= 3:
            done[tuple(head[:3])] = "never out of sync" in parts[1] or "OUT OF SYNC" in parts[1]
t1, t2 = [], []
for line in (SW / "missions.txt").read_text(encoding="utf-8").splitlines():
    h = line.split()
    if len(h) < 5:
        continue
    if int(h[2]) < 50:
        t1.append(line)
    elif not done.get(tuple(h[:3])):
        t2.append(line)
(SW / "list-y.txt").write_text("\n".join(t1) + "\n", encoding="utf-8", newline="\n")
for i in range(n):
    (SW / ("list-x%d.txt" % i)).write_text("\n".join(t2[i::n]) + "\n", encoding="utf-8", newline="\n")
print("type 1: %d missions; type 2 still to run: %d in %d lists" % (len(t1), len(t2), n))
