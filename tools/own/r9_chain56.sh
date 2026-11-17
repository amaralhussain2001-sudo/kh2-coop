#!/bin/bash
# TEST ONLY (ninth round, the user's items 1, 2 and 3 of 2026-11-15 evening), candidate v125 (fourth part: the dome ends once). Eight lanes at once:
# usage: r9_chain56.sh [ownTag]   (default test-own-v125)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v125}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain56.txt"; }
say "chain56 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
SYN="5240,5400,5600,6000,6400,7000,7500,8000,9000,10000,11000,11900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <probe> <frames> <snaps> <list> <p1> <p2>
  ISO=${ISO:-test-s1-tt137.iso} PROBE="$T/$6" FROM=4700 TO=$(( $7 - 100 )) SNAPS="$8" FRAMES=$7 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/${10}" P2S="$O/${11}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$9"
  say "$1 done"
}
D="$X-snapB-god-cap-xe0028"; R="$X-snapB-god-cap-xe0096"; LSN="6400,8000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,19900"
ISO=test-v5-tt137.iso one xsR run-m 29050 28081 $D cap_log_probe2.py 16000 "$SN" "$B/list-eh20.txt" idle.txt mashrc_long_p2.txt &
ISO=test-v5-tt137.iso one xsS run-v3 30150 28061 $D cap_log_probe2.py 16000 "$SN" "$B/list-eh20.txt" mashrc_long_p1.txt mashrc_long_p2_off5.txt &
ISO=test-v5-tt137.iso one xsT run-v3b 30350 28062 $D cap_log_probe2.py 16000 "$SN" "$B/list-eh20.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
ISO=test-v5-tt137.iso one xsU run-v3c 30550 28063 $D cap_log_probe2.py 16000 "$SN" "$B/list-eh20.txt" mashrc_long_p1.txt idle.txt &
ISO=test-v5-tt137.iso one xsV run-x1 30750 28064 $R cap_log_probe2.py 20000 "$LSN" "$B/list-eh20.txt" mashrc_long_p1.txt idle.txt &
ISO=test-v5-tt137.iso one xsW run-x2 30950 28065 $R cap_log_probe2.py 20000 "$LSN" "$B/list-eh20.txt" idle.txt idle.txt &
one syE2 run-x3 31150 28066 $X-snapB-god-strong sy_count_probe.py 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt idle.txt &
one syG2 run-x4 31350 28067 $X-snapB-god-strong sy_count_probe.py 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt mashrc_long_p2_off5.txt &
wait
say "chain56 through"
