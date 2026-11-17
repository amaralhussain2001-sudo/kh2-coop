#!/bin/bash
# TEST ONLY (ninth round, job 5): THE THREE SMALL GAMES STARTED BY THE GAME'S OWN "TYPE 2" JUMP (world + set number: the jump the story's
# event makes, e.g. "SetJump Type 2 World NM ... LocalSet 63"; tools/own/sweep6.sh with make_jumpkit.py), not by the Type 1 jump into the
# room with three program numbers that the other runs use. Candidate v107 (-snapB), 16,000 frames, probe sp_probe.py.
#   run-m: t2A = nm10 63 the toy cannon (cannon scripts)   run-v3: t2B = al14 61 the carpet escape   run-v3b: t2C = eh22 72 the sidecar
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v107-snapB}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain42.txt"; }
say "chain42 start ($OWN)"
SN="5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <list> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="$SN" FRAMES=16000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep6.sh $1 $2 $3 $4 "$OWN" "$5"
  say "$1 done"
}
one t2A run-m 29050 28081 "$B/list-t2-nm63.txt" cannon_p1.txt cannon_p2.txt &
one t2B run-v3 30150 28061 "$B/list-t2-al61.txt" sp_p1.txt sp_p2.txt &
one t2C run-v3b 30350 28062 "$B/list-t2-eh72.txt" sp_p1.txt sp_p2.txt &
wait
say "chain42 through"
