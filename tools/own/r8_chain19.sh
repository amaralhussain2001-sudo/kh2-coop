#!/bin/bash
# TEST ONLY (eighth round, plan row 45): King Mickey for two, candidate v42 (the hardened thirty-seventh glue).
#   mkC  Shan-Yu: both fall at 6500 (two Mickeys), player 1's Mickey loses all HP at 8000 (what does the game do?),
#        both heroes fall again at 10500 (a second rescue after whatever came). 16,000 frames.
#   mkH  THE HYDRA (the room with the least free memory), with the heap recorder: both fall at 6500.
#   mkS  Storm Rider: both fall at 6500.
# Words after " | ": engine player and parking place, the twin, the parked twin, the abort recorder (, the heap block).
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain19.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain19.txt"; }
say "chain19 start"
MS="5200,6400,6700,6900,7000,7400,7700,7900,8000,8100,8200,8400,8700,9000,9500,10000,10400,10700,10900,11000,11400,12000,13000,14000,15000,15900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$MS FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8mkC P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkC run-m 29050 28081 test-own-v42-snapB-killx-roll-abort "$L/list-sy.txt"
say "mkC done"
M2="5200,6400,6700,6900,7000,7400,8000,8500,8900,9500,10000,11000,11900"
echo "he18 06 171 HE18_MS108 DEFAULT 171 171 171 0" > "$L/list-hy1.txt"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14,000F1F80:40 SNAPS=$M2 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8mkH P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkH run-m 29050 28081 test-own-v42-snapB-kill65-roll-heap-abort "$L/list-hy1.txt"
say "mkH done"
echo "mu08 08 79 MU08_MS204 W_FRIEND 79 79 79 0" > "$L/list-sr1.txt"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$M2 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8mkS P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS run-m 29050 28081 test-own-v42-snapB-kill65-roll-abort "$L/list-sr1.txt"
say "mkS done"
say "chain19 through"
