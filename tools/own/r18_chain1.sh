#!/bin/bash
# TEST ONLY (part 152, glue 86 --hullgauges): (1) hgR8 candidate test-own-hg1 Gummi route 8 (both fire and weave, lane S3's
# scripts), (2) ctR8 control merged-v26-own route 8 (the probe lines of both are compared: score / hulls must be the same at
# every snapshot; build 19 ends with 90,939), (3) hgH0 candidate route 0, player 1 weaves and fires, player 2 idles: ship 2 is hit,
# gauge 2 must drop. Probe tools/own/hg_probe.py (G2, pool, places; before the flight: pool B memory must be zero).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; S="$P/tests/scripts/lane-s3"; cd "$P" || exit 1
SN=$(python -c "print('4000,6000,' + ','.join(str(f) for f in range(8000, 40000, 2000)) + ',39900')")
SH="4000,6000,9000,10000,11000,12000,13000,14000,15000,15900"
run() { PROBE="$P/tools/own/hg_probe.py" bash tools/own/dusk_one.sh "$1" "$P/patches/$2" test-s1-tt137.iso "$3" "$4" "$S/$5" "$S/$6" "$7" "$8" "$9" > "local/sweep/r18/$1.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' "$P/local/$7/p1/logs/emulog.txt")" >> "local/sweep/r18/$1.log"; }
run r18-hgR8 test-own-hg1-gum8 40000 "$SN" gb_p1_fight.txt gb_p2_fight.txt run-x5 31550 28068 &
run r18-ctR8 merged-v26-own-gum8 40000 "$SN" gb_p1_fight.txt gb_p2_fight.txt run-x6 31750 28069 &
run r18-hgH0 test-own-hg1-gum0 16000 "$SH" gb_p1_fight.txt gb_p2_idle.txt run-x7 31950 28070 &
wait
echo "r18 chain1 done" >> local/sweep/r18/chain1.txt
