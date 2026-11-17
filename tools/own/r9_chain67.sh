#!/bin/bash
# TEST ONLY (ninth round, the pickup test, second step): MP 10 / Drive 0 for both heroes already at frame 4900 (tools/own/make_lowkit.py),
# so that player 2's own MP balls show; and the Drive Forms kit (-forms), so that the game may drop Drive balls. Candidate v129,
# probe tools/own/prize_probe.py, 16,000 frames; player 1 runs far away and stands, player 2 fights:
#   pmA run-x1  Agrabah's city (al00 program 2), kit -snapB-god-strong-pkl49 (as plD, MP / Drive low from 4900)
#   pmB run-x2  the 1000 Heartless (hb17 66), kit -forms-god-strong-pkl (Drive Forms on)
#   pmC run-x3  Agrabah's city, kit -forms-god-strong-pkl
#   pmD run-x4  the 1000 Heartless, kit -forms-god-strong-pkl, both fight
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain67.txt"; }
say "chain67 start"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <list> <p1> <p2>
  ISO=test-s1-tt137.iso PROBE="$T/prize_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$7" P2S="$O/$8" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$6"
  say "$1 done"
}
one pmA run-x1 30750 28064 test-own-v129-snapB-god-strong-pkl49 "$B/list-al00lb.txt" walkfar_p1.txt mashrc_long_p2.txt &
one pmB run-x2 30950 28065 test-own-v129-forms-god-strong-pkl "$L/list-hb17.txt" walkfar_p1.txt mashrc_long_p2.txt &
one pmC run-x3 31150 28066 test-own-v129-forms-god-strong-pkl "$B/list-al00lb.txt" walkfar_p1.txt mashrc_long_p2.txt &
one pmD run-x4 31350 28067 test-own-v129-forms-god-strong-pkl "$L/list-hb17.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
wait
say "chain67 through"
