#!/bin/bash
# TEST ONLY (ninth round, plan row 9, job 3): THE FIGHTS WHOSE STATE IS "RUN" OR "SWEEP" IN docs\ROW9-PAIRED-MOVES.md, PLAYED ON PURPOSE
# WITH TWO HEROES: 40 missions (local/sweep/r9/list-r9s-0.txt .. 3.txt), candidate v103 with HP held at 150 (kit -snapB-god), the v5
# test disc, 20,000 frames each, both players Circle / Triangle / R1 (mashrc_long), probe act_poll_probe.py (a captured motion shows
# as action FC .. FF). Four lanes: run-m, run-v3, run-v3b, run-v3c (the pool sweep has run-x1 .. run-x6).
# Logs local/sweep/r9/r9s0.log .. r9s3.log, timelines local/tests/r9rs-*-probe.txt (read them with tools/own/holdsum.py); progress chain15.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v103-snapB-god}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain15.txt"; }
say "chain15 start ($OWN)"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9rs P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh r9s$1 $2 $3 $4 "$OWN" "$B/list-r9s-$1.txt"
  say "r9s$1 done"
}
lane 0 run-m 29050 28081 &
lane 1 run-v3 30150 28061 &
lane 2 run-v3b 30350 28062 &
lane 3 run-v3c 30550 28063 &
wait
say "chain15 through"
