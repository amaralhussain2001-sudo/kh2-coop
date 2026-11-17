#!/bin/bash
# TEST ONLY (eighth round, plan row 39): PLAYER 2 USES FOUR ITEMS, three Potions being there (build 18's patch + the
# kit of chain 134). After each use: Sora's item places, the twin's view's, and a picture of his "Items" list
# (the snapshots at +120 after each "Items" press). THE QUESTION: does his list still show an item that is gone.
# One run (run-x1). Log local/sweep/b15/it5.log; progress chain135.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain135.txt"; }
say "chain135 start"
RG=0032E054:10,000E7D34:10,0032F0B0:8
CH=0034E948+48C@0:8,000F05CC+48C@0:8
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5130,5350,5530,5750,5930,6150,6330,6550,6800" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8it5 P1S="$S/newgame_only.txt" P2S="$O/useitem4_p2.txt" bash tools/own/sweep4.sh it5 run-x1 30750 28064 test-own-b18-it2 "$L/list-hb13.txt"
say "it5 done"
say "chain135 through"
