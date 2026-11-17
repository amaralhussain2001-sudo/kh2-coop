#!/bin/bash
# TEST ONLY (tenth round, deeper checks of glues 74 and 75 on v134 = BUILD 22's files; after r10_chain29.sh frees its five lanes):
#  GLUE 74 (item boxes; Agrabah's city al00 program 2; recorder tools/own/make_rec_box.py: 0x000F1D00 boxes made, + 4 taken by player 1,
#  + 8 by player 2, + 0xC by others, + 0x10 the last item; bags: the game's bytes 0x0032F0B0 (item 1, Potion) / 0x0032F13F (Shard), player
#  2's stock of item 1 at 0x0032E380, his bag byte 0x0032E3D8 (Shard)):
#   bR1 run-m    Blazing Shard boxes, PLAYER 2 fights, player 1 far away       bR2 run-v3   Shard boxes, PLAYER 1 fights, player 2 far away
#   bR3 run-v3b  POTION boxes, PLAYER 2 fights, player 1 far away (a fight item: the "taker's item places" branch, both stocks)
#  GLUE 75 (Drive Form files through doors; disc test-s1-hb13s.iso, kit -forms):
#   fT1 run-v3c  TWO FORMS: player 1 Limit Form, player 2 Final Form, both through the west door (formdoor3), filepool_probe.py
#   fT2 run-x1   the same, bind_probe.py
#   then fM1 run-m  player 2 in Final Form through the west door and BACK AND FORTH three more times (finaldoor4), filepool_probe.py
#        fM2 run-v3 the same, bind_probe.py
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
bx() { RANGES=0032F0B0:4,0032F13C:4,0032E380:4,0032E3D8:4,000F1D00:14 ISO=test-s1-tt137.iso PROBE="$T/sweepm_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 $7 "$B/list-al00lb.txt"; }
fr() { PROBE="$T/$5" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/test-own-v134-forms" test-s1-hb13s.iso $6 "$7" "$O/$8" "$O/$9" $2 $3 $4 > "$B/$1.log" 2>&1; }
bx bR1 run-m 29050 28081 walkfar_p1.txt mashrc_long_p2.txt test-own-v134-snapB-god-strong-rbs &
bx bR2 run-v3 30150 28061 mashrc_long_p1.txt far_p2.txt test-own-v134-snapB-god-strong-rbs &
bx bR3 run-v3b 30350 28062 walkfar_p1.txt mashrc_long_p2.txt test-own-v134-snapB-god-strong-rbp &
fr fT1 run-v3c 30550 28063 filepool_probe.py 7400 "4690,5300,5590,6000,6450,6900,7350" formdoor3_p1.txt formdoor3_p2.txt &
fr fT2 run-x1 30750 28064 bind_probe.py 7400 "4690,5300,5590,6000,6450,6900,7350" formdoor3_p1.txt formdoor3_p2.txt &
wait
fr fM1 run-m 29050 28081 filepool_probe.py 9000 "5250,6100,6900,7700,8500,8950" finaldoor4_p1.txt finaldoor4_p2.txt &
fr fM2 run-v3 30150 28061 bind_probe.py 9000 "5250,6100,6900,7700,8500,8950" finaldoor4_p1.txt finaldoor4_p2.txt &
wait
echo done > "$B/r10chain32.done"
