#!/bin/bash
# TEST ONLY (eighth round, plan row 39 stage 1b; A LANE BESIDE THE OTHERS, sandbox run-x1, port 30750, PINE 28064):
# candidate v91, DO PLAYER 2'S ABILITY SWITCHES (five shorts in King Mickey's record, 0x0032E390, mark 0x5032 at
# 0x0032E39A) SURVIVE (1) two King Mickeys in a fight, (2) a Game Over and "Continue".
#  mkS9  Storm Rider (mu08 79), both heroes killed at 6500, King Mickey's roll always wins (kit -mk): two Mickeys
#        fight, the heroes come back. The switches were set to 0002 at frame 4300.
#  ab9   the roam disc, kit -die2-ab, the regression's save / Game Over / Continue scripts (save_cont).
# Dumps: the hero's first places, the view T, the switches + mark, King Mickey's record.
# Logs local/sweep/b15/mkS9.log, ab9.log; progress chain119.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x1; PT=30750; PN=28064
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain119.txt"; }
say "chain119 start"
RG=0034E948:8,000F05CC:4,0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
M3="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$M3 FRAMES=14000 TOUT=700 SWEEP_PROBE_WAIT=700 LOGDIR=local/sweep/b15 TAG=r8mkS9 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS9 $RD $PT $PN test-own-v91-mk "$L/list-sr1.txt"
say "mkS9 done"
PROBE="$T/sweepm_probe.py" RANGES=$RG bash tools/own/dusk_one.sh ab9 "$P/patches/test-own-v91-die2-ab" test-m-roam.iso 16000 "6600,7000,8000,9000,9100,9700,10300,11000,12000,13000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" $RD $PT $PN > "$B/ab9.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/$RD/p1/logs/emulog.txt)" >> "$B/ab9.log"; cat "$P/local/tests/ab9-probe.txt" >> "$B/ab9.log" 2>/dev/null
say "ab9 done"
say "chain119 through"
