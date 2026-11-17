#!/bin/bash
# TEST ONLY: the third pass of the mission sweep. Waits for the workers x2, x4, x5 and y0, makes the list of the
# missions that still show no hero (tools/own/sweep_lists3.py; plus BB05_MS104B program 81, whose fault lines
# come from the missing map program), splits it in four and runs four workers (tools/own/sweep2.sh, logs z0..z3).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
for w in x2 x4 x5 y0; do
  while ! grep -q "sweep worker $w done" "local/sweep/$w.log" 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
done
python -I tools/own/sweep_lists3.py > local/sweep/list-z-how.txt 2>&1
python - <<'PY'
import pathlib, subprocess, sys
SW = pathlib.Path("local/sweep")
lines = [l for l in (SW / "list-z.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
extra = subprocess.run([sys.executable, "-I", "tools/own/sweep_lists3.py", "bb05:81"], capture_output=True, text=True)
lines += [l for l in (SW / "list-z.txt").read_text(encoding="utf-8").splitlines() if l.strip() and l not in lines]
(SW / "list-z-all.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
for i in range(4):
    (SW / ("list-z%d.txt" % i)).write_text("\n".join(lines[i::4]) + "\n", encoding="utf-8", newline="\n")
print(len(lines), "missions in the third pass")
PY
bash tools/own/sweep2.sh z0 run-m 29050 28081 test-own-v33-snapB local/sweep/list-z0.txt &
bash tools/own/sweep2.sh z1 run-v3 30150 28061 test-own-v33-snapB local/sweep/list-z1.txt &
bash tools/own/sweep2.sh z2 run-v3b 30350 28062 test-own-v33-snapB local/sweep/list-z2.txt &
bash tools/own/sweep2.sh z3 run-v3c 30550 28063 test-own-v33-snapB local/sweep/list-z3.txt &
wait
echo "third pass done $(date +%H:%M:%S)" >> local/sweep/z-done.txt
