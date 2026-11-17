#!/bin/bash
# TEST ONLY (ninth round, job 7): THE 40 "RUN / SWEEP" FIGHTS OF docs\ROW9-PAIRED-MOVES.md ON THE LAST CANDIDATE (v115), with the capture log,
# 20,000 frames each, both players Circle / Triangle / R1, HP held. EIGHT lanes (the regression's sandboxes), started when the whole
# regression that is running is through (the count of "ALL EIGHT THROUGH" lines in local/reg-par8.log goes above <countNow>).
# usage: r9_chain47.sh <countNow> [<own>] [<tag>]   Logs local/sweep/r9/<tag>0.log .. 7.log; timelines local/tests/r9<tag>-*-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
N0=$1; OWN=${2:-test-own-v115-snapB-god-cap}; TG=${3:-rs3}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain47.txt"; }
say "chain47 waits for the regression"
while [ "$(grep -c 'ALL EIGHT THROUGH' "$P/local/reg-par8.log")" -le "$N0" ]; do sleep 5; done
say "chain47 start ($OWN, $TG)"
cat "$B"/list-r9s-0.txt "$B"/list-r9s-1.txt "$B"/list-r9s-2.txt "$B"/list-r9s-3.txt > "$B/list-$TG-all.txt"
for k in 0 1 2 3 4 5 6 7; do awk -v k=$k 'NR % 8 == k' "$B/list-$TG-all.txt" > "$B/list-$TG-$k.txt"; done
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-$1.txt"
  say "$TG$1 done"
}
lane 0 run-m 29050 28081 &
lane 1 run-v3 30150 28061 &
lane 2 run-v3b 30350 28062 &
lane 3 run-v3c 30550 28063 &
lane 4 run-x1 30750 28064 &
lane 5 run-x2 30950 28065 &
lane 6 run-x3 31150 28066 &
lane 7 run-x4 31350 28067 &
wait
say "chain47 through ($TG)"
