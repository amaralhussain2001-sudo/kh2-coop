#!/bin/bash
# TEST ONLY (eighth round): ONE RUN AT A TIME on sandbox run-m. Start it with KH2_TEST_SHOW=1 to see the windows.
#   f3c   Shan-Yu's Mickey part with NO patch and MAP PROGRAM 0 (the start of the old run that had 50 fault lines)
#   menu  the main menu with the save's menu byte (save + 0x239E) = FF and Strength / Defense = 150 (register G1, G2)
#   h2    the object heap in six heavy fights, TWO heroes (build 12 + HP kit + heap recorder)
#   h1    the same six, ONE hero, no patch (HP kit + heap recorder)
# Logs: local/sweep/b15/. Progress: local/sweep/b15/chain1.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
mkdir -p "$B"
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain1.txt"; }
MK="5200,6400,6700,7000,7400,8000,8900,10000,11900"
LONG="5200,7000,9000,11000,13000,15000,17000,19000,21000,23900"
say "chain1 start"
echo "mu09 08 75 MU09_MS108 W_FRIEND 0 75 75 0" > "$L/list-f3c.txt"
SNAPS=$MK FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8c0 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" \
  bash tools/own/sweep4.sh f3c run-m 29050 28081 test-empty-kill65 "$L/list-f3c.txt"
say "f3c done"
bash tools/own/dusk_one.sh t15-menu "$P/patches/test-own-v33-menu" test-m-roam.iso 6000 "4900,5060,5160,5260,5330,5440,5620,5800,5950" "$O/keyexp_p1.txt" "$O/idle.txt" run-m 29050 28081 > "$B/menu.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/menu.log"
say "menu done"
cat > "$L/list-h.txt" <<'EOF'
hb17 04 66 HB17_MS405 NO_FRIEND 66 66 66 0
eh20 12 74 EH20_MS113 W_FRIEND_ONLY 74 74 74 0
mu09 08 75 MU09_MS108 W_FRIEND 75 75 75 0
he18 06 171 HE18_MS108 DEFAULT 171 171 171 0
eh19 12 59 EH19_MS105 NO_FRIEND 59 59 59 0
mu08 08 79 MU08_MS204 W_FRIEND 79 79 79 0
EOF
PROBE="$P/tools/own/heap_probe.py" SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8h2 \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh h2 run-m 29050 28081 test-own-v33-snapB-god-heap "$L/list-h.txt"
say "h2 done"
PROBE="$P/tools/own/heap_probe.py" SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8h1 \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh h1 run-m 29050 28081 test-empty-god-heap "$L/list-h.txt"
say "h1 done"
say "chain1 through"
