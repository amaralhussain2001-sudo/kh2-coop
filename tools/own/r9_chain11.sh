#!/bin/bash
# TEST ONLY (ninth round, plan row 39): CANDIDATE v102 (= v101 + kb_fact forgets kb_fix's note for a new body), two runs again:
#  keB (run-v3)   A SAVE, A GAME OVER AND "CONTINUE" with two different Keyblades (run kdB again).
#  keC (run-v3b)  KING MICKEY'S RESCUE FOR TWO at Storm Rider; both heroes fall at 5400 this time (in run kdC they were riding
#                 the dragon at 6500 and the fall did not come).
# Probe tools/own/kb_probe.py. Logs local/sweep/r9/keB.log, keC.log; progress chain11.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain11.txt"; }
say "chain11 start"
( PROBE="$T/kb_probe.py" SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh r9keB "$P/patches/test-own-v102-die2-kb" test-m-roam.iso 16000 "6600,7000,8000,9000,9100,9700,10300,11000,12000,13000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" run-v3 30150 28061 > "$B/keB.log" 2>&1
  echo "TLB misses $(grep -ac 'TLB Miss' local/run-v3/p1/logs/emulog.txt)" >> "$B/keB.log"; cat "$P/local/tests/r9keB-probe.txt" >> "$B/keB.log" 2>/dev/null; say "keB done" ) &
( ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="5200,5600,5900,6400,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900" FRAMES=14000 TOUT=700 SWEEP_PROBE_WAIT=700 LOGDIR=local/sweep/r9 TAG=r9keC P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh keC run-v3b 30350 28062 test-own-v102-mk "$L/list-sr1.txt"; say "keC done" ) &
wait
say "chain11 through"
