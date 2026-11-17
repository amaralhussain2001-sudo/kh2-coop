#!/bin/bash
# TEST ONLY (ninth round), two lanes:
#   run-m:  fzB = the standing picture of v104 at the armoured Xemnas (eh21 99, from frame 16646), the same run with
#           tools/own/hold_state_probe.py at 16000, 16600, 16700, 16800, 17000, 18000, 19900: the whole state of the hold
#   run-x4: cnC = THE TOY CANNON, A VIEW FOR EACH PLAYER, third form (the game's still view, moved to player 2's cannon):
#           nm10 63 on patches/test-own-v103e-snapB, 16,000 frames
# Logs local/sweep/r9/fzB.log, cnC.log; progress chain23.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain23.txt"; }
say "chain23 start"
(
  ISO=test-v5-tt137.iso PROBE="$T/hold_state_probe.py" SNAPS="16000,16600,16700,16800,17000,18000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9fzB P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh fzB run-m 29050 28081 test-own-v104-snapB-god-cap "$B/list-eh21.txt"
  say "fzB done"
) &
(
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5200,6000,6500,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900" FRAMES=16000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r9 TAG=r9cnC P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh cnC run-x4 31350 28067 test-own-v103e-snapB "$L/list-nm63.txt"
  say "cnC done"
) &
wait
say "chain23 through"
