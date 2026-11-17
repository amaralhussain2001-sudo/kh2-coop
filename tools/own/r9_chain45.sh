#!/bin/bash
# TEST ONLY (ninth round, job 3): WHO STEERS RIKU while the last Xemnas holds both heroes (eh20 74, both Xemnas objects' HP written to 150
# at frame 6500; candidate v112, HP held). Both players mash up to frame 10050 (as in run xeB); after that:
#   xeG = PLAYER 1 holds the stick (forward 10100-11600, right 11600-13100), player 2 does nothing
#   xeH = PLAYER 2 holds the stick, player 1 does nothing
#   xeI = nobody presses (what Riku does by himself)
# Probe riku_probe.py every 100 frames from 9800 to 13500. 13,600 frames.
# usage: r9_chain45.sh <name> <sandbox> <port> <pine>      (one run; start several at once in different sandboxes)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain45.txt"; }
SN=$(python -c "print(','.join(str(f) for f in range(9800, 13501, 100)))")
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  say "$1 start ($2)"
  ISO=test-v5-tt137.iso PROBE="$T/${PRB:-riku_probe.py}" SNAPS="$SN" FRAMES=13600 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 ${KIT:-test-own-v112-snapB-god-xe0096} "$B/list-eh20.txt"
  say "$1 done"
}
case "$1" in
  xeG) one xeG $2 $3 $4 riku_steer_p1.txt riku_wait_p2.txt ;;
  xeH) one xeH $2 $3 $4 riku_wait_p1.txt riku_steer_p2.txt ;;
  xeI) one xeI $2 $3 $4 riku_wait_p1.txt riku_wait_p2.txt ;;
  xeJ) KIT=test-own-v114-snapB-god-xe0096; one xeJ $2 $3 $4 riku_steer_p1.txt riku_wait_p2.txt ;;   # v114 (glue 68): player 1 steers
  xeK) KIT=test-own-v114-snapB-god-xe0096; one xeK $2 $3 $4 riku_wait_p1.txt riku_steer_p2.txt ;;   # v114: player 2 steers
  xeL) KIT=test-own-v114-snapB-god-xe0096; PRB=pads_probe.py; one xeL $2 $3 $4 riku_steer_p1.txt riku_wait_p2.txt ;;   # v114, player 1 steers, the pad records read
  xeM) KIT=test-own-v114-snapB-god-xe0096; PRB=pads_probe2.py; SN="9100,9150,10500,11000,12000"; one xeM $2 $3 $4 riku_steer2_p1.txt riku_wait_p2.txt ;;   # where the stick lives
  xeN) KIT=test-own-v115-snapB-god-xe0096; one xeN $2 $3 $4 riku_steer_p1.txt riku_wait_p2.txt ;;   # v115 (glue 68, second form): player 1 steers
  xeO) KIT=test-own-v115-snapB-god-xe0096; one xeO $2 $3 $4 riku_wait_p1.txt riku_steer_p2.txt ;;   # v115: player 2 steers
  xeP) KIT=test-own-v115-snapB-god-xe0096; one xeP $2 $3 $4 mashrc_long_p1.txt mashrc_long_p2.txt ;;   # v115: both mash (as run xeB)
  *) echo "which run?"; exit 1 ;;
esac
