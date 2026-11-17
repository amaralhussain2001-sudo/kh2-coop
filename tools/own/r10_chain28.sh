#!/bin/bash
# TEST ONLY (tenth round): THE 40 FIGHTS (list list-<tag>-all.txt = rs5's) ON SIX LANES run-x5 .. run-x10, beside the whole regression
# (which takes the eight other sandboxes). Same settings as r9_chain64.sh (20,000 frames, capture log, both press).
# usage: r10_chain28.sh <own kit> <tag>     read with: python -I tools/own/row9_rs2.py --tags=<tag>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=$1; TG=$2
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/r10chain28.txt"; }
say "r10chain28 start ($OWN, $TG)"
cat "$B"/$TG[0-9].log 2>/dev/null | grep "ession closed" | awk '{print $1" "$2" "$3" "}' > "$B/done-$TG.txt"
grep -v -F -f "$B/done-$TG.txt" "$B/list-$TG-all.txt" > "$B/rest-$TG.txt" || true
say "r10chain28: $(wc -l < "$B/rest-$TG.txt") fights left"
for k in 0 1 2 3 4 5; do awk -v k=$k 'NR % 6 == k' "$B/rest-$TG.txt" > "$B/list-$TG-r$k.txt"; done
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-r$1.txt"
  say "$TG$1 done"
}
lane 0 run-x5 31550 28068 &
lane 1 run-x6 31750 28069 &
lane 2 run-x7 31950 28070 &
lane 3 run-x8 32150 28071 &
lane 4 run-x9 32350 28072 &
lane 5 run-x10 32550 28073 &
wait
say "r10chain28 through ($TG)"

