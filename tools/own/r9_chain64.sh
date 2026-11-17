#!/bin/bash
# TEST ONLY (ninth round): THE REST OF THE 40 FIGHTS of r9_chain62.sh (tag rs4) ON TEN LANES, after the whole regression is through
# and r9_chain62.sh was stopped. The fights already in local/sweep/r9/rs40.log / rs41.log are left out; the rest is dealt to ten
# workers rs40 .. rs49 (a worker skips what its log already has). Same settings as r9_chain62.sh.
# usage: r9_chain64.sh <own kit> <tag>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=$1; TG=$2
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain64.txt"; }
say "chain64 start ($OWN, $TG)"
cat "$B"/$TG[0-9].log 2>/dev/null | grep "ession closed" | awk '{print $1" "$2" "$3" "}' > "$B/done-$TG.txt"
grep -v -F -f "$B/done-$TG.txt" "$B/list-$TG-all.txt" > "$B/rest-$TG.txt" || true
say "chain64: $(wc -l < "$B/rest-$TG.txt") fights left"
for k in 0 1 2 3 4 5 6 7 8 9; do awk -v k=$k 'NR % 10 == k' "$B/rest-$TG.txt" > "$B/list-$TG-r$k.txt"; done
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-r$1.txt"
  say "$TG$1 done"
}
lane 0 run-x5 31550 28068 &
lane 1 run-x6 31750 28069 &
lane 2 run-m 29050 28081 &
lane 3 run-v3 30150 28061 &
lane 4 run-v3b 30350 28062 &
lane 5 run-v3c 30550 28063 &
lane 6 run-x1 30750 28064 &
lane 7 run-x2 30950 28065 &
lane 8 run-x3 31150 28066 &
lane 9 run-x4 31350 28067 &
wait
say "chain64 through ($TG)"
