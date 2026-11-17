#!/bin/bash
# TEST ONLY (ninth round, item 4: the "Riku frees Sora" part with one hero held, candidate v127): the command that ended the part
# in the old pair run xeB (callback 654 -> move 0x104) is offered by a motion. Is it offered in the one-hero part, to whom, and
# do the presses reach glue 47's rc_one? HP 150 kits, 20,000 frames, lanes x2 .. x4.
#   rkC run-x2  recorder make_rec_offer2.py 654 (from counter 9000): player 1 mashrc_long, player 2 idle
#   rkD run-x3  the same recorder: both mashrc_long
#   rkE run-x4  recorder make_rec_rc.py (from 9000): both mashrc_long (who presses which source)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=test-own-v127
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain61.txt"; }
say "chain61 start ($X)"
LSN="6400,8000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,19900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <probe> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/$6" FROM=4700 TO=19900 SNAPS="$LSN" FRAMES=20000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$7" P2S="$O/$8" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh20.txt"
  say "$1 done"
}
one rkC run-x2 30950 28065 $X-snapB-god-xe0096-of654 offer_probe.py mashrc_long_p1.txt idle.txt &
one rkD run-x3 31150 28066 $X-snapB-god-xe0096-of654 offer_probe.py mashrc_long_p1.txt mashrc_long_p2.txt &
one rkE run-x4 31350 28067 $X-snapB-god-xe0096-rc rc_probe.py mashrc_long_p1.txt mashrc_long_p2.txt &
wait
say "chain61 through"
