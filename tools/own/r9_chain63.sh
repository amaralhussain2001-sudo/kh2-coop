#!/bin/bash
# TEST ONLY (ninth round, the user's items 1 and 4 of 2026-11-15 evening), candidate v128 (fourth part, fourth form: hs_rc only: the dome's
# pieces run on the named hero; the other hero's press is sent in his name; ip_one as a safety net). The last Xemnas's dome
# (HP 40, capture log), four lanes:
# usage: r9_chain63.sh [ownTag]   (default test-own-v128)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v128}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain63.txt"; }
say "chain63 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$X-snapB-god-cap-xe0028" "$B/list-eh20.txt"
  say "$1 done"
}
#   xt2 run-m   ONLY player 2 presses        xs3 run-v3   both, player 2 five frames later (xsY's case)
#   xt4 run-v3b both, player 1 five frames later   xs5 run-v3c  both in the same frames   xs6 run-x1  ONLY player 1
one xt2 run-m 29050 28081 idle.txt mashrc_long_p2.txt &
one xt3 run-v3 30150 28061 mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one xt4 run-v3b 30350 28062 mashrc_long_p1_off5.txt mashrc_long_p2.txt &
one xt5 run-v3c 30550 28063 mashrc_long_p1.txt mashrc_long_p2.txt &
one xt6 run-x1 30750 28064 mashrc_long_p1.txt idle.txt &
wait
say "chain63 through"
