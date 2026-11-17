#!/bin/bash
# TEST ONLY (eighth round, the vehicle items): THE FIFTY-SECOND GLUE (--carpet2, candidate v76 = v74 + that glue):
# a second carpet under player 2's hero. The v5 test disc (two carpet riders), three carpet missions: the fight
# al14 86, Jafar al05 62, the race al14 100. Both players move and attack (sp_p1 / sp_p2). Probe sp_probe.py (both
# heroes' places and HP); pictures every 250 frames. Read: the pictures (two carpets?), in sync, the fault line count.
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/carp2.log; progress chain85.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain85.txt"; }
say "chain85 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,5250,5500,5750,6000,6250,6500,6750,7000,7500,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8carp2 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh carp2 run-m 29050 28081 test-own-v76-snapB "$L/list-carp3.txt"
say "carp2 done"
say "chain85 through"
