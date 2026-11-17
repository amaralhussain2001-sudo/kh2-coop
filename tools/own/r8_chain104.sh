#!/bin/bash
# TEST ONLY (eighth round, the toy cannon with two cannons): WHO HANDS A MISSING HP RECORD TO THE LOW-HP TEST at the
# game's end (run one10: 50 fault lines at pc 0x001A2478 from about frame 38,400). Candidate v88 + the recorder of
# bad calls (make_rec_bad.py at 0x001A2478), the v5 test disc, the same scripts, 40,000 frames.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/one12.log; progress chain104.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain104.txt"; }
say "chain104 start"
ISO=test-v5-tt137.iso PROBE="$T/recbad_probe.py" SNAPS="36000,38000,38600,39900" FRAMES=40000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8one12 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one12 run-m 29050 28081 test-own-v88-lowrec "$L/list-nm63.txt"
say "one12 done"
say "chain104 through"
