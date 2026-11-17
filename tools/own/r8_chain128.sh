#!/bin/bash
# TEST ONLY (eighth round, plan row 9, the other fights): THE TEN BOSS ROOMS ON CANDIDATE v93 (= v91 + the sixtieth
# glue --holdwatch: a hero in one and the same captured motion for 1,800 steps is let go; WITHOUT the fifty-ninth
# glue), on four sandboxes at once (run-x1 .. run-x4). Everything else as in r8_chain113.sh (HP held at 150, the
# v5 test disc, 20,000 frames, both players Circle / Triangle / R1, probe act_poll_probe.py); run names r8r9m-*.
# THE QUESTIONS: is the hero at the Groundshaker let go (about 1,800 frames after 8650), and are the other nine
# rooms as on v89 (the Hydra too).
# Logs local/sweep/b15/r9m1.log .. r9m4.log; progress chain128.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain128.txt"; }
say "chain128 start"
lane() {  # lane <worker> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8r9m P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-own-v93-snapB-god "$L/list-$1.txt"
  say "lane $1 through"
}
lane r9m1 run-x1 30750 28064 &
lane r9m2 run-x2 30950 28065 &
lane r9m3 run-x3 31150 28066 &
lane r9m4 run-x4 31350 28067 &
wait
say "chain128 through"
