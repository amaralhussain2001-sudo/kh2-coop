#!/bin/bash
# TEST ONLY (ninth round, after build 21): the three fights where v129 still makes a pair (the 40 fights, tag rs5: eh26 69, eh28 68,
# mu08 79), again with tools/own/cap_log_probe3.py, which names each captor's object number and kind (BOSS 3, ZAKO 4, RTN 15 ...):
# are these captors enemies (then the user's single-target rule applies) or other objects (build 20's pair, on purpose)?
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain70.txt"; }
say "chain70 start"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9ob$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh ob$1 $2 $3 $4 test-own-v129-snapB-god-cap "$B/list-ob$1.txt"
  say "ob$1 done"
}
lane 1 run-x7 31950 28070 &
lane 2 run-x8 32150 28071 &
lane 3 run-x9 32350 28072 &
wait
say "chain70 through"
