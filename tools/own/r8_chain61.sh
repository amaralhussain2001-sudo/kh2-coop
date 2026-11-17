#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): candidate v61 = v60 with the close of player 2's menu
# seen at the field's START look-out. The kit and the room as r8_chain60.sh (item 0x35 in the hero's accessory
# place 1, item 0x28 in player 2's, written once at frame 4300; Merlin's House).
#   om3  PLAYER 2 opens the pause menu (START 5000) and closes it (Cross 5600): the places must be back after it
#   om4  PLAYER 1 does the same: nothing may change places
#   om5  PLAYER 2 opens it and puts on the first accessory of the list (one Ability Ring in the bag, save + 0x3587)
# Read: Sora's record, the view T, the source / flag words, the bag bytes 0x3580..0x35BF, both slots' stat words.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/om3.log ..; progress chain61.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain61.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain61 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E020:40,000E7D00:40,000E7E20:8,0032F0B0:40
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om3 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh om3 run-m 29050 28081 test-own-v61-menu-acc "$L/list-hb13.txt"
tlb om3; say "om3 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om4 P1S="$O/ownmenu_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh om4 run-m 29050 28081 test-own-v61-menu-acc "$L/list-hb13.txt"
tlb om4; say "om4 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5060,5160,5260,5340,5420,5520,5640,5760,5860,6000,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om5 P1S="$S/newgame_only.txt" P2S="$O/ownequip_p2.txt" bash tools/own/sweep4.sh om5 run-m 29050 28081 test-own-v61-menu-acc-ring "$L/list-hb13.txt"
tlb om5; say "om5 done"
say "chain61 through"
