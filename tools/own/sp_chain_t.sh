#!/bin/bash
# TEST ONLY (2026-11-13, tests-only session): the crash tests of the new job list on the build 12 candidate
# (test-own-v33-snapB + test kits), after the whole regression (waits for "ALL FOUR THROUGH" in local/reg-b12.log).
# Logs in local/sweep/b13/ (NOT local/sweep/*.log: sweep_doc.py reads those as sweep results).
#   g0..g3  long fights with both heroes' HP held (kit -snapB-god): 24,000 frames, both players attack and press
#           Triangle (Reaction Commands): Data Roxas, the 1000 Heartless, the bosses that carry one hero
#   gp2     player 2 ALONE against Shan-Yu (player 1 only starts the game), HP held
#   k0..k3  the 11 Mickey-rescue missions: both heroes fall at frame 6500 (kit -snapB-kill65), 12,000 frames
#   then    the no-patch controls (list-ctl), the menu exploration (Keyblade change), player 2 in Valor Form
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
while ! grep -q "ALL FOUR THROUGH" local/reg-b12.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 15" > /dev/null; done
mkdir -p local/sweep/b13
L=local/sweep
LONG="5200,7000,9000,11000,13000,15000,17000,19000,21000,23900"
MK="5200,6400,6700,7000,7400,8000,8900,10000,11900"
lane() {  # sandbox port pine godList mickeyList
  SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b13 TAG=god P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
    bash tools/own/sweep3.sh "g$4" "$1" "$2" "$3" test-own-v33-snapB-god "$L/list-g$4.txt"
  SNAPS=$MK FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b13 TAG=mk P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
    bash tools/own/sweep3.sh "k$4" "$1" "$2" "$3" test-own-v33-snapB-kill65 "$L/list-k$4.txt"
}
lane run-m 29050 28081 0 &
lane run-v3 30150 28061 1 &
lane run-v3b 30350 28062 2 &
(
  lane run-v3c 30550 28063 3
  # player 2 alone against Shan-Yu, HP held
  echo "mu09 08 75 MU09_MS108 W_FRIEND 0 75 75 0" > "$L/list-gp2.txt"
  SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b13 TAG=gp2 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" \
    bash tools/own/sweep3.sh gp2 run-v3c 30550 28063 test-own-v33-snapB-god "$L/list-gp2.txt"
) &
wait
# the no-patch controls (one hero, controller 2 idle, scripts that never answer a Game Over menu)
LOGDIR=local/sweep/ctl TAG=swc P1S="$O/ctl_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh ctl run-m 29050 28081 test-empty "$L/list-ctl.txt" &
# the main menu, step by step (Keyblade change), on the roam disc with two more Keyblades in the bag
( bash tools/own/dusk_one.sh t13-keyexp "$P/patches/test-own-v33-keys" test-m-roam.iso 6000 "4900,5060,5160,5260,5330,5440,5620,5800,5950" "$O/keyexp_p1.txt" "$O/idle.txt" run-v3 30150 28061 > local/sweep/b13/keyexp.log 2>&1; echo "TLB misses $(grep -c 'TLB Miss' local/run-v3/p1/logs/emulog.txt)" >> local/sweep/b13/keyexp.log ) &
# player 2 in Valor Form in a fight (Borough with Heartless): the Valor and Wisdom records at each picture
( RANGES="0032EE24:38,0032EE5C:38" PROBE="$P/tools/own/memdump_probe.py" bash tools/own/dusk_one.sh t13-valor-p2 "$P/patches/test-own-v33-forms" test-s1-hb9h.iso 7000 "4690,4900,5300,5500,5700,5900,6300,6900" "$S/newgame_only.txt" "$O/drive2_p2.txt" run-v3b 30350 28062 > local/sweep/b13/valor.log 2>&1; echo "TLB misses $(grep -c 'TLB Miss' local/run-v3b/p1/logs/emulog.txt)" >> local/sweep/b13/valor.log ) &
wait
echo "tests t done $(date +%H:%M:%S)" >> local/sweep/b13/t-done.txt
