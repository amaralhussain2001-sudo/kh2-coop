#!/bin/bash
# TEST ONLY (eighth round, plan row 39): CANDIDATE v94 (= build 18 + the sixty-first glue --itemsync): four item uses,
# three Potions being there, two lanes:
#  it6 (run-x1)  PLAYER 2 uses four times: his list must go x3, x2, x1, then nothing to take.
#  it7 (run-x2)  PLAYER 1 uses four times (player 2 idle): as the game.
# Dumps and pictures as in r8_chain135.sh. Logs local/sweep/b15/it6.log, it7.log; progress chain136.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain136.txt"; }
say "chain136 start"
RG=0032E054:10,000E7D34:10,0032F0B0:8
CH=0034E948+48C@0:8,000F05CC+48C@0:8
SN="4900,5130,5350,5530,5750,5930,6150,6330,6550,6800"
(
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS=$SN FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8it6 P1S="$S/newgame_only.txt" P2S="$O/useitem4_p2.txt" bash tools/own/sweep4.sh it6 run-x1 30750 28064 test-own-v94-it2 "$L/list-hb13.txt"
  say "it6 done"
) &
(
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS=$SN FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8it7 P1S="$O/useitem4_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh it7 run-x2 30950 28065 test-own-v94-it2 "$L/list-hb13.txt"
  say "it7 done"
) &
wait
say "chain136 through"
