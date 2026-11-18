#!/bin/bash
# TEST ONLY (part 151): the leak test again with the right buttons (Circle on Guard opens "Don't Equip / Equip": UP, Circle).
# merged-v26-own + snapB + make_once 4300: Guard 0x8052 (equipped) in Sora's ability place 1 (0x0032E074). nm10, Abilities page,
# Circle on the first ability. lkA4 player 1 in his partner view (L2 START), lkB4 player 2 in his, lkN4 CONTROL player 1 START
# alone (his own menu: the switch must happen, 52 80 -> 52 00). (2) THE FIRST TOWN: New Game on the shipped disc (kh2-coop-v5),
# merged-v26-own, pictures + gauge probe: the partner's Drive strip must stay hidden where the game hides it.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="6850,7050,7150,7300,7700,7950"
export RANGES="0032E020:A0,0032E35C:A0,000E7E20:C,000DD800:4,0032F228:8,0032F0B0:40" CHAINS=""
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/memdump_probe.py" SNAPS="$SN" FRAMES=8000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r17 TAG=r17$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one lkA5 run-x5 31550 28068 test-own-b34-lk pv_leak5_p1.txt idle8000_p2.txt "$B/list-st-nm10.txt" &
one lkB5 run-x6 31750 28069 test-own-b34-lk idle8000_p1.txt pv_leak5_p2.txt "$B/list-st-nm10.txt" &
one lkN5 run-x7 31950 28070 test-own-b34-lk pv_leak5own_p1.txt idle8000_p2.txt "$B/list-st-nm10.txt" &
wait
echo "r17 chain2 done" >> local/sweep/r17/chain1.txt
