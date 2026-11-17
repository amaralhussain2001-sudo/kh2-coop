#!/bin/bash
# TEST ONLY (ninth round): THE THIRD FORM OF THE SIXTY-FIFTH GLUE (candidate v106) and the toy cannon's view, ten lanes:
#   run-v3, run-v3b, run-x4, run-m: the ten boss rooms on v106 with the capture log (r9_chain17.sh test-own-v106-snapB-god-cap h6)
#   run-x1: cnE = the toy cannon, a view for each player, fourth form (patches/test-own-v103f-snapB), 16,000 frames, pictures
#   run-x2: cnF = the same with tools/own/cam_probe.py, 9,000 frames
#   run-x5: lxD = Data Luxord (eh14 101) on v106 with the capture log     run-v3c: lxE = the same on v103
#   run-x6: gsD = the Groundshaker on v106 + A STRAY CAPTURE FE OF PLAYER 1's HERO AT 8300 (make_orphan.py), no capture log
#   run-x3: gsE = the same with the stray capture at 6200
# Logs local/sweep/r9/h60.log .., cnE.log, cnF.log, lxD.log, lxE.log, gsD.log, gsE.log; progress chain25.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain25.txt"; }
say "chain25 start"
bash tools/own/r9_chain17.sh test-own-v106-snapB-god-cap h6 &
one() {  # one <name> <sandbox> <port> <pine> <own> <probe> <list> <frames> <snaps> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/$6" FROM=4700 TO=$(( $8 - 100 )) SNAPS="$9" FRAMES=$8 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/${10}" P2S="$O/${11}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$7"
  say "$1 done"
}
SN="5200,8000,11000,14000,17000,19900"
one cnE run-x1 30750 28064 test-own-v103f-snapB sp_probe.py "$L/list-nm63.txt" 16000 "5200,6000,6500,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900" cannon_p1.txt cannon_p2.txt &
one cnF run-x2 30950 28065 test-own-v103f-snapB cam_probe.py "$L/list-nm63.txt" 9000 "5200,6000,6500,7000,7500,8000,8900" cannon_p1.txt cannon_p2.txt &
one lxD run-x5 31550 28068 test-own-v106-snapB-god-cap cap_log_probe2.py "$B/list-eh14d.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
one lxE run-v3c 30550 28063 test-own-v103-snapB-god-cap cap_log_probe2.py "$B/list-eh14d.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
one gsD run-x6 31750 28069 test-own-v106-snapB-god-orph83 cap_log_probe2.py "$L/list-lk15.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
one gsE run-x3 31150 28066 test-own-v106-snapB-god-orph62 cap_log_probe2.py "$L/list-lk15.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
wait
say "chain25 through"
