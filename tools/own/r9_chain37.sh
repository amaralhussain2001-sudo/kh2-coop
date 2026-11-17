#!/bin/bash
# TEST ONLY (ninth round, job 6): which ship fires a cannon shot: the log of shot start-ups (make_rec_ginit.py, probe ginit_probe.py).
#   gi1 = only player 1 fires     gi2 = only player 2 fires.   Route 0, 11,000 frames. Lanes run-x1, run-x2.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S3="$P/tests/scripts/lane-s3"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain37.txt"; }
say "chain37 start"
one() {  # one <name> <p1script> <p2script> <sandbox> <port> <pine>
  out=$(PROBE="$T/ginit_probe.py" FROM=6000 TO=10900 SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r9$1" "patches/test-own-v103-gum0-ginit" test-s1-tt137.iso 11000 "8000,9000,10000,10900" "$S3/$2" "$S3/$3" $4 $5 $6 2>&1 | head -n 1)
  say "$1 | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/$4/p1/logs/emulog.txt")"
}
one gi1 gb_p1_fight.txt gb_p2_idle.txt run-x1 30750 28064 &
one gi2 gb_p1_idle.txt gb_p2_fight.txt run-x2 30950 28065 &
wait
say "chain37 through"
