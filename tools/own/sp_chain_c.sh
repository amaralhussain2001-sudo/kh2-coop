#!/bin/bash
# TEST ONLY: the Olympus cups (tools/own/sweep_cups.py: one "If Entrance" block per cup mission name, 44 runs)
# on the four sandboxes after the third sweep pass. Logs local/sweep/c0.log .. c3.log.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
while [ ! -f local/sweep/z-done.txt ]; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sweep2.sh c0 run-m 29050 28081 test-own-v33-snapB local/sweep/list-c0.txt &
bash tools/own/sweep2.sh c1 run-v3 30150 28061 test-own-v33-snapB local/sweep/list-c1.txt &
bash tools/own/sweep2.sh c2 run-v3b 30350 28062 test-own-v33-snapB local/sweep/list-c2.txt &
bash tools/own/sweep2.sh c3 run-v3c 30550 28063 test-own-v33-snapB local/sweep/list-c3.txt &
wait
echo "cups done $(date +%H:%M:%S)" >> local/sweep/c-done.txt
