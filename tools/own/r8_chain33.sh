#!/bin/bash
# TEST ONLY (eighth round, plan row 45): King Mickey for two, candidate v51 (thirty-seventh glue, third version: the
# rescue's end is safe against the second Mickey's own call).
#   mkH2  THE HYDRA's room again (run mkH stopped at the rescue's end: "pc 0x00179F10"), with the heap recorder
#   mkC2  two rescues one after the other (run mkC had 50 fault lines: their addresses are kept this time)
#   mkD   KING MICKEY FALLS at 8000 while two Mickeys play (kit make_mkkill.py): what the game does
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/mkH2.log, mkC2.log, mkD.log (+ -tlb.txt); progress chain33.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain33.txt"; }
say "chain33 start"
M2="5200,6400,6700,6900,7000,7400,8000,8500,8900,9500,10000,10500,11000,11200,11400,11600,11900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14,000F1F80:40 SNAPS=$M2 FRAMES=12000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkH2 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkH2 run-m 29050 28081 test-own-v51-snapB-kill65-roll-heap-abort "$L/list-hy1.txt"
grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -80 > "$B/mkH2-tlb.txt"
say "mkH2 done"
MS="5200,6400,6700,6900,7000,7400,7700,7900,8000,8100,8200,8400,8700,9000,9500,10000,10400,10700,10900,11000,11400,12000,13000,14000,15000,15900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$MS FRAMES=16000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkC2 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkC2 run-m 29050 28081 test-own-v51-snapB-killx-roll-abort "$L/list-sy.txt"
grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -80 > "$B/mkC2-tlb.txt"
say "mkC2 done"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$MS FRAMES=16000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkD P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkD run-m 29050 28081 test-own-v51-snapB-kill65-roll-abort-mk80 "$L/list-sy.txt"
grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -80 > "$B/mkD-tlb.txt"
say "mkD done"
say "chain33 through"
