#!/bin/bash
# TEST ONLY (ninth round, items 1 and 4): THE 40 "RUN / SWEEP" FIGHTS (as r9_chain47.sh) ON A CANDIDATE, with the capture log, 20,000 frames
# each, both players Circle / Triangle / R1, HP held. TWO lanes (run-x5, run-x6), so that the whole regression (reg_par8.sh, the
# other eight sandboxes) can run at the same time.
# usage: r9_chain62.sh <own kit> <tag>     Logs local/sweep/r9/<tag>0.log, <tag>1.log; timelines local/tests/r9<tag>-*-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=$1; TG=$2
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain62.txt"; }
say "chain62 start ($OWN, $TG)"
cat "$B"/list-r9s-0.txt "$B"/list-r9s-1.txt "$B"/list-r9s-2.txt "$B"/list-r9s-3.txt > "$B/list-$TG-all.txt"
for k in 0 1; do awk -v k=$k 'NR % 2 == k' "$B/list-$TG-all.txt" > "$B/list-$TG-$k.txt"; done
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-$1.txt"
  say "$TG$1 done"
}
lane 0 run-x5 31550 28068 &
lane 1 run-x6 31750 28069 &
wait
say "chain62 through ($TG)"
