#!/bin/bash
# TEST ONLY: the fourth sweep pass (tools/own/sweep_lists4.py, lists q0..q3) on the four sandboxes after the cups.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
while [ ! -f local/sweep/c-done.txt ]; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sweep2.sh zq0 run-m 29050 28081 test-own-v33-snapB local/sweep/list-q0.txt &
bash tools/own/sweep2.sh zq1 run-v3 30150 28061 test-own-v33-snapB local/sweep/list-q1.txt &
bash tools/own/sweep2.sh zq2 run-v3b 30350 28062 test-own-v33-snapB local/sweep/list-q2.txt &
bash tools/own/sweep2.sh zq3 run-v3c 30550 28063 test-own-v33-snapB local/sweep/list-q3.txt &
wait
echo "fourth pass done $(date +%H:%M:%S)" >> local/sweep/q-done.txt
