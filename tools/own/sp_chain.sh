#!/bin/bash
# TEST ONLY: waits for the first special-mode batch (log sp1), then runs the no-patch controls on the plain jump
# disc and the second batch on the disc with second vehicles. usage: bash tools/own/sp_chain.sh
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/sp1.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-empty run-v3b 30350 28062 spc test-s1-tt137.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-spc.txt
bash tools/own/sp_batch.sh test-own-v28-snapB run-v3b 30350 28062 sp2 test-s1-tt137sp2.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-sp2.txt
