#!/bin/bash
# TEST ONLY (ninth round, plan row 9, job 3): THE TEN BOSS ROOMS WITH THE SIXTY-FIFTH GLUE (--holdpair: both heroes inside the same
# hold of a boss). Candidate v104 with HP held at 150 (kit -snapB-god), the v5 test disc, 20,000 frames each, both players
# Circle / Triangle / R1 (mashrc_long), probe act_poll_probe.py (a captured motion shows as action FC .. FF).
# Four lanes: run-m, run-v3, run-v3b, run-x4. usage: bash tools/own/r9_chain17.sh [<ownPatchDirName>] [<tag>]
# Logs local/sweep/r9/<tag>0.log .. 3.log, timelines local/tests/r9<tag>-*-probe.txt (read: tools/own/holdsum.py); progress chain17.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v104-snapB-god-cap}; TG=${2:-h4}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain17.txt"; }
say "chain17 start ($OWN, $TG)"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$TG P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $TG$1 $2 $3 $4 "$OWN" "$B/list-r9h-$1.txt"
  say "$TG$1 done"
}
lane 0 run-v3 30150 28061 &
lane 1 run-v3b 30350 28062 &
lane 2 run-x4 31350 28067 &
(while ! grep -q "chain15 through" "$B/chain15.txt"; do sleep 5; done; lane 3 run-m 29050 28081) &
wait
say "chain17 through ($TG)"
