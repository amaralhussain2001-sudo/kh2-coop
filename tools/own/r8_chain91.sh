#!/bin/bash
# TEST ONLY (eighth round): the second carpet after a GAME OVER and "Continue" (final candidate v81, kit -die2: both
# heroes' HP held at 1, so the first hits end the fight). The v5 test disc, the carpet fight al14 86, 14,000
# frames, both players move and attack (their Circle answers the Game Over menu). Read: after the Continue, are
# there two carpets again, in sync, the fault line count.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/carp4.log; progress chain91.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain91.txt"; }
say "chain91 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,13900" FRAMES=14000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8carp4 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh carp4 run-m 29050 28081 test-own-v81-snapB-die2 "$L/list-carp86b.txt"
say "carp4 done"
say "chain91 through"
