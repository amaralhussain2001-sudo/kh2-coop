#!/bin/bash
# TEST ONLY (ninth round, jobs 3 and 4), one lane (run-v3c):
#   gsC  = THE GROUNDSHAKER'S FAULT IN ITS OWN RUN, WITH THE CAPTURE LOG: lk15 59 on the old candidate v89 (the run r8r9h of part 81,
#          in which player 1's free hero got FE at 8650 and stayed held) + the capture recorder (make_rec_cap3.py), probe cap_log_probe.py
#   lxC  = DATA LUXORD, THE ONE-HERO NO-PATCH CONTROL (patches/test-empty-god = no patch + HP held; the plain disc; player 2 idle):
#          how long does the game itself keep the hero in the captured motion FE of the fight's start
# Logs local/sweep/r9/gsC.log, lxC.log; timelines local/tests/r9gsC-*-probe.txt, r9lxC-*-probe.txt; progress chain18.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain18.txt"; }
say "chain18 start"
ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9gsC P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh gsC run-v3c 30550 28063 test-own-v89-snapB-god-cap "$L/list-lk15.txt"
say "gsC done"
ISO=test-s1-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9lxC P1S="$O/mashrc_long_p1.txt" P2S="$S/idle_p2.txt" bash tools/own/sweep4.sh lxC run-v3c 30550 28063 test-empty-god "$B/list-eh14d.txt"
say "lxC done"
say "chain18 through"
