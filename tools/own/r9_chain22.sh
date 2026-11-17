#!/bin/bash
# TEST ONLY (ninth round), four lanes:
#   run-m:   fzA = THE FREEZE OF v104 AT THE ARMOURED XEMNAS (eh21 99, frame 16646, run h4 of r9_chain17.sh), the same run once more
#            with tools/own/freeze_probe.py: where is the game when its counter stands still
#   run-v3:  frA = mu08 74 on v103 (two heroes),  run-v3b: frB = mu08 74, the one-hero no-patch control,
#   run-x4:  frC = ca01 51, the one-hero no-patch control: tools/own/friend_probe.py: each friend's slot number (object + 0xB70)
# Logs local/sweep/r9/fzA.log, frA.log, frB.log, frC.log; progress chain22.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain22.txt"; }
say "chain22 start"
(
  ISO=test-v5-tt137.iso PROBE="$T/freeze_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9fzA P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh fzA run-m 29050 28081 test-own-v104-snapB-god-cap "$B/list-eh21.txt"
  say "fzA done"
) &
fr() {  # fr <name> <sandbox> <port> <pine> <iso> <own> <p2script> <list>
  ISO=$5 PROBE="$T/friend_probe.py" SNAPS="4900,5200,6000,7000,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$7" bash tools/own/sweep4.sh $1 $2 $3 $4 "$6" "$8"
  say "$1 done"
}
fr frA run-v3 30150 28061 test-v5-tt137.iso test-own-v103-snapB-god "$O/mashrc_long_p2.txt" "$B/list-mu74.txt" &
fr frB run-v3b 30350 28062 test-s1-tt137.iso test-empty-god "$S/idle_p2.txt" "$B/list-mu74.txt" &
fr frC run-x4 31350 28067 test-s1-tt137.iso test-empty-god "$S/idle_p2.txt" "$B/list-ca51.txt" &
wait
say "chain22 through"
