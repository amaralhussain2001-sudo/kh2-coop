#!/bin/bash
# TEST ONLY (eighth round, plan row 39, a look before the next stage): WHAT HAPPENS TO THE ITEM PLACES WHEN A PLAYER
# USES AN ITEM FROM HIS COMMAND MENU. Build 18's own-screen patch + three Potions in Sora's item places 1 to 3
# (kit patches/test-own-b18-it2: the same + the save word + 0x36E8 = 1, which unlocks the "Items" row; read at 0x001BDD20), Merlin's House, two lanes:
#  it3 (run-x1)  PLAYER 2 uses the first item, twice.      it4 (run-x2)  PLAYER 1 does.   (it1 / it2 of chain 133: the row was "?")
# Dumps: Sora's item places (0032E054), the twin's view's (000E7D34), the bag's first bytes (0032F0B0), both
# heroes' HP words. Logs local/sweep/b15/it3.log, it4.log; progress chain134.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain134.txt"; }
say "chain134 start"
RG=0032E054:10,000E7D34:10,0032F0B0:8
CH=0034E948+48C@0:8,000F05CC+48C@0:8
SN="4900,5060,5140,5220,5300,5400,5500,5660,5740,5820,5900,6000,6300"
(
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8it3 P1S="$S/newgame_only.txt" P2S="$O/useitem_p2.txt" bash tools/own/sweep4.sh it3 run-x1 30750 28064 test-own-b18-it2 "$L/list-hb13.txt"
  say "it3 done"
) &
(
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8it4 P1S="$O/useitem_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh it4 run-x2 30950 28065 test-own-b18-it2 "$L/list-hb13.txt"
  say "it4 done"
) &
wait
say "chain134 through"
