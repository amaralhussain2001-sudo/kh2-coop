#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF CANDIDATE v94 (= build 18 + the sixty-first glue
# --itemsync; patches/test-own-v94 / patches/test-v18-a, control patches/test-v18-a-nn) ON EIGHT SANDBOXES AT ONCE:
# tools/own/reg_par8.sh test-own-v94 test-v18-a b21 w21; and beside it, on run-x5 / run-x6, two own checks that
# are not in the regression: one23 = the toy cannon for 60,000 frames, orC = the stray capture on purpose at the
# Groundshaker (as orB). v93's logs of the same steps: local/reg-b20/.
# Progress: local/reg-par8.log (last line "ALL EIGHT THROUGH"), local/sweep/b15/count-b21.txt, chain137.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain137.txt"; }
say "chain137 start"
(
  SN2=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN2 FRAMES=60000 TOUT=2700 SWEEP_PROBE_WAIT=2700 LOGDIR=local/sweep/b15 TAG=r8one23 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one23 run-x5 31550 28068 test-own-v94-snapB "$L/list-nm63.txt"
  say "one23 done"
) &
(
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,6100,6400,7000,7900,8200,9000,11900" FRAMES=12000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/b15 TAG=r8orC P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh orC run-x6 31750 28069 test-own-v94-orph "$L/list-lk15.txt"
  say "orC done"
) &
bash tools/own/reg_par8.sh test-own-v94 test-v18-a b21 w21
wait
say "chain137 through"
