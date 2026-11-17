#!/bin/bash
# TEST ONLY (eighth round, part 82): THE RELEASE OF THE SIXTIETH GLUE ITSELF. Candidate v93t = v93 with the test
# option --holdwatch-test (a hero in one and the same captured motion for 100 steps, not 1,800, is let go), so
# that ORDINARY holds are cut: six boss rooms, two lanes (run-v3b: the Dark Thorn, the Groundshaker, the Hydra;
# run-v3c: Cerberus, Scar, Xaldin). Everything else as r8_chain128.sh; run names r8r9t-*.
# THE QUESTIONS: does a hero who is let go in the middle of a boss's hold go on normally (no fault line, in sync,
# nobody stuck), and does the boss go on.
# Logs local/sweep/b15/r9t1.log, r9t2.log; progress chain130.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain130.txt"; }
say "chain130 start"
lane() {  # lane <worker> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8r9t P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-own-v93t-snapB-god "$L/list-$1.txt"
  say "lane $1 through"
}
lane r9t1 run-v3b 30350 28062 &
lane r9t2 run-v3c 30550 28063 &
wait
say "chain130 through"
