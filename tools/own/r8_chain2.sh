#!/bin/bash
# TEST ONLY (eighth round): ONE RUN AT A TIME on sandbox run-m. Start it with KH2_TEST_SHOW=1 to see the windows.
#   z0     is memory 0x00080000-0x000EFFFF unused? (the build in the 1000 Heartless, zero_probe.py)
#   keychg player 1 changes the Keyblade in the pause menu with both heroes in the room (register G1)
#   gp4    player 2 ALONE against Shan-Yu with strong heroes (Strength / Defense 150): the finisher (G3)
#   dr     Data Roxas with strong heroes, HP held, the heap recorder (G2)
#   rv1..3 the revenge count on Shan-Yu: only player 1 hits, only player 2 hits, both hit (plan row 40)
#   bb15   the Mickey mission that gave no Mickey, clean jump, both heroes fall at 6500 (G4)
# Logs: local/sweep/b15/. Progress: local/sweep/b15/chain2.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
mkdir -p "$B"
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain2.txt"; }
MK="5200,6400,6700,7000,7400,8000,8900,10000,11900"
LONG="5200,7000,9000,11000,13000,15000,17000,19000,21000,23900"
T="$P/tools/own"
say "chain2 start"
echo "hb17 04 66 HB17_MS405 NO_FRIEND 66 66 66 0" > "$L/list-z0.txt"
PROBE="$T/zero_probe.py" RANGES=00080000:70000,000F0000:8000 SNAPS="1000,3000,5200,7000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8z \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh z0 run-m 29050 28081 test-own-v33-snapB-god "$L/list-z0.txt"
say "z0 done"
bash tools/own/dusk_one.sh t15-keychg "$P/patches/test-own-v33-menu" test-m-roam.iso 7500 "5060,5160,5260,5360,5440,5540,5660,5760,5860,5960,6200,6600,7000,7400" "$O/keychg_p1.txt" "$O/keychg_p2.txt" run-m 29050 28081 > "$B/keychg.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/keychg.log"
say "keychg done"
echo "mu09 08 75 MU09_MS108 W_FRIEND 75 75 75 0" > "$L/list-sy.txt"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp4 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" \
  bash tools/own/sweep4.sh gp4 run-m 29050 28081 test-own-v33-snapB-god-strong "$L/list-sy.txt"
say "gp4 done"
echo "eh21 12 99 EH21_MS101 NO_FRIEND 99 99 99 0" > "$L/list-dr.txt"
PROBE="$T/heap_probe.py" SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8dr \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh dr run-m 29050 28081 test-own-v33-snapB-god-heap-strong "$L/list-dr.txt"
say "dr done"
RV="5200,5600,6000,6400,6800,7200,7600,8000,8900,10000,11900"
PROBE="$T/sweepm_probe.py" RANGES=000F1FC0:20 SNAPS=$RV FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8rv1 \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh rv1 run-m 29050 28081 test-own-v33-snapB-god-rev "$L/list-sy.txt"
say "rv1 done"
PROBE="$T/sweepm_probe.py" RANGES=000F1FC0:20 SNAPS=$RV FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8rv2 \
  P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh rv2 run-m 29050 28081 test-own-v33-snapB-god-rev "$L/list-sy.txt"
say "rv2 done"
PROBE="$T/sweepm_probe.py" RANGES=000F1FC0:20 SNAPS=$RV FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8rv3 \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh rv3 run-m 29050 28081 test-own-v33-snapB-god-rev "$L/list-sy.txt"
say "rv3 done"
echo "bb15 05 82 BB15_MS203 W_FRIEND 82 82 82 0" > "$L/list-bb15.txt"
PROBE="$T/sweepm_probe.py" RANGES=0032F8E0:4,01C60528:8 CHAINS=01D49320+8:8,00352130:100 SNAPS=$MK FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8mk \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh bb15 run-m 29050 28081 test-own-v33-snapB-kill65 "$L/list-bb15.txt"
say "bb15 done"
say "chain2 through"
