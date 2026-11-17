#!/bin/bash
# TEST ONLY (ninth round, item 4: the "Riku frees Sora" part with ONE hero held, candidate v126): does the part END when Riku
# stands at Xemnas? Riku (object 0x01AE9A20) is set ONCE next to where the part ended in the old pair run xeB ((1495, -85,
# 107) at 12880) by tools/own/make_teleport.py; player 1 (the held hero, he plays Riku) mashrc_long, player 2 idle. Lanes x3 / x4.
#   rkA run-x3  Riku set at frame 11000 to (1495, -85, 107)       rkB run-x4  at frame 12000 to (1495, y kept, 107)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=test-own-v126
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain59.txt"; }
say "chain59 start ($X)"
LSN="6400,8000,10000,11000,11100,11400,12000,12100,12400,13000,14000,15000,16000,17000,18000,19000,19900"
one() {  # one <name> <sandbox> <port> <pine> <kit>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="$LSN" FRAMES=20000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh20.txt"
  say "$1 done"
}
one rkA run-x3 31150 28066 $X-snapB-god-cap-xe0096-rk11 &
one rkB run-x4 31350 28067 $X-snapB-god-cap-xe0096-rk12 &
wait
say "chain59 through"
