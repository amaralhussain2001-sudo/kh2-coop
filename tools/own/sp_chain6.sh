#!/bin/bash
# TEST ONLY: on run-m after sweep worker x0: sweep worker x3 (the fourth list of the second pass).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
while ! grep -q "sweep worker x0 done" local/sweep/x0.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sweep1.sh x3 run-m 29050 28081 test-own-v28-snapB local/sweep/list-x3.txt type2
