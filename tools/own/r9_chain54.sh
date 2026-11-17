#!/bin/bash
# TEST ONLY (ninth round, the user's items 1, 2 and 4 of 2026-11-15 evening): candidate v124 (glue 65 fifth form + co_two (the
# dome's command in both menus) + hs_hf (the dome is never a hero's own move)). Six lanes at once:
#   xsM run-m   last Xemnas, HP 40, capture log, BOTH press        -> the pair is made (in xsK on v123 it was not)
#   xsN run-v3  HP 40, capture log, ONLY PLAYER 2 presses           -> his reflects; the dome ends as with player 1
#   xsO run-v3b HP 40, capture log, ONLY PLAYER 1 presses           -> as xsC / xsJ
#   xsP run-v3c HP 150 (the Riku part), capture log, both mash, 20,000 frames -> one hero held, the part ends
#   syC run-x1  Shan-Yu's clash (mu09 75), strong kit + capture log, both press (mashrc_long), 12,000 frames (item 2)
#   syD run-x2  the same with fast mash on both pads (mashfast), 12,000 frames
# usage: r9_chain54.sh [ownTag]   (default test-own-v124)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v124}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain54.txt"; }
say "chain54 start ($X)"
CAPSN="6400,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900"
LSN="6400,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,19900"
SYN="5240,5400,5600,6000,6400,7000,7500,8000,9000,10000,11000,11900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <frames> <snaps> <list> <p1> <p2>
  ISO=${ISO:-test-v5-tt137.iso} PROBE="$T/cap_log_probe2.py" FROM=4700 TO=$(( $6 - 100 )) SNAPS="$7" FRAMES=$6 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$9" P2S="$O/${10}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$8"
  say "$1 done"
}
one xsM run-m 29050 28081 $X-snapB-god-cap-xe0028 16000 "$CAPSN" "$B/list-eh20.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
one xsN run-v3 30150 28061 $X-snapB-god-cap-xe0028 16000 "$CAPSN" "$B/list-eh20.txt" idle.txt mashrc_long_p2.txt &
one xsO run-v3b 30350 28062 $X-snapB-god-cap-xe0028 16000 "$CAPSN" "$B/list-eh20.txt" mashrc_long_p1.txt idle.txt &
one xsP run-v3c 30550 28063 $X-snapB-god-cap-xe0096 20000 "$LSN" "$B/list-eh20.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
ISO=test-s1-tt137.iso one syC run-x1 30750 28064 $X-snapB-god-strong-cap 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
ISO=test-s1-tt137.iso one syD run-x2 30950 28065 $X-snapB-god-strong-cap 12000 "$SYN" "$L/list-sy.txt" mashfast_p1.txt mashfast_p2.txt &
wait
say "chain54 through"
