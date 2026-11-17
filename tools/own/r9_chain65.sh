#!/bin/bash
# TEST ONLY (ninth round, the user's question on pickups, 2026-11-15 night): WHO TAKES WHICH PRIZE (HP / MP / Drive / munny balls,
# item drops) with two heroes, candidate v129. Kit -snapB-god-strong-pk (HP held, Strength / Defense 150, recorder
# tools/own/make_rec_prize.py), probe tools/own/prize_probe.py; 16,000 frames; four lanes at once:
#   pkA run-m   the 1000 Heartless (hb17 66, no Donald / Goofy): player 2 fights (mashrc_long), player 1 runs far away and stands
#   pkB run-v3  the same, the other way round (player 1 fights, player 2 far away)
#   pkC run-v3b the same, both fight
#   pkD run-v3c Agrabah's city (al00 program 2, Donald and Goofy there): player 2 fights, player 1 far away
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
K=test-own-v129-snapB-god-strong-pk
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain65.txt"; }
say "chain65 start ($K)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <list> <p1> <p2>
  ISO=test-s1-tt137.iso PROBE="$T/prize_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 "$K" "$5"
  say "$1 done"
}
one pkA run-m 29050 28081 "$L/list-hb17.txt" walkfar_p1.txt mashrc_long_p2.txt &
one pkB run-v3 30150 28061 "$L/list-hb17.txt" mashrc_long_p1.txt far_p2.txt &
one pkC run-v3b 30350 28062 "$L/list-hb17.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
one pkD run-v3c 30550 28063 "$B/list-al00lb.txt" walkfar_p1.txt mashrc_long_p2.txt &
wait
say "chain65 through"
