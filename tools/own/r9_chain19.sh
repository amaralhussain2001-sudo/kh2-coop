#!/bin/bash
# TEST ONLY (ninth round): THE TWO "RUN / SWEEP" FIGHTS THAT SHOWED 50 FAULT LINES ON v103 (pc 0x0010E8AC, a friend's follow routine
# with a wild slot number): mu08 74 (Shan-Yu with Mulan) and ca01 51 (Port Royal's first fight), the same scripts and kit (HP held,
# mashrc_long, 20,000 frames), on BUILD 19 (test-own-v94-snapB-god) and once more on v103: is the fault new, does it come again.
#   lane run-x1: f19a = mu08 74 on build 19, f19b = ca01 51 on build 19
#   lane run-x5: f103a = mu08 74 on v103,    f103b = ca01 51 on v103
# Logs local/sweep/r9/f19a.log ..; timelines local/tests/r9f19a-*-probe.txt; fault lines local/tests/r9f19a-*-emulog.txt; progress chain19.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain19.txt"; }
say "chain19 start"
run() {  # run <name> <sandbox> <port> <pine> <ownPatch> <list>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$6"
  say "$1 done"
}
(run f19a run-x1 30750 28064 test-own-v94-snapB-god "$B/list-mu74.txt"; run f19b run-x1 30750 28064 test-own-v94-snapB-god "$B/list-ca51.txt") &
(run f103a run-x5 31550 28068 test-own-v103-snapB-god "$B/list-mu74.txt"; run f103b run-x5 31550 28068 test-own-v103-snapB-god "$B/list-ca51.txt") &
wait
say "chain19 through"
