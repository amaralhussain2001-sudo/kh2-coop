#!/bin/bash
# TEST ONLY (ninth round, job 3): THE 40 "RUN / SWEEP" FIGHTS OF docs\ROW9-PAIRED-MOVES.md ON THE LAST CANDIDATE (v112: the sixty-fifth glue's
# fourth form), with the capture log (kit -snapB-god-cap, probe cap_log_probe2.py), 20,000 frames each, both players Circle / Triangle / R1.
# Two lanes (run-x5, run-x6: the whole regression has the other eight). usage: r9_chain43.sh [<own>] [<tag>]
# Logs local/sweep/r9/<tag>0.log, <tag>1.log; timelines local/tests/r9<tag>-*-probe.txt (holdstat.py); progress chain43.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v112-snapB-god-cap}; TG=${2:-rs2}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain43.txt"; }
say "chain43 start ($OWN, $TG)"
cat "$B/list-r9s-0.txt" "$B/list-r9s-2.txt" > "$B/list-$TG-0.txt"
cat "$B/list-r9s-1.txt" "$B/list-r9s-3.txt" > "$B/list-$TG-1.txt"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-$TG-$1.txt"
  say "$TG$1 done"
}
lane 0 run-x5 31550 28068 &
lane 1 run-x6 31750 28069 &
wait
say "chain43 through ($TG)"
