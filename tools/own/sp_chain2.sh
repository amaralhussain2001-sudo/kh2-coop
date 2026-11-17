#!/bin/bash
# TEST ONLY: waits for the first chain (log sp2), then: the no-twin tests (plain jump disc, player 2 does everything
# alone) and the special modes on the disc with second objects, original first (test-s1-tt137sp3.iso).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/sp2.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-own-v29-snapB run-v3b 30350 28062 nt test-s1-tt137.iso "$O/none_p1.txt" "$O/alone_p2.txt" local/sweep/list-nt.txt
bash tools/own/sp_batch.sh test-own-v29-snapB run-v3b 30350 28062 sp3 test-s1-tt137sp3.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-sp3.txt
