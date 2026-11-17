#!/bin/bash
# TEST ONLY: on run-v3 after sweep worker x1: two no-patch controls (fault lines kept), the one recheck (r0),
# then the sweep's Type 1 list (y0: the 30 programs below 50).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sweep worker x1 done" local/sweep/x1.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-empty run-v3 30150 28061 spc3 test-s1-tt137.iso "$O/ctl_p1.txt" "$O/idle.txt" local/sweep/list-spc3.txt
bash tools/own/sweep1.sh r0 run-v3 30150 28061 test-own-v28-snapB local/sweep/list-r.txt type2
bash tools/own/sweep1.sh y0 run-v3 30150 28061 test-own-v28-snapB local/sweep/list-y.txt type1
