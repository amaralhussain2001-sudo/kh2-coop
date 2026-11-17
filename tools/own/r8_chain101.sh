#!/bin/bash
# TEST ONLY (eighth round, the toy cannon with two cannons): THE END OF THE GAME. Candidate v88, the v5 test disc,
# nm10 63, 60,000 frames; both players fire all the time, reload and sweep the aim (cannon_p1 / cannon_p2).
# Read: does the score reach its goal, what comes then (the room, the mission word), in sync, the fault lines.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/one10.log; progress chain101.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain101.txt"; }
say "chain101 start"
SN=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN FRAMES=60000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/b15 TAG=r8one10 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one10 run-m 29050 28081 test-own-v88-snapB "$L/list-nm63.txt"
say "one10 done"
say "chain101 through"
