#!/bin/bash
# TEST ONLY (ninth round, the user's item 1 of 2026-11-15 evening): the last Xemnas's laser dome (HP 40 kit) on v122 with the
# recorder tools/own/make_rec_rc.py in front of the forty-seventh glue's rc_one (from game counter 7100) and the probe
# tools/own/rc_probe.py: does player 2's "Reflect" reach rc_one, and with which source object?
#   xsE run-m   ONLY PLAYER 2 presses (idle / mashrc_long_p2)
#   xsF run-v3  ONLY PLAYER 1 presses (mashrc_long_p1 / idle)   (the control)
# usage: [PRB=probe.py] [N1=name N2=name] r9_chain52.sh [kit]   (kit default test-own-v122-snapB-god-xe0028-rc)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
KIT=${1:-test-own-v122-snapB-god-xe0028-rc}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain52.txt"; }
say "chain52 start ($KIT)"
SN="6400,7000,7500,8000,8500,9000,9500,10000,11000,12000,13000,14000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/${PRB:-rc_probe.py}" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$KIT" "$B/list-eh20.txt"
  say "$1 done"
}
one ${N1:-xsE} run-m 29050 28081 idle.txt mashrc_long_p2.txt &
one ${N2:-xsF} run-v3 30150 28061 mashrc_long_p1.txt idle.txt &
wait
say "chain52 through"
