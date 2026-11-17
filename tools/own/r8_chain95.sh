#!/bin/bash
# TEST ONLY (eighth round, the three one-hero small games): candidate v86 = build 16 + the glues 53 to 56 (56 in its
# second form: the toy cannon too) on the v5 test disc (ONE hero in these rooms; the second is made at run time).
#   one4  the toy cannon nm10 63, the carpet escape al14 61, the sidecar eh22 72: 9,000 frames each
#   one5  the escape and the sidecar, 16,000 frames: how do they end with two heroes
#   one6  the escape and the sidecar with both heroes' HP held at 1 (kit -die2), 14,000 frames: what happens when a
#         hero is beaten there, and after "Continue"
# Both players move and press (sp_p1 / sp_p2). Probe sp_probe.py. ONE RUN AT A TIME, hidden, sandbox run-m.
# Logs local/sweep/b15/one4.log, one5.log, one6.log; progress chain95.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain95.txt"; }
say "chain95 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one4 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one4 run-m 29050 28081 test-own-v86-snapB "$L/list-one3.txt"
say "one4 done"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900" FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8one5 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one5 run-m 29050 28081 test-own-v86-snapB "$L/list-one2.txt"
say "one5 done"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,5500,6000,6500,7000,7500,8000,9000,10000,11000,12000,13000,13900" FRAMES=14000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8one6 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one6 run-m 29050 28081 test-own-v86-snapB-die2 "$L/list-one2.txt"
say "one6 done"
say "chain95 through"
