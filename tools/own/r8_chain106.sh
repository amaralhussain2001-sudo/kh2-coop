#!/bin/bash
# TEST ONLY (eighth round, part 77): WHOSE HP DOES PLAYER 1's GAUGE SHOW when the second hero is made at run time.
# Candidate v88 (= the build 17 patch), the v5 test disc: the carpet escape and the sidecar (list-one2), then the
# toy cannon (list-nm63); probe hud_probe.py = the HUD's party table beside both heroes.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/one14.log, one15.log; progress chain106.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain106.txt"; }
say "chain106 start"
ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one14 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one14 run-m 29050 28081 test-own-v88-snapB "$L/list-one2.txt"
say "one14 done"
ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one15 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one15 run-m 29050 28081 test-own-v88-snapB "$L/list-nm63.txt"
say "one15 done"
say "chain106 through"
