#!/bin/bash
# TEST ONLY (eighth round, plan row 39 stage 1b, AN EXPERIMENT): PLAYER 2'S OWN ABILITY SWITCHES (glue 58, --ownabil),
# candidate v90 (patches/test-own-v90 / patches/test-v15-a), the v5 test disc.
#  ab1  Data Roxas; Second Chance + Once More ON for the hero, OFF for player 2 (his switches 0000): the first hit
#       must leave the hero at 1 HP and take the twin down.            ab2: the other way round.
#  ab3  Merlin's House; hero: place 0 on, place 1 off; player 2: place 1 on. PLAYER 2 opens and closes the menu:
#       the switches must change places while it is open and come back.
#  ab4  both on for both; PLAYER 2 goes to Abilities > Sora and presses Circle: one of HIS switches must change,
#       the hero's must be as before after the close.
#  ab5  no mark: his switches must be made from the hero's (0001) by themselves.
#  ab6  both on for both; PLAYER 1 does the same in his menu: one of the HERO's switches changes, player 2's none.
# Dumps: the hero's first ability places (0032E074), the view T's (000E7D54), player 2's switches + mark
# (0032E390), the flags (000E7E20), King Mickey's record (0032E35C: counts at + 0x10 .. + 0x12, the places).
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/ab1.log .. ab6.log; progress chain112.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain112.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain112 start"
for k in ab1 ab2; do
  ISO=test-v5-tt137.iso PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8$k P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh $k run-m 29050 28081 test-own-v90-$k "$L/list-dr.txt"
  tlb $k; say "$k done"
done
RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
SN="4900,5060,5160,5260,5340,5420,5500,5570,5660,5760,5860,6000,6300"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab3 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh ab3 run-m 29050 28081 test-own-v90-ab3 "$L/list-hb13.txt"
tlb ab3; say "ab3 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab4 P1S="$S/newgame_only.txt" P2S="$O/ownabil_p2.txt" bash tools/own/sweep4.sh ab4 run-m 29050 28081 test-own-v90-ab4 "$L/list-hb13.txt"
tlb ab4; say "ab4 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab5 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh ab5 run-m 29050 28081 test-own-v90-ab5 "$L/list-hb13.txt"
tlb ab5; say "ab5 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab6 P1S="$O/ownabil_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh ab6 run-m 29050 28081 test-own-v90-ab4 "$L/list-hb13.txt"
tlb ab6; say "ab6 done"
say "chain112 through"
# (added before the chain's start, 23:25) ab7 / ab8: the game's own "give an ability" 0x00188B68(Sora's record, Once More,
# on = 1 / 0) is called once at frame 5300 (kit make_callonce.py); the hero has Second Chance in place 0, player 2's
# switches are 0000 with the mark. After it: place 1 = 81A0 / 01A0, and player 2's switch of place 1 = on / off.
for k in ab7 ab8; do
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8$k P1S="$S/newgame_only.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh $k run-m 29050 28081 test-own-v90-$k "$L/list-hb13.txt"
  tlb $k; say "$k done"
done
say "chain112 really through"
