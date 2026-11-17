#!/bin/bash
# TEST ONLY (ninth round, job 7): SHAN-YU'S CLASH (mu09 75; build 16's own pair) ON THE LAST CANDIDATE (v115: the glues 65 to 68 must leave it
# as it was). Kit -snapB-god-strong (HP held, Strength / Defense 150), probe act_poll_probe.py. One lane, one run after the other.
#   syA = both players press Circle and Triangle, 12,000 frames (as run tg36)
#   syB = player 1 fast mash, player 2 idle, 24,000 frames: is the fight won (as run tg39)
# usage: r9_chain49.sh <sandbox> <port> <pine>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain49.txt"; }
K=test-own-v115-snapB-god-strong
say "chain49 start ($1)"
SN="5240,5300,5400,5500,5600,5800,6000,6200,6400,6600,6800,7000,7200,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/r9 TAG=r9syA P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh syA $1 $2 $3 $K "$L/list-sy.txt"
say "syA done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=23900 SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9syB P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh syB $1 $2 $3 $K "$L/list-sy.txt"
say "syB done"
say "chain49 through"
