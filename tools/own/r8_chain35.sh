#!/bin/bash
# TEST ONLY (eighth round, plan row 44), candidate v50:
#   fd3   BOTH heroes in a form through a door (player 1 Limit Form at 4870, player 2 Final at 5220, the door at about 5700)
#   hyf2  THE HYDRA'S ROOM: player 2 takes Valor at 5560 (about 0.96 MB of the file pool stay free); player 1 opens his
#         Drive list at 6100: every other form must be DIM ("no room"), his Circle at 6200 must do nothing
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/fd3.log, hyf2.log; progress chain35.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain35.txt"; }
say "chain35 start"
FS="4690,5000,5250,5450,5650,5800,5900,6000,6100,6300,6450,6500,6700,6900,7100,7350"
PROBE="$T/sweep_probe.py" bash tools/own/dusk_one.sh t15-fd3 "$P/patches/test-own-v50-forms" test-s1-hb13s.iso 7400 "$FS" "$O/formdoor3_p1.txt" "$O/formdoor3_p2.txt" run-m 29050 28081 > "$B/fd3.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/fd3.log"
grep -a 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -10 >> "$B/fd3.log"
cat "$P/local/tests/t15-fd3-probe.txt" >> "$B/fd3.log" 2>/dev/null
say "fd3 done"
PROBE="$T/filepool_probe.py" LOW=4000 SNAPS="4690,5540,5900,6150,6190,6300,6450" FRAMES=6500 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8hyf2 P1S="$O/hyf2_p1.txt" P2S="$O/twoforms_p2.txt" bash tools/own/sweep4.sh hyf2 run-m 29050 28081 test-own-v50-snapB-forms-abort "$L/list-hy1.txt"
say "hyf2 done"
say "chain35 through"
