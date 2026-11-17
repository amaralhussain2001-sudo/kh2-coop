#!/bin/bash
# TEST ONLY (ninth round), three lanes:
#   run-x1: c74 = mu08 74, run-x5: c51 = ca01 51: THE ONE-HERO NO-PATCH CONTROLS of the two fights with 50 fault lines at pc 0x0010E8AC
#           (patches/test-empty-god = no patch + HP held; the plain disc; player 1 mashes as in the two-hero runs, player 2 idle)
#   run-x4: cnB = THE TOY CANNON, A VIEW FOR EACH PLAYER, second form (player 2's cannon gets player 1's camera offsets):
#           nm10 63 on patches/test-own-v103d-snapB, 16,000 frames
# Logs local/sweep/r9/c74.log, c51.log, cnB.log; progress chain21.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain21.txt"; }
say "chain21 start"
ctl() {  # ctl <name> <sandbox> <port> <pine> <list>
  ISO=test-s1-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$S/idle_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-empty-god "$5"
  say "$1 done"
}
ctl c74 run-x1 30750 28064 "$B/list-mu74.txt" &
ctl c51 run-x5 31550 28068 "$B/list-ca51.txt" &
(
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5200,6000,6500,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900" FRAMES=16000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r9 TAG=r9cnB P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh cnB run-x4 31350 28067 test-own-v103d-snapB "$L/list-nm63.txt"
  say "cnB done"
) &
wait
say "chain21 through"
