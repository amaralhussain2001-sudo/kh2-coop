#!/bin/bash
# TEST ONLY (eighth round, plan row 44), candidate v50 (glues 30 to 43):
#   tf8b  Limit Form + Final once more: the ONE fault line of run tf8, with its address
#   fd2   BOTH heroes in a form through a door (player 1 Limit Form, player 2 Final; Merlin's House -> the Borough)
#   hyf   a second form in THE HYDRA'S ROOM (the tightest room): player 1 Valor, player 2 his first row; the file pool
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/tf8b.log, fd2.log, hyf.log; progress chain32.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain32.txt"; }
say "chain32 start"
TF="4690,5000,5380,5540,5650,5700,5900,6300,6480,6600,6700,6780,6950,7100,7280,7400,7600,7900"
PROBE="$T/heap_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tf8b "$P/patches/test-own-v50-forms-heap-abort" test-s1-hb9f.iso 8000 "$TF" "$O/limitf2_p1.txt" "$O/finalf2_p2.txt" run-m 29050 28081 > "$B/tf8b.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tf8b.log"
grep -a -B3 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 >> "$B/tf8b.log"
cat "$P/local/tests/t15-tf8b-probe.txt" >> "$B/tf8b.log" 2>/dev/null
say "tf8b done"
FS="4690,5000,5250,5380,5600,5800,6000,6100,6230,6260,6450,6630,6660,6900,7100,7350"
PROBE="$T/sweep_probe.py" bash tools/own/dusk_one.sh t15-fd2 "$P/patches/test-own-v50-forms" test-s1-hb13s.iso 7400 "$FS" "$O/formdoor2_p1.txt" "$O/finaldoor3_p2.txt" run-m 29050 28081 > "$B/fd2.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/fd2.log"
grep -a -B3 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 >> "$B/fd2.log"
cat "$P/local/tests/t15-fd2-probe.txt" >> "$B/fd2.log" 2>/dev/null
say "fd2 done"
PROBE="$T/filepool_probe.py" LOW=4000 SNAPS="4690,5000,5380,5540,5700,5900,6300" FRAMES=6500 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8hyf P1S="$O/twoforms_p1.txt" P2S="$O/twoforms_p2.txt" bash tools/own/sweep4.sh hyf run-m 29050 28081 test-own-v50-snapB-forms-abort "$L/list-hy1.txt"
say "hyf done"
say "chain32 through"
