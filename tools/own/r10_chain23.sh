#!/bin/bash
# TEST ONLY (tenth round, candidate v133 = v132 + glues 74 --boxpick and 75 --formroom), six lanes:
#  ITEM BOXES (open item g; Agrabah's city al00 program 2, disc test-s1-tt137.iso, kit -snapB-god-strong-box: every prize drop also
#  drops a Blazing Shard box, item 0x013D; probe sweepm_probe.py: the game's bag byte 0x0032F13F, player 2's bag byte 0x0032E3D8):
#   bxA-v133 run-x5  player 1 runs far away, PLAYER 2 FIGHTS        bxA-v132 run-x6  the same on v132 (control: he cannot take a box)
#   bxB-v133 run-x7  PLAYER 1 FIGHTS, player 2 runs far away
#  DRIVE FORM FILES THROUGH A DOOR (open item e; f8B of part 92: Merlin's house with the helpers, disc test-s1-hb13s.iso, kit -forms,
#  player 2 takes Final Form and goes through the west door; scripts finaldoor3_p1 / _p2, 7,400 frames):
#   frA-v133 run-x8  probe bind_probe.py        frB-v133 run-x9  probe filepool_probe.py (keep-numbers)   frB-v132 run-x10 control
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
bx() { RANGES=0032F13C:4,0032E3D8:4,0034F240:4,000E7FAC:4 ISO=test-s1-tt137.iso PROBE="$T/sweepm_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 $7 "$B/list-al00lb.txt"; }
fr() { PROBE="$T/$5" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/$6" test-s1-hb13s.iso 7400 "4690,5250,5600,6100,6450,6900,7350" "$O/finaldoor3_p1.txt" "$O/finaldoor3_p2.txt" $2 $3 $4 > "$B/$1.log" 2>&1; }
bx bxA3 run-x5 31550 28068 walkfar_p1.txt mashrc_long_p2.txt test-own-v133-snapB-god-strong-box &
bx bxA2 run-x6 31750 28069 walkfar_p1.txt mashrc_long_p2.txt test-own-v132-snapB-god-strong-box &
bx bxB3 run-x7 31950 28070 mashrc_long_p1.txt far_p2.txt test-own-v133-snapB-god-strong-box &
fr frA3 run-x8 32150 28071 bind_probe.py test-own-v133-forms &
fr frB3 run-x9 32350 28072 filepool_probe.py test-own-v133-forms &
fr frB2 run-x10 32550 28073 filepool_probe.py test-own-v132-forms &
wait
