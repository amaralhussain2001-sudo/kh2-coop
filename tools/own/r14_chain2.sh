#!/bin/bash
# TEST ONLY (part 147, glue 84 --partnerview): THE LEAK TEST. Abilities page: Circle x3 switches Sora's first ability.
#   lkA run-x5 candidate: player 1 in his partner view tries it      lkB run-x6 candidate: player 2 in his partner view tries it
#   lk0 run-x7 control merged-v22-own: player 1 (L2 means nothing): his own menu, the switch must happen
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="6150,6850,7000,7100,7400,7550"
export RANGES="0032E020:A0,0032E35C:A0,000E7E20:C,000DD800:4,0032F228:8,0032F0B0:40" CHAINS=""
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/memdump_probe.py" SNAPS="$SN" FRAMES=7600 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r14 TAG=r14$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one lkA2 run-x5 31550 28068 test-own-pv1-acc pv_leak_p1.txt pv_idle_p2.txt "$B/list-st-nm10.txt" &
one lkB2 run-x6 31750 28069 test-own-pv1-acc pv_idle2_p1.txt pv_leak_p2.txt "$B/list-st-nm10.txt" &
one lk02 run-x7 31950 28070 merged-v22-own-acc pv_leak_p1.txt pv_idle_p2.txt "$B/list-st-nm10.txt" &
wait
echo "r14 chain2 done" >> local/sweep/r14/chain2.txt
