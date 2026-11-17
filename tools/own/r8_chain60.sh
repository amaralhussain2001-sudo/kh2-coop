#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): candidate v60 = build 14 + --ownrec --ownmenu.
# A one-time write at frame 4300 puts item 0x0035 into the hero's accessory place 1 (Sora's record + 0x24) and item
# 0x0028 into PLAYER 2's accessory place (+ 0x2C). Merlin's House by jump kit (hb13, a quiet room).
#   om1  PLAYER 2 opens the pause menu (START 5000) and closes it (Cross 5600)
#   om2  PLAYER 1 does the same
# Read at 4900 / 5200 / 5400 / 5800 / 6300: Sora's record (0x0032E020, 0x40 bytes), the view T (0x000E7D00), the
# source word and the "player 2's menu is open" flag (0x000E7E20 / 24), the module list (0x00369D98), both slots'
# stat words. ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/om1.log, om2.log; progress chain60.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain60.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain60 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E020:40,000E7D00:40,000E7E20:8,00369D98:10
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om1 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh om1 run-m 29050 28081 test-own-v60-menu-acc "$L/list-hb13.txt"
tlb om1; say "om1 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om2 P1S="$O/ownmenu_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh om2 run-m 29050 28081 test-own-v60-menu-acc "$L/list-hb13.txt"
tlb om2; say "om2 done"
say "chain60 through"
