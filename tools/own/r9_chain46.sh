#!/bin/bash
# TEST ONLY (ninth round, job 7): THE TEN BOSS ROOMS ON THE LAST CANDIDATE (v113), with the capture log, 20,000 frames each, both players
# Circle / Triangle / R1, HP held. Two lanes (run-x5, run-x6), started when r9_chain43.sh (the 40 fights) is through.
# usage: r9_chain46.sh [<own>] [<tag>]     Logs local/sweep/r9/<tag>0.log, <tag>1.log; timelines local/tests/r9<tag>-*-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v113-snapB-god-cap}; TG=${2:-h9}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain46.txt"; }
say "chain46 waits for chain43"
while ! grep -q "chain43 through" "$B/chain43.txt"; do sleep 5; done
say "chain46 start ($OWN, $TG)"
cat "$B/list-r9h-0.txt" "$B/list-r9h-2.txt" > "$B/list-$TG-0.txt"
cat "$B/list-r9h-1.txt" "$B/list-r9h-3.txt" > "$B/list-$TG-1.txt"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-$1.txt"
  say "$TG$1 done"
}
lane 0 run-x5 31550 28068 &
lane 1 run-x6 31750 28069 &
wait
say "chain46 through ($TG)"
