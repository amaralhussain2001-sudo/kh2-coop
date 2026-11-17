#!/bin/bash
# TEST ONLY (eighth round; a lane, sandbox run-x2, port 30950, PINE 28065): CANDIDATE v92 (= v89 + glue 58 "player
# 2's own ability switches" + glue 59 "a boss that holds one hero captures that hero"), ITS OWN CHECKS AGAIN:
#  one19  the toy cannon for 60,000 frames (as one16 on v89): the game's end with "TLB misses 0".
#  one20  the carpet escape and the sidecar with hud_probe.py (as one18).
#  ab1c / ab2c  Data Roxas, the two abilities on for one hero only, each way (as ab1 / ab2 on v90).
#  ab4c   player 2 switches Second Chance off in his own Abilities menu (as ab4b on v91).
# Logs local/sweep/b15/one19.log, one20.log, ab1c.log, ab2c.log, ab4c.log; progress chain126.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x2; PT=30950; PN=28065
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain126.txt"; }
say "chain126 start"
ISO=test-v5-tt137.iso PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8ab1c P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh ab1c $RD $PT $PN test-own-v92-ab1 "$L/list-dr.txt"
say "ab1c done"
ISO=test-v5-tt137.iso PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8ab2c P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh ab2c $RD $PT $PN test-own-v92-ab2 "$L/list-dr.txt"
say "ab2c done"
RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C,0032E35C:60
SN="4900,5060,5160,5260,5340,5420,5500,5600,5700,5800,5900,6000,6300"
ISO=test-v5-tt137.iso PROBE="$T/sweepm_probe.py" RANGES=$RG SNAPS=$SN FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8ab4c P1S="$S/newgame_only.txt" P2S="$O/ownabil2_p2.txt" bash tools/own/sweep4.sh ab4c $RD $PT $PN test-own-v92-ab4 "$L/list-hb13.txt"
say "ab4c done"
ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one20 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one20 $RD $PT $PN test-own-v92-snapB "$L/list-one2.txt"
say "one20 done"
SN2=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN2 FRAMES=60000 TOUT=2400 SWEEP_PROBE_WAIT=2400 LOGDIR=local/sweep/b15 TAG=r8one19 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one19 $RD $PT $PN test-own-v92-snapB "$L/list-nm63.txt"
say "one19 done"
say "chain126 through"
