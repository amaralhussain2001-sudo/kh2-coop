#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF CANDIDATE v93 (= v89 + glue 58 "player 2's own ability
# switches" + glue 60 "no hero is held for ever"; patches/test-own-v93 / patches/test-v17-a, control
# patches/test-v17-a-nn) ON EIGHT SANDBOXES AT ONCE: tools/own/reg_par8.sh test-own-v93 test-v17-a b20 w20 (the
# fourteen steps and the thirteen counting runs w20-*). It first waits until r8_chain130.sh (run-v3b, run-v3c) is
# through. v89's logs of the same steps: local/reg-b18/. (The regression of v92, r8_chain127.sh, prefix b19, was
# stopped two minutes after its start: void.)
# Progress: local/reg-par8.log (last line "ALL EIGHT THROUGH"), local/sweep/b15/count-b20.txt, chain131.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
echo "chain131 start (waiting for chain 130) $(date +%H:%M:%S)" >> "$B/chain131.txt"
n=0
while ! grep -q "chain130 through" "$B/chain130.txt" 2>/dev/null && [ $n -lt 180 ]; do sleep 10; n=$((n+1)); done
if [ $n -ge 180 ]; then echo "chain131: chain 130 did not end in 30 minutes, nothing run $(date +%H:%M:%S)" >> "$B/chain131.txt"; exit 0; fi
echo "chain131 go $(date +%H:%M:%S)" >> "$B/chain131.txt"
bash tools/own/reg_par8.sh test-own-v93 test-v17-a b20 w20
echo "chain131 through $(date +%H:%M:%S)" >> "$B/chain131.txt"
