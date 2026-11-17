#!/bin/bash
# TEST ONLY (ninth round, the user's items 1 and 4 of 2026-11-15 evening), candidate v122 (glue 65 fifth form: only the last
# Xemnas's laser dome takes both heroes; glue 68 left out: each hero keeps his own controller). The last Xemnas (eh20 74),
# capture log, HP held, both Xemnas objects' HP written at 6500. Four runs at once:
#   xsA run-m   HP 150 (the "Riku frees Sora" part), both mash             -> one hero held, the other free; the part ends
#   xsB run-v3  HP 150, player 1 steers Riku-wise as xeN (riku_steer_p1), player 2 idle  (probe riku_probe.py)
#   xsC run-v3b HP 40 (the laser dome), ONLY PLAYER 1 presses (mashrc_long_p1 / idle)   -> both in the dome; no capture or
#               callback with player 2 as the sender (one press is not counted for the other)
#   xsD run-v3c HP 40, ONLY PLAYER 2 presses (idle / mashrc_long_p2)
# usage: r9_chain51.sh
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain51.txt"; }
say "chain51 start"
CAPSN="6400,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,19900"
one() {  # one <name> <sandbox> <port> <pine> <own> <probe> <frames> <snaps> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/$6" FROM=4700 TO=$(( $7 - 100 )) SNAPS="$8" FRAMES=$7 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$9" P2S="$O/${10}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh20.txt"
  say "$1 done"
}
RSN=$(python -c "print(','.join(str(f) for f in range(9800, 13501, 100)))")
one xsA run-m 29050 28081 test-own-v122-snapB-god-cap-xe0096 cap_log_probe2.py 20000 "$CAPSN" mashrc_long_p1.txt mashrc_long_p2.txt &
one xsB run-v3 30150 28061 test-own-v122-snapB-god-xe0096 riku_probe.py 13600 "$RSN" riku_steer_p1.txt riku_wait_p2.txt &
one xsC run-v3b 30350 28062 test-own-v122-snapB-god-cap-xe0028 cap_log_probe2.py 16000 "$CAPSN" mashrc_long_p1.txt idle.txt &
one xsD run-v3c 30550 28063 test-own-v122-snapB-god-cap-xe0028 cap_log_probe2.py 16000 "$CAPSN" idle.txt mashrc_long_p2.txt &
wait
say "chain51 through"
