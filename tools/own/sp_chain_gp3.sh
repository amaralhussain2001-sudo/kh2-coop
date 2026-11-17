#!/bin/bash
# TEST ONLY (2026-11-13): player 2 ALONE against Shan-Yu again (player 1 only starts the game), HP kit, 24,000 frames,
# with the jump of the clean sweep run (map = battle = event = 75), sandbox run-v3c after sp_chain_valor.sh.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "TLB misses" local/sweep/b13/valorf-p1.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 15" > /dev/null; done
SNAPS=5200,7000,9000,11000,13000,15000,17000,19000,21000,23900 FRAMES=24000 TOUT=1000 SWEEP_PROBE_WAIT=1000 LOGDIR=local/sweep/b13c TAG=gp3 \
  P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep3.sh gp3 run-v3c 30550 28063 test-own-v33-snapB-god local/sweep/list-gp3.txt
