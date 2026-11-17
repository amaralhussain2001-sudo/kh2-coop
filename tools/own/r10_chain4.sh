#!/bin/bash
# TEST ONLY (tenth round, open item h): THE DATA FIGHT'S LASER DOME (EH20_MS113_RE = eh20 98, the last Xemnas's level-99
# copy B_EX170_LAST_LV99, object 0x09CA), the five cases of r9_chain63.sh on candidate v130 (kit -snapB-god-cap-xe0028:
# Xemnas's HP words set to 40 at 6500, as for the story fight). Five lanes run-x5 .. run-x9.
# usage: r10_chain4.sh [ownTag]   (default test-own-v130)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v130}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/r10chain4.txt"; }
say "r10chain4 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$X-snapB-god-cap-xe0028" "$B/list-eh20-98.txt"
  say "$1 done"
}
#   xd2 run-x5   ONLY player 2 presses        xd3 run-x6   both, player 2 five frames later (xsY's case)
#   xd4 run-x7 both, player 1 five frames later   xd5 run-x8  both in the same frames   xd6 run-x9  ONLY player 1
one xd2 run-x5 31550 28068 idle.txt mashrc_long_p2.txt &
one xd3 run-x6 31750 28069 mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one xd4 run-x7 31950 28070 mashrc_long_p1_off5.txt mashrc_long_p2.txt &
one xd5 run-x8 32150 28071 mashrc_long_p1.txt mashrc_long_p2.txt &
one xd6 run-x9 32350 28072 mashrc_long_p1.txt idle.txt &
wait
say "r10chain4 through"
