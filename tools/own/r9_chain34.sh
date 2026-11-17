#!/bin/bash
# TEST ONLY (ninth round, job 6): THE GUMMI FLIGHT COUNTS PLAYER 2'S POINTS (the sixty-sixth glue). Route 0, 14,000 frames, probe gscore_probe.py:
#   gq1 = only player 1 fires (player 2's points must stay 0)   gq2 = only player 2 fires (all points must be his)   gq3 = both fire
# usage: r9_chain34.sh <ownPatch-gum0> <tag> <sandbox1> <port1> <pine1> <sandbox2> <port2> <pine2> <sandbox3> <port3> <pine3>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S3="$P/tests/scripts/lane-s3"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v108-gum0}; TG=${2:-gq}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain34.txt"; }
say "chain34 start ($OWN, $TG)"
SN="7000,8000,9000,10000,11000,12000,13000,13900"
one() {  # one <name> <p1script> <p2script> <sandbox> <port> <pine>
  out=$(PROBE="$T/gscore_probe.py" SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r9$1" "patches/$OWN" test-s1-tt137.iso 14000 "$SN" "$S3/$2" "$S3/$3" $4 $5 $6 2>&1 | head -n 1)
  say "$1 | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/$4/p1/logs/emulog.txt")"
}
one ${TG}1 gb_p1_fight.txt gb_p2_idle.txt ${3:-run-x1} ${4:-30750} ${5:-28064} &
one ${TG}2 gb_p1_idle.txt gb_p2_fight.txt ${6:-run-x2} ${7:-30950} ${8:-28065} &
one ${TG}3 gb_p1_fight.txt gb_p2_fight.txt ${9:-run-x3} ${10:-31150} ${11:-28066} &
wait
say "chain34 through ($TG)"
