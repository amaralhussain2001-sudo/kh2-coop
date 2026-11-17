#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): candidate v62 = v61 + three safety points (only a
# hero's slot gets player 2's places; the hero's record is the one that changes places; the menu flag is cleared
# at a load and at a New Game).
#   om6   PLAYER 2 opens and closes the pause menu (as om3)
#   om7   PLAYER 2 puts on the Ability Ring from the bag (one entry down in the list)
#   om8   both heroes go through a door and back (the roam disc): each keeps the bonus of his own accessory
#   mkS8  Storm Rider, two King Mickeys (a body of the twin that is not a hero: the plain copy)
# ONE RUN AT A TIME, hidden. Logs local/sweep/b15/om6.log ..; progress chain62.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain62.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain62 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E020:40,000E7D00:40,000E7E20:C,0032F0B0:40
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om6 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh om6 run-m 29050 28081 test-own-v62-menu-acc "$L/list-hb13.txt"
tlb om6; say "om6 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="4900,5060,5160,5260,5340,5420,5500,5570,5660,5760,5860,6000,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8om7 P1S="$S/newgame_only.txt" P2S="$O/ownequip2_p2.txt" bash tools/own/sweep4.sh om7 run-m 29050 28081 test-own-v62-menu-acc-ring "$L/list-hb13.txt"
tlb om7; say "om7 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om8 "$P/patches/test-own-v62-acc" test-m-roam.iso 7400 "4700,5300,5620,6200,6520,7200" "$S/rt_p1.txt" "$S/rt_p2.txt" run-m 29050 28081 > "$B/om8.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/om8.log"
cat "$P/local/tests/om8-probe.txt" >> "$B/om8.log" 2>/dev/null
say "om8 done"
M3="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14,000E7E20:C SNAPS=$M3 FRAMES=14000 TOUT=500 SWEEP_PROBE_WAIT=500 LOGDIR=local/sweep/b15 TAG=r8mkS8 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS8 run-m 29050 28081 test-own-v62-snapB-kill65-roll-abort "$L/list-sr1.txt"
tlb mkS8; say "mkS8 done"
say "chain62 through"
