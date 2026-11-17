#!/bin/bash
# TEST ONLY (eighth round, plan row 9, the other fights): DOES THE BOSS'S FORCED MOVE (a hold, a throw) TAKE A HERO
# AND LET HIM GO AGAIN WITH TWO HEROES. Ten boss rooms (local/sweep/list-r9h.txt: the Dark Thorn, Cerberus, Scar,
# Xaldin, Demyx twice, the Hydra, the Groundshaker, the last Xemnas, the armoured Xemnas), candidate v89 with HP
# held at 150 (kit -snapB-god; level 1 strength, so the boss lives), the v5 test disc, 20,000 frames each; both
# players press Circle / Triangle / R1 (mashrc_long). Probe act_poll_probe.py: a line whenever a hero's action
# word changes (a captured motion shows as FC .. FF).
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/r9h.log; progress chain111.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain111.txt"; }
say "chain111 start"
ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/b15 TAG=r8r9h P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh r9h run-m 29050 28081 test-own-v89-snapB-god "$L/list-r9h.txt"
say "chain111 through"
