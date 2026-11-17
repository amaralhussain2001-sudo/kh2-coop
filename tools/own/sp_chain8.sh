#!/bin/bash
# TEST ONLY: on run-v3b after the batch v5b: the Atlantica musical with player 2 alone (no hero there: twenty-eighth
# glue), then the five replay (_FREE) special missions on the v5 test disc with scripts that never answer a
# Game Over menu (a Continue in a replay mission stops a jump test).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/v5b.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-own-v33-snapB run-v3b 30350 28062 nt2 test-s1-tt137.iso "$O/none_p1.txt" "$O/alone_mash_p2.txt" local/sweep/list-nt2.txt
bash tools/own/sp_batch.sh test-own-v33-snapB run-v3b 30350 28062 v5free test-v5-tt137.iso "$O/ctl_p1.txt" "$O/sticks_p2.txt" local/sweep/list-v5free.txt
