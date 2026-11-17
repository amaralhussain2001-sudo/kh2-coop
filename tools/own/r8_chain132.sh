#!/bin/bash
# TEST ONLY (eighth round, part 83): A STRAY CAPTURE ON PURPOSE, AND THE SIXTIETH GLUE'S RELEASE. The Groundshaker's
# room (lk15 59), HP held, both players Circle / Triangle / R1; at frame 6200 the kit make_orphan.py makes the
# boss (object 0x0459) capture player 1's hero with move FE, with no script behind it.
#  orA  on v89 (no rule): the hero must stay in action FE (the fault, made on purpose).        sandbox run-x5
#  orB  on v93 (glue 60, 1,800 steps): he must be let go near frame 8000 and play on.          sandbox run-x6
# 12,000 frames each. Logs local/sweep/b15/orA.log, orB.log; progress chain132.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain132.txt"; }
say "chain132 start"
lane() {  # lane <worker> <sandbox> <port> <pine> <kit>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,6100,6400,7000,7900,8200,9000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-lk15.txt"
  say "$1 done"
}
lane orA run-x5 31550 28068 test-own-v89-orph &
lane orB run-x6 31750 28069 test-own-v93-orph &
wait
say "chain132 through"
