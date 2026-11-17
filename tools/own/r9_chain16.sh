#!/bin/bash
# TEST ONLY (ninth round, job 4: the Groundshaker's lost hold): lk15 59 with the capture log (kit -snapB-god-cap = HP held at 150 +
# tools/own/make_rec_cap3.py), probe tools/own/cap_log_probe.py, 20,000 frames, both players Circle / Triangle / R1 (mashrc_long).
#   gsA = candidate v103 (no hold glue): who sends the capture that takes the free hero
#   gsB = candidate v104 (the sixty-fifth glue --holdpair): the same fight
# One lane: run-x4. Logs local/sweep/r9/gsA.log, gsB.log; timelines local/tests/r9gsA-*-probe.txt; progress chain16.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain16.txt"; }
say "chain16 start"
run() {  # run <name> <ownPatch>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 run-x4 31350 28067 "$2" "$L/list-lk15.txt"
  say "$1 done"
}
run gsA test-own-v103-snapB-god-cap
run gsB test-own-v104-snapB-god-cap
say "chain16 through"
