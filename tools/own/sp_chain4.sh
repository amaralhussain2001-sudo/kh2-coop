#!/bin/bash
# TEST ONLY: on run-v3b after the batch sp3: the gauge guard (EH14_MS103 again on patch v32), the Light Cycle
# button tests (player 2 alone presses, then player 1 alone), then every special-mode mission on the v5 test disc.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/sp3.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-own-v32-snapB run-v3b 30350 28062 q test-s1-tt137.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-q.txt
G="$P/local/sweep/lc.log"
for t in "lc-p2 lc_new_p1 lc_act_p2" "lc-p1 lc_act_p1 lc_idle_p2"; do
  set -- $t
  out=$(FROM=5200 TO=6500 PROBE="$P/tools/own/act_poll_probe.py" bash "$P/tools/own/dusk_one.sh" "$1" patches/test-lc-61 test-v5-tt137.iso 7000 "5300,5450,5750,5950,6100,6400" "$O/$2.txt" "$O/$3.txt" run-v3b 30350 28062 2>&1 | head -n 1)
  echo "$1 | $out | TLB misses $(grep -c 'TLB Miss' "$P/local/run-v3b/p1/logs/emulog.txt")" >> "$G"
  sed 's/^/    /' "$P/local/tests/$1-probe.txt" | cut -c1-170 | head -n 60 >> "$G"
done
echo "lc done" >> "$G"
bash tools/own/sp_batch.sh test-own-v32-snapB run-v3b 30350 28062 v5 test-v5-tt137.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-v5.txt
