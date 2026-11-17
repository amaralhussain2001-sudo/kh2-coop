#!/bin/bash
# TEST ONLY (ninth round, the user's item 3 of 2026-11-15 evening: the Large Body's command and the Samurai duel by player 2),
# candidate v126. Lanes run-x5 / run-x6 (and run-x1 / run-x2 when given "4"):
#   lbC run-x5  Agrabah city al00, battle program 2 (Large Bodies), recorder make_rec_offer2.py for command 533 "Full Swing":
#               player 1 walks away (walk_p1), player 2 only Triangle (tri_long_p2) -> is "Full Swing" offered, to whom
#   smC run-x6  Twilight Town tt19, battle program 7, the scripts of run smA (player 1 idle, player 2 mashrc_long), probe
#               sy_count_probe.py on the Samurai of smA (object 0x01B0C480: work + 160 .. 175, "The End" = work + 164)
#               and pictures every 40 frames around the duel
#   lbD run-x1  as lbC, but ONLY PLAYER 1 presses Triangle (tri_long_p1, new) and player 2 is idle: is "Full Swing"
#               offered to anyone in that room (the control)
#   smD run-x2  tt19 as smA with the recorder for command 301 "Duel Stance"
# usage: r9_chain57.sh [4]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=test-own-v126
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain57.txt"; }
say "chain57 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
DSN="7600,7640,7680,7720,7760,7800,7840,7880,7920,7960,8000,8040,8080,8120,8160,8200,8240,8280,8320,8400,8600,9000,15900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <probe> <frames> <snaps> <list> <p1> <p2>
  ISO=${ISO:-test-s1-tt137.iso} PROBE="$T/$6" FROM=4700 TO=$(( $7 - 100 )) SNAPS="$8" FRAMES=$7 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/${10}" P2S="$O/${11}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$9"
  say "$1 done"
}
one lbC run-x5 31550 28068 $X-snapB-god-of533 offer_probe.py 16000 "$SN" "$B/list-al00lb.txt" walk_p1.txt tri_long_p2.txt &
SY_OBJ=01B0C480 SY_WIN0=160 SY_WINN=4 one smC run-x6 31750 28069 $X-snapB-god sy_count_probe.py 16000 "$DSN" "$B/list-tt19sam.txt" ctl_p1.txt mashrc_long_p2.txt &
if [ "$1" = "4" ]; then
  one lbD run-x1 30750 28064 $X-snapB-god-of533 offer_probe.py 16000 "$SN" "$B/list-al00lb.txt" tri_long_p1.txt idle.txt &
  one smD run-x2 30950 28065 $X-snapB-god-of301 offer_probe.py 16000 "$SN" "$B/list-tt19sam.txt" ctl_p1.txt mashrc_long_p2.txt &
fi
wait
say "chain57 through"
