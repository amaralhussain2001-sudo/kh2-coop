#!/bin/bash
# TEST ONLY (eighth round, the toy cannon with two cannons): WHO PUTS THE FIRST CANNON INTO THE HUD'S PARTY TABLE at
# the game's end (run one12: player 1's own gauge refreshes with the cannon, which has no HP record). Candidate v88
# + the recorder at the table's "set a slot" routine 0x0013DC38 (ring: return address, slot index, object, frame),
# the v5 test disc, the same scripts, stopped at 38,700 frames so that the ring still holds the game's end.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/one13.log; progress chain105.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain105.txt"; }
say "chain105 start"
ISO=test-v5-tt137.iso PROBE="$T/rec_probe.py" SNAPS="6000,38000,38500,38600,38690" FRAMES=38700 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8one13 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one13 run-m 29050 28081 test-own-v88-setrec "$L/list-nm63.txt"
say "one13 done"
say "chain105 through"
