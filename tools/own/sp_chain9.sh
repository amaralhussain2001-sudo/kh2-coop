#!/bin/bash
# TEST ONLY: on run-v3b after the batch v5free: the two Pooh minigames that have no hero object (Hunny Slider,
# Hunny Pot) with player 2 alone (twenty-eighth glue).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/v5free.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-own-v33-snapB run-v3b 30350 28062 nt3 test-s1-tt137.iso "$O/none_p1.txt" "$O/alone_p2.txt" local/sweep/list-nt3.txt
