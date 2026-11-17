#!/bin/bash
# TEST ONLY (ninth round, job 3): DATA LUXORD'S LONG HOLD OF PLAYER 1'S HERO: THE CAUSE AND THE CURE (the sixty-seventh glue, --trickguard).
#   lxP = eh14 101 on v113 (with the glue), both players mash        -> the cure: the hold must end after about 130 frames
#   lxQ = eh14 101 on v112 (without), PLAYER 2 DOES NOT PRESS         -> the cause: nobody hits Luxord, the hold must end by itself
#   lxR = eh14 58 (the story fight) on v113, both players mash
#   lxS = eh14 101 on v112 (without), both players mash              -> the fault as it was (the same hour, the same kit kind)
# All with the capture log (cap_log_probe2.py), HP held, 16,000 frames.
# usage: r9_chain44.sh <name> <sandbox> <port> <pine>      (one run; start several at once in different sandboxes)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain44.txt"; }
SN="5000,6000,8000,10000,12000,14000,15900"
one() {  # one <name> <sandbox> <port> <pine> <own> <list> <p1> <p2>
  say "$1 start ($2)"
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$7" P2S="$O/$8" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$6"
  say "$1 done"
}
case "$1" in
  lxP) one lxP $2 $3 $4 test-own-v113-snapB-god-cap "$B/list-eh14d.txt" mashrc_long_p1.txt mashrc_long_p2.txt ;;
  lxQ) one lxQ $2 $3 $4 test-own-v112-snapB-god-cap "$B/list-eh14d.txt" mashrc_long_p1.txt idle.txt ;;
  lxR) one lxR $2 $3 $4 test-own-v113-snapB-god-cap "$B/list-eh14s.txt" mashrc_long_p1.txt mashrc_long_p2.txt ;;
  lxS) one lxS $2 $3 $4 test-own-v112-snapB-god-cap "$B/list-eh14d.txt" mashrc_long_p1.txt mashrc_long_p2.txt ;;
  *) echo "which run?"; exit 1 ;;
esac
