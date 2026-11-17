#!/bin/bash
# TEST ONLY (ninth round): CANDIDATE v107 (the sixty-fifth glue's fourth form + the toy cannon's own views), ten lanes:
#   run-v3, run-v3b, run-x4, run-m: the ten boss rooms with the capture log (r9_chain17.sh test-own-v107-snapB-god-cap h7)
#   run-x1: stA = THE TOY CANNON ENTERED FROM THE STORY (room nm10, event program 22), the cannon scripts, 30,000 frames
#   run-x2: stB = THE CARPET ESCAPE FROM THE STORY (room al11, event program 10)      run-x3: stC = THE SIDECAR FROM THE STORY (room eh29, event program 93)
#   run-x5: gsG = the Groundshaker + a stray capture FE of player 1's hero at 8300 (it must not be made while player 2 rides)
#   run-x6: gsH = the same at 6200 (both free: a pair of two orphans: the two nets must let both go)
#   run-v3c: lxI = Data Luxord (eh14 101) with the capture log
# Logs local/sweep/r9/h70.log .., stA.log, stB.log, stC.log, gsG.log, gsH.log, lxI.log; progress chain33.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain33.txt"; }
say "chain33 start"
bash tools/own/r9_chain17.sh test-own-v107-snapB-god-cap h7 &
one() {  # one <name> <sandbox> <port> <pine> <own> <probe> <list> <frames> <snaps> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/$6" FROM=4700 TO=$(( $8 - 100 )) SNAPS="$9" FRAMES=$8 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/${10}" P2S="$O/${11}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$7"
  say "$1 done"
}
SN="5200,8000,11000,14000,17000,19900"
ST=$(python -c "print(','.join(str(f) for f in range(5000, 30000, 1000)) + ',29900')")
one stA run-x1 30750 28064 test-own-v107-snapB sp_probe.py "$B/list-st-nm10.txt" 30000 "$ST" cannon_p1.txt cannon_p2.txt &
one stB run-x2 30950 28065 test-own-v107-snapB sp_probe.py "$B/list-st-al11.txt" 30000 "$ST" mashrc_long_p1.txt mashrc_long_p2.txt &
one stC run-x3 31150 28066 test-own-v107-snapB sp_probe.py "$B/list-st-eh29.txt" 30000 "$ST" mashrc_long_p1.txt mashrc_long_p2.txt &
one gsG run-x5 31550 28068 test-own-v107-snapB-god-orph83 cap_log_probe2.py "$L/list-lk15.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
one gsH run-x6 31750 28069 test-own-v107-snapB-god-orph62 cap_log_probe2.py "$L/list-lk15.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
one lxI run-v3c 30550 28063 test-own-v107-snapB-god-cap cap_log_probe2.py "$B/list-eh14d.txt" 20000 "$SN" mashrc_long_p1.txt mashrc_long_p2.txt &
wait
say "chain33 through"
