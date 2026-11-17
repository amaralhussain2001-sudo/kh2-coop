#!/bin/bash
# TEST ONLY (eighth round): candidate v58 (build 14?), the things beside the bosses that the forty-seventh glue
# touches (a hero's Reaction Command and its callback):
#   mkS5   Storm Rider, both heroes fall, a King Mickey for each, Healing Light (the rescue must stay as it is)
#   chest3 player 2 opens a chest (his Triangle on the chest's command)
#   sam3   the Dusk's "Reversal" by player 2 alone (HP held)
#   sam4   the same fight, BOTH players press Triangle and Circle (one Dusk, two heroes on its command)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain51.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain51.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain51 start"
M2="5200,6400,6700,6900,7000,7400,8000,8500,8900,9500,10000,11000,11900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$M2 FRAMES=12000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkS5 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS5 run-m 29050 28081 test-own-v58-snapB-kill65-roll-abort "$L/list-sr1.txt"
tlb mkS5; say "mkS5 done"
PROBE="$P/tools/own/pos_probe.py" POINTS="1116:-23" SNAPS="4690,4880,4950,5000,5100,5200,5400,5700" FRAMES=6000 LOGDIR=local/sweep/b15 TAG=r8chest3 \
  P1S="$O/ctl_p1.txt" P2S="$O/chest2_p2.txt" bash tools/own/sweep4.sh chest3 run-m 29050 28081 test-own-v58 "$L/list-chest.txt"
tlb chest3; say "chest3 done"
SNAPS="5200,5300,5400,5500,5600,5700,5800,5900,6000,6200,6400,6700,7000,7500,8000,8900" LOGDIR=local/sweep/b15 TAG=r8sam3 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh sam3 run-m 29050 28081 test-own-v58-snapB-god "$L/list-hb08b.txt"
tlb sam3; say "sam3 done"
SNAPS="5200,5300,5400,5500,5600,5700,5800,5900,6000,6200,6400,6700,7000,7500,8000,8900" LOGDIR=local/sweep/b15 TAG=r8sam4 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh sam4 run-m 29050 28081 test-own-v58-snapB-god "$L/list-hb08b.txt"
tlb sam4; say "sam4 done"
say "chain51 through"
