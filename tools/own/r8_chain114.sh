#!/bin/bash
# TEST ONLY (eighth round; A LANE BESIDE THE QUEUE, sandbox run-x2, port 30950, PINE 28065):
# (1) THE EXPERIMENT v90, player 2's own ability switches (glue 58): the runs ab1 .. ab8 exactly as written in
#     r8_chain112.sh (which is NOT run); (2) the last five boss rooms of r8_chain111.sh (local/sweep/list-r9hb.txt:
#     Demyx in Hollow Bastion, the Hydra, the Groundshaker, the last Xemnas, the armoured Xemnas), as chain 113.
# Logs local/sweep/b15/ab1.log .. ab8.log, r9hb.log; progress chain114.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x2; PT=30950; PN=28065
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain114.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/$RD/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain114 start"
for k in ab1 ab2; do
  ISO=test-v5-tt137.iso PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8$k P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh $k $RD $PT $PN test-own-v90-$k "$L/list-dr.txt"
  tlb $k; say "$k done"
done
RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
SN="4900,5060,5160,5260,5340,5420,5500,5570,5660,5760,5860,6000,6300"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab3 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh ab3 $RD $PT $PN test-own-v90-ab3 "$L/list-hb13.txt"
tlb ab3; say "ab3 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab4 P1S="$S/newgame_only.txt" P2S="$O/ownabil_p2.txt" bash tools/own/sweep4.sh ab4 $RD $PT $PN test-own-v90-ab4 "$L/list-hb13.txt"
tlb ab4; say "ab4 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab5 P1S="$S/newgame_only.txt" P2S="$O/ownmenu_p2.txt" bash tools/own/sweep4.sh ab5 $RD $PT $PN test-own-v90-ab5 "$L/list-hb13.txt"
tlb ab5; say "ab5 done"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab6 P1S="$O/ownabil_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh ab6 $RD $PT $PN test-own-v90-ab4 "$L/list-hb13.txt"
tlb ab6; say "ab6 done"
for k in ab7 ab8; do
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS="4900,5200,5400,5800,6300" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8$k P1S="$S/newgame_only.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh $k $RD $PT $PN test-own-v90-$k "$L/list-hb13.txt"
  tlb $k; say "$k done"
done
say "the ability runs through"
ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8r9h P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh r9hb $RD $PT $PN test-own-v89-snapB-god "$L/list-r9hb.txt"
say "chain114 through"
