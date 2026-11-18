#!/bin/bash
# TEST ONLY (part 147, glue 84 --partnerview): disc test-v5-tt137 jump to nm10, kits -acc (snapB + make_once 4300: Medal 0x35 in
# the hero's accessory place 1 (0x0032E044), Soldier Earring 0x28 in player 2's place 5 (0x0032E04C)).
#   pvA run-x5 candidate: player 1 L2+START (his partner view), player 2 holds the stick right meanwhile
#   pvB run-x6 candidate: player 2 L2+START (his partner view)
#   pvN run-x7 candidate: player 2 START without L2 (his own menu, as before)
#   pv0 run-x8 control merged-v22-own (build 30): player 1 L2+START = his own menu (L2 means nothing there)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="6150,6300,6500,6700,6800,7000,7300"
export RANGES="0032E020:60,0032F228:8,000E7E20:C,000DD800:4,0032DF70:4,0032E35C:60" CHAINS="000F05CC+70:4,000F05CC+78:4"
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/memdump_probe.py" SNAPS="$SN" FRAMES=7400 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r14 TAG=r14$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one pvA run-x5 31550 28068 test-own-pv1-acc pv_view_p1.txt pv_right_p2.txt "$B/list-st-nm10.txt" &
one pvB run-x6 31750 28069 test-own-pv1-acc pv_idle_p1.txt pv_view_p2.txt "$B/list-st-nm10.txt" &
one pvN run-x7 31950 28070 test-own-pv1-acc pv_idle_p1.txt pv_own_p2.txt "$B/list-st-nm10.txt" &
one pv0 run-x8 32150 28071 merged-v22-own-acc pv_view_p1.txt pv_right_p2.txt "$B/list-st-nm10.txt" &
wait
echo "r14 chain1 done" >> local/sweep/r14/chain1.txt
