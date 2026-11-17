#!/bin/bash
# TEST ONLY (eighth round, register G1 -> A FAULT): player 1 changes the Keyblade in the pause menu and the game
# stops when the menu closes (test t15-keychg: one frozen picture from 5860 on, 27 fault lines).
# Merlin's House by jump kit, kit test-own-v33-menu (save + 0x239E = FF, Oathkeeper and Oblivion in the bag).
#   kc2  two heroes (the jump disc)            -> the fault lines are kept in local/tests/r8kc2-...-emulog.txt
#   kc1  ONE hero (the jump disc without twin) -> the control: does the change work with one hero?
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/kc2.log, kc1.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain9.txt"; }
echo "hb13 04 0 HB13_ROAM DEFAULT 0 0 0 0" > "$L/list-hb13.txt"
SN="5060,5360,5540,5860,5960,6200,6600,7000,7400"
say "chain9 start"
SNAPS=$SN FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kc2 P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" \
  bash tools/own/sweep4.sh kc2 run-m 29050 28081 test-own-v33-menu "$L/list-hb13.txt"
cp "$P/local/run-m/p1/logs/emulog.txt" "$B/kc2-emulog-full.txt" 2>/dev/null
say "kc2 done"
ISO=test-s1-tt137solo.iso SNAPS=$SN FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kc1 P1S="$O/keychg_p1.txt" P2S="$O/idle.txt" \
  bash tools/own/sweep4.sh kc1 run-m 29050 28081 test-own-v33-menu "$L/list-hb13.txt"
cp "$P/local/run-m/p1/logs/emulog.txt" "$B/kc1-emulog-full.txt" 2>/dev/null
say "kc1 done"
say "chain9 through"
