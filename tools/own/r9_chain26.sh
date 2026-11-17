#!/bin/bash
# TEST ONLY (ninth round, job 3): DATA LUXORD (eh14 101): on v103 player 1's hero stays in the captured motion FE of the opening trick
# for a minute (the one-hero no-patch control leaves the trick after 68 frames). Which build brought it: the same run on
#   run-x1: lxF = build 19 (test-own-v94-snapB-god)     run-x2: lxG = v97 (items only)     run-v3c: lxH = v100 (items + Keyblade, first form)
# Probe act_poll_probe.py. Logs local/sweep/r9/lxF.log, lxG.log, lxH.log; progress chain26.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain26.txt"; }
say "chain26 start"
one() {  # one <name> <sandbox> <port> <pine> <own>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,8000,11000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh14d.txt"
  say "$1 done"
}
one lxF run-x1 30750 28064 test-own-v94-snapB-god &
one lxG run-x2 30950 28065 test-own-v97-snapB-god &
one lxH run-v3c 30550 28063 test-own-v100-snapB-god &
wait
say "chain26 through"
