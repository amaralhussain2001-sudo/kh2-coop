#!/bin/bash
# TEST ONLY (eighth round, the toy cannon): THE CONTROL for run one10 (v88: 50 fault lines at pc 0x001A2478 when the
# cannon's game ends): the same disc, the same scripts, the same 60,000 frames on BUILD 16 (candidate v81: ONE
# cannon, both controllers drive it). Are the fault lines at the game's end there too?
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/one11.log; progress chain103.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain103.txt"; }
say "chain103 start"
SN=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN FRAMES=60000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/b15 TAG=r8one11 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one11 run-m 29050 28081 test-own-v81-snapB "$L/list-nm63.txt"
grep -a "TLB Miss" local/run-m/p1/logs/emulog.txt | sed 's/.*pc=\(0x[0-9a-f]*\) addr=\(0x[0-9a-f]*\).*/\1 \2/' | sort | uniq -c | sort -rn | head -8 >> "$B/chain103.txt"
grep -a -B3 "TLB Miss" local/run-m/p1/logs/emulog.txt | grep -a "stats: frame" | head -2 >> "$B/chain103.txt"
say "one11 done"
say "chain103 through"
