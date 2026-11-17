#!/bin/bash
# TEST ONLY (ninth round, plan row 39, the rest): CANDIDATE v96 (= v95 with the hero record taken as a constant: edit_merge_v7_ownitems2.py); the same six runs as r9_chain1.sh, names ojA .. ojF, six lanes:
#  oiA (run-x1)  PLAYER 2 uses the first item of his list four times. He has Potion / Hi-Potion / Potion, player 1 three Potions.
#  oiB (run-x2)  PLAYER 1 uses four times (player 2 idle).
#  oiC (run-x3)  PLAYER 2 opens his pause menu (5000) and closes it (5600): do the places, the stock and the shortcuts change places and come back.
#  oiD (run-x4)  THE GAME GIVES at 5000: a Potion to the hero, an accessory, a Keyblade, a material, a Hi-Potion to the hero.
#  oiE (run-x5)  the refill: PLAYER 1 opens his pause menu.      oiF (run-x6)  the refill: PLAYER 2 opens his.
# Dumps: Sora's places + refill (0032E054), player 2's store (0032E370: places, refill, stock, shortcuts), the view T's
# places (000E7D34), the bag's first bytes (0032F0B0), the bag at the material (0032F198), the shortcuts (0032F228).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
mkdir -p "$B"; cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain2.txt"; }
say "chain2 start"
RG=0032E054:20,0032E370:20,000E7D34:20,0032F0B0:28,0032F198:4,0032F228:8,000E7E20:C
CH=0034E948+48C@0:8,000F05CC+48C@0:8
run() {  # run <worker> <sandbox> <port> <pine> <kit> <p1script> <p2script> <snaps> <frames>
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS=$8 FRAMES=$9 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$6" P2S="$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-hb13.txt"
  say "$1 done"
}
SN4="4900,5130,5350,5530,5750,5930,6150,6330,6550,6800"
run ojA run-x1 30750 28064 test-own-v96-oi1 "$S/newgame_only.txt" "$O/useitem4_p2.txt" $SN4 7000 &
run ojB run-x2 30950 28065 test-own-v96-oi1 "$O/useitem4_p1.txt" "$O/idle.txt" $SN4 7000 &
run ojC run-x3 31150 28066 test-own-v96-oi1 "$S/newgame_only.txt" "$O/ownmenu_p2.txt" "4900,5300,5500,5900,6300" 6500 &
run ojD run-x4 31350 28067 test-own-v96-oi2g "$S/newgame_only.txt" "$O/idle.txt" "4900,5100,5400" 5600 &
run ojE run-x5 31550 28068 test-own-v96-oi3 "$O/ownmenu_p1.txt" "$O/idle.txt" "4900,5300,5900,6300" 6500 &
run ojF run-x6 31750 28069 test-own-v96-oi3 "$S/newgame_only.txt" "$O/ownmenu_p2.txt" "4900,5300,5900,6300" 6500 &
wait
say "chain2 through"
