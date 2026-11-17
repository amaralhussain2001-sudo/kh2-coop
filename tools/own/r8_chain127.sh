#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF CANDIDATE v92 (= v89 + glue 58 "player 2's own ability
# switches" + glue 59 "a boss that holds one hero captures that hero"; patches/test-own-v92 / patches/test-v16-a,
# control patches/test-v16-a-nn) ON EIGHT SANDBOXES AT ONCE: tools/own/reg_par8.sh test-own-v92 test-v16-a b19 w19
# (the fourteen steps and the thirteen counting runs w19-*). It first waits until the two boss-room lanes
# (r8_chain124.sh on run-x1, r8_chain125.sh on run-x4) are through. v89's logs of the same steps: local/reg-b18/.
# Progress: local/reg-par8.log (last line "ALL EIGHT THROUGH"), local/sweep/b15/count-b19.txt, chain127.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
echo "chain127 start (waiting for chains 124 and 125) $(date +%H:%M:%S)" >> "$B/chain127.txt"
n=0
while { ! grep -q "chain124 through" "$B/chain124.txt" 2>/dev/null || ! grep -q "chain125 through" "$B/chain125.txt" 2>/dev/null; } && [ $n -lt 180 ]; do sleep 10; n=$((n+1)); done
if [ $n -ge 180 ]; then echo "chain127: the lanes did not end in 30 minutes, nothing run $(date +%H:%M:%S)" >> "$B/chain127.txt"; exit 0; fi
echo "chain127 go $(date +%H:%M:%S)" >> "$B/chain127.txt"
bash tools/own/reg_par8.sh test-own-v92 test-v16-a b19 w19
echo "chain127 through $(date +%H:%M:%S)" >> "$B/chain127.txt"
