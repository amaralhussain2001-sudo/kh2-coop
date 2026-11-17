#!/bin/bash
# TEST ONLY (eighth round): THE ONE QUEUE. Everything that is still to run, strictly one run after the other, in
# ONE shell (after the mishap of 2026-11-14 00:35: two "wait for the chain before me" shells had started the same
# chain twice and their runs collided on sandbox run-m; never queue with waiting shells again).
# Start it with KH2_TEST_SHOW=1 to see the windows. Progress: local/sweep/b15/master2.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/master2.txt"; }
say "master2 start"
# 1. the Keyblade change with the freed-object recorder at 0x0017FE10 (make_rec_vt.py)
PROBE="$T/recbad_probe.py" SNAPS="5060,5540,5860,6200,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcvt P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" \
  bash tools/own/sweep4.sh kcvt run-m 29050 28081 test-own-v33-menu-vt "$L/list-hb13.txt"
say "kcvt done"
for c in 8 11 12 13 14 10 7 6; do
  say "chain $c start"
  bash "tools/own/r8_chain$c.sh"
  say "chain $c done"
done
say "master2 through"
