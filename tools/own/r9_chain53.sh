#!/bin/bash
# TEST ONLY (ninth round, the user's items 1 and 4 of 2026-11-15 evening): candidate v123 (glue 65 fifth form + its second part
# co_two: the dome's command in both heroes' menus). The last Xemnas's laser dome (HP 40 kits), four runs at once:
#   xsI run-m   capture log, ONLY PLAYER 2 presses   -> reflect moves sent by player 2; the dome goes on as in xsC
#   xsJ run-v3  capture log, ONLY PLAYER 1 presses   -> as xsC on v122
#   xsK run-v3b capture log, BOTH press              -> one callback per press, no press counted twice
#   xsL run-v3c recorder in front of rc_one (make_rec_rc.py), ONLY PLAYER 2 presses -> his calls in the dome
# usage: r9_chain53.sh [ownTag]   (default test-own-v123)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v123}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain53.txt"; }
say "chain53 start ($X)"
CAPSN="6400,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <probe> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/$6" FROM=4700 TO=15900 SNAPS="$CAPSN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$7" P2S="$O/$8" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh20.txt"
  say "$1 done"
}
one xsI run-m 29050 28081 $X-snapB-god-cap-xe0028 cap_log_probe2.py idle.txt mashrc_long_p2.txt &
one xsJ run-v3 30150 28061 $X-snapB-god-cap-xe0028 cap_log_probe2.py mashrc_long_p1.txt idle.txt &
one xsK run-v3b 30350 28062 $X-snapB-god-cap-xe0028 cap_log_probe2.py mashrc_long_p1.txt mashrc_long_p2.txt &
one xsL run-v3c 30550 28063 $X-snapB-god-xe0028-rc rc_probe.py idle.txt mashrc_long_p2.txt &
wait
say "chain53 through"
