#!/bin/bash
# TEST ONLY (eighth round, plan row 39 stage 1b, the experiment's second form; A LANE BESIDE THE QUEUE, the new
# sandbox run-x4, port 31350, PINE 28067): candidate v91 (patches/test-own-v91 / patches/test-v15-b = v90 + "the
# twin's view gets a given ability at once"), the v5 test disc, Merlin's House.
#  ab4b  both abilities on for both; PLAYER 2: Abilities > Sora > the first ability > "Don't Equip" (ownabil2_p2):
#        HIS switch of place 0 must go off (his five shorts 0003 -> 0002), the hero's must be as before.
#  ab6b  the same by PLAYER 1 (ownabil2_p1): the hero's place 0 goes off (819F -> 019F), player 2's stay 0003.
#  ab7b  the game's "give an ability" (Once More, on) at frame 5300: the twin's view T must show it at once.
# Dumps as in chain 114. Logs local/sweep/b15/ab4b.log, ab6b.log, ab7b.log; progress chain117.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x4; PT=31350; PN=28067
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain117.txt"; }
say "chain117 start"
RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
SN="4900,5060,5160,5260,5340,5420,5500,5600,5700,5800,5900,6000,6300"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab4b P1S="$S/newgame_only.txt" P2S="$O/ownabil2_p2.txt" bash tools/own/sweep4.sh ab4b $RD $PT $PN test-own-v91-ab4 "$L/list-hb13.txt"
say "ab4b done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab6b P1S="$O/ownabil2_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh ab6b $RD $PT $PN test-own-v91-ab4 "$L/list-hb13.txt"
say "ab6b done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab7b P1S="$S/newgame_only.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh ab7b $RD $PT $PN test-own-v91-ab7 "$L/list-hb13.txt"
say "ab7b done"
say "chain117 through"
