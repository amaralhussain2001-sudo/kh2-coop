#!/bin/bash
# TEST ONLY (eighth round): THE FINAL CANDIDATE v81 (build 15 + the glues 50, 51, 52: both heroes in Shan-Yu's
# clash, player 2's Gummi ship can be hit, a carpet under player 2's hero) BEFORE its whole regression: the three
# new things once more, now all in one patch.
#   tg40 .. tg44  Shan-Yu, the five runs of r8_chain80.sh
#   carp3         seven carpet missions on the v5 test disc (the fights al14 86 / 87, Jafar al05 62, the race al14
#                 100 / 101 / 102, and the carpet ESCAPE al14 61, where there is one hero: nothing may change)
#   gh10, gh11    Gummi route 0: nobody fires / both fire, the whole mission
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg40.log .., carp3.log, chain90.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"; S="$P/tests/scripts/lane-s3"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain90.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
K=test-own-v81-snapB-god-strong
say "chain90 start"
SN="5240,5280,5300,5310,5340,5400,5440,5480,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg40 P1S="$O/tri_only_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh tg40 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg40; say "tg40 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg41 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg41 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg41; say "tg41 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg42 P1S="$O/mash_new_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh tg42 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg42; say "tg42 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg43 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg43 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg43; say "tg43 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg44 P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh tg44 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg44; say "tg44 done"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,5250,5500,5750,6000,6250,6500,6750,7000,7500,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8carp3 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh carp3 run-m 29050 28081 test-own-v81-snapB "$L/list-carp7.txt"
say "carp3 done"
one() {  # name frames snaps p1script p2script
  local n=$1
  out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/test-own-v81-gum0" test-s1-tt137.iso "$2" "$3" "$4" "$5" run-m 29050 28081 2>&1 | head -n 1)
  echo "$n | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/run-m/p1/logs/emulog.txt")" >> "$B/chain90.txt"
  cp "$P/local/tests/$n-probe.txt" "$B/$n-probe.txt" 2>/dev/null
  say "$n done"
}
SG=$(python -c "print(','.join(str(f) for f in range(8000, 24000, 1000)) + ',23900')")
one r8gh10 24000 "$SG" "$S/gb_p1_idle.txt" "$S/gb_p2_idle.txt"
SG2=$(python -c "print(','.join(str(f) for f in range(8000, 40000, 2000)) + ',39900')")
one r8gh11 40000 "$SG2" "$S/gb_p1_fight.txt" "$S/gb_p2_fight.txt"
say "chain90 through"
