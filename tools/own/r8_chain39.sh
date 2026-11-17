#!/bin/bash
# TEST ONLY (eighth round, job 10): Luxord (eh14 58) with candidate v52 once more: the FOUR fault lines of runs lux / lux2
# (build 12 has none in this fight), with their addresses. 7,000 frames are enough (the lines come early).
# ONE RUN on sandbox run-m. Log: local/sweep/b15/lux3.log, lux3-tlb.txt; progress chain39.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain39.txt"; }
say "chain39 start"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=6900 SNAPS="5000,5080,5100,5130,5200,5400,6000,6900" FRAMES=7000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux3 run-m 29050 28081 test-own-v52-snapB-god-strong "$L/list-lux.txt"
grep -a -B3 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -40 > "$B/lux3-tlb.txt"
say "lux3 done"
say "chain39 through"
