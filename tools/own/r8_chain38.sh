#!/bin/bash
# TEST ONLY (eighth round, job 10): Xigbar, the story fight (eh10 57). In run xig (candidate v52) player 1's hero showed the
# action 0xFC and player 2's 0xFF at every picture from 7000 to 22000: both HELD for the whole fight?
#   xigc  THE CONTROL: build 12 (test-own-v33-snapB-god-strong), the action timeline of both heroes, 12,000 frames
#   xig2  candidate v52, the same
#   xigdc Data Xigbar (eh10 100) with build 12 (run xigd: player 1 in action 0xB5 at every picture)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/xigc.log, xig2.log, xigdc.log; progress chain38.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain38.txt"; }
say "chain38 start"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
for kv in "xigc test-own-v33-snapB-god-strong list-xig.txt" "xig2 test-own-v52-snapB-god-strong list-xig.txt" "xigdc test-own-v33-snapB-god-strong list-xigd.txt"; do set -- $kv
  PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 run-m 29050 28081 $2 "$L/$3"
  say "$1 done"
done
say "chain38 through"
