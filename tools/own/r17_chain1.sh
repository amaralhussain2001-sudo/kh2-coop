#!/bin/bash
# TEST ONLY (build 34 checks the user asked for, part 151): (1) THE LEAK TEST with a switchable ability: kit test-own-b34-lk =
# merged-v26-own + snapB + make_once 4300: Guard 0x8052 (equipped) in Sora's ability place 1 (0x0032E074). nm10, Abilities page,
# Circle on the first ability. lkA4 player 1 in his partner view (L2 START), lkB4 player 2 in his, lkN4 CONTROL player 1 START
# alone (his own menu: the switch must happen, 52 80 -> 52 00). (2) THE FIRST TOWN: New Game on the shipped disc (kh2-coop-v5),
# merged-v26-own, pictures + gauge probe: the partner's Drive strip must stay hidden where the game hides it.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="6150,6850,7000,7100,7400,7550"
export RANGES="0032E020:A0,0032E35C:A0,000E7E20:C,000DD800:4,0032F228:8,0032F0B0:40" CHAINS=""
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/memdump_probe.py" SNAPS="$SN" FRAMES=7600 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r17 TAG=r17$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one lkA4 run-x5 31550 28068 test-own-b34-lk pv_leak_p1.txt pv_idle_p2.txt "$B/list-st-nm10.txt" &
one lkB4 run-x6 31750 28069 test-own-b34-lk pv_idle2_p1.txt pv_leak_p2.txt "$B/list-st-nm10.txt" &
one lkN4 run-x7 31950 28070 test-own-b34-lk pv_leakown_p1.txt pv_idle_p2.txt "$B/list-st-nm10.txt" &
PROBE="$P/tools/own/gauge_probe.py" bash tools/own/dusk_one.sh r17-town "$P/patches/merged-v26-own" kh2-coop-v5.iso 7600 6340,6912,7300,7550 \
  "$O/mash_new_p1.txt" "$O/idle9000_p2.txt" run-x8 32150 28071 > local/sweep/r17/town.log 2>&1 &
wait
echo "r17 chain1 done" >> local/sweep/r17/chain1.txt
