#!/bin/bash
# TEST ONLY (eighth round, job 10): Luxord (eh14 58). In run lux (candidate v52) player 2's hero showed the SAME action
# word 0xFE at every picture from 6000 to 23900. Is that the candidate or the game / build 12?
#   luxc  THE CONTROL: build 12 (test-own-v33-snapB-god-strong), the action timeline of both heroes, 12,000 frames
#   lux2  candidate v52, the same
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/luxc.log, lux2.log; progress chain37.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain37.txt"; }
say "chain37 start"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
for kv in "luxc test-own-v33-snapB-god-strong" "lux2 test-own-v52-snapB-god-strong"; do set -- $kv
  PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 run-m 29050 28081 $2 "$L/list-lux.txt"
  say "$1 done"
done
say "chain37 through"
