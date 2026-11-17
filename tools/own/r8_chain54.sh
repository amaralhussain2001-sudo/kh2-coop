#!/bin/bash
# TEST ONLY (eighth round): candidate v58, the Dusk's "Reversal" (an ordinary enemy's Reaction Command), which
# r8_chain51.sh did NOT run: its run names sam3 / sam4 were names of older runs and the sweep script skips a name
# that has a log already.
#   dsk1   the Dusk's "Reversal" by player 2 alone (HP held)
#   dsk2   the same fight, BOTH players press Triangle and Circle in the same frames
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain54.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain54.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain54 start"
SN="5200,5300,5400,5500,5600,5700,5800,5900,6000,6200,6400,6700,7000,7500,8000,8900"
SNAPS=$SN LOGDIR=local/sweep/b15 TAG=r8dsk1 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh dsk1 run-m 29050 28081 test-own-v58-snapB-god "$L/list-hb08b.txt"
tlb dsk1; say "dsk1 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=8900 SNAPS=$SN FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8dsk2 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh dsk2 run-m 29050 28081 test-own-v58-snapB-god "$L/list-hb08b.txt"
tlb dsk2; say "dsk2 done"
say "chain54 through"
