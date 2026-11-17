#!/bin/bash
# TEST ONLY (eighth round): CANDIDATE v93's OWN CHECKS that are not in the regression, two lanes:
#  run-m   one21 = the toy cannon for 60,000 frames (as one16 / one19): the game's end with "TLB misses 0".
#  run-v3  ab1d (Data Roxas, the abilities on for the hero only), ab4d (player 2 switches Second Chance off in
#          his own menu), one22 (the carpet escape and the sidecar with hud_probe.py).
# Logs local/sweep/b15/one21.log, ab1d.log, ab4d.log, one22.log; progress chain129.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain129.txt"; }
say "chain129 start"
(
  SN2=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN2 FRAMES=60000 TOUT=2400 SWEEP_PROBE_WAIT=2400 LOGDIR=local/sweep/b15 TAG=r8one21 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one21 run-m 29050 28081 test-own-v93-snapB "$L/list-nm63.txt"
  say "one21 done"
) &
(
  ISO=test-v5-tt137.iso PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8ab1d P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh ab1d run-v3 30150 28061 test-own-v93-ab1 "$L/list-dr.txt"
  say "ab1d done"
  RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
  SN="4900,5060,5160,5260,5340,5420,5500,5600,5700,5800,5900,6000,6300"
  ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab4d P1S="$S/newgame_only.txt" P2S="$O/ownabil2_p2.txt" bash tools/own/sweep4.sh ab4d run-v3 30150 28061 test-own-v93-ab4 "$L/list-hb13.txt"
  say "ab4d done"
  ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one22 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one22 run-v3 30150 28061 test-own-v93-snapB "$L/list-one2.txt"
  say "one22 done"
) &
wait
say "chain129 through"
