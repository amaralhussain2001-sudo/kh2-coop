#!/bin/bash
# TEST ONLY (eighth round), the queue after r8_master2.sh. ONE RUN AT A TIME on sandbox run-m.
#   tfab   fault F6: player 2 picks Wisdom while player 1 is in Valor -> the game calls abort() and leaves to the
#          PS2 browser. The abort recorder (tools/own/make_abortrec.py) keeps the game alive and notes the callers.
#   ffd3   Final Form through the west door of Merlin's House (36 frames "up" first), then jump, glide, attack
#   chest2 player 2 opens a chest: the chest is BEHIND his start, so "stick down" for 40 frames, then Triangle
# Logs: local/sweep/b15/; progress local/sweep/b15/chain15.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain15.txt"; }
say "chain15 start"
PROBE="$T/sweepm_probe.py" RANGES=000E7100:20,000E7120:400,000F1F80:40 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tfab "$P/patches/test-own-v37-forms-heap-abort" test-s1-hb9f.iso 6000 "4690,5540,5590,5700,5900" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tfab.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tfab.log"
cat "$P/local/tests/t15-tfab-probe.txt" >> "$B/tfab.log" 2>/dev/null
say "tfab done"
# tf3: the same test with the thirty-fifth glue (candidate v38: a hero's form files stay while the other hero changes), abort recorder kept
TF="4690,5000,5380,5450,5540,5600,5700,5900,6300,6480,6600,6780,6950,7100,7280,7400,7500"
PROBE="$T/sweepm_probe.py" RANGES=000E7100:14,000F1F80:40 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tf3 "$P/patches/test-own-v38-forms-heap-abort" test-s1-hb9f.iso 7600 "$TF" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tf3.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tf3.log"
cat "$P/local/tests/t15-tf3-probe.txt" >> "$B/tf3.log" 2>/dev/null
say "tf3 done"
# gp5 / cap2: plan row 9, first step (candidate v39 with the thirty-sixth glue: a boss's scripted move takes the hero who is in it,
# or the nearer hero). gp5 = run gp4 again: player 2 ALONE against Shan-Yu, player 1 only starts the game, HP held, strong heroes.
# cap2 = run cap0 again: both players Circle / Triangle, the recorder at the paired-move routine (who is pulled in).
LONG="5200,7000,9000,11000,13000,15000,17000,19000,21000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp5 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh gp5 run-m 29050 28081 test-own-v39-snapB-god-strong "$L/list-sy.txt"
say "gp5 done"
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap2 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap2 run-m 29050 28081 test-own-v39-snapB-def-cap "$L/list-sy.txt"
say "cap2 done"
# mkA / mkB: plan row 45, King Mickey for two (thirty-seventh glue). Shan-Yu, clean jump; both heroes fall at 6500, the roll always
# wins, the abort recorder is in. mkA = candidate v40 (a Mickey for each player), mkB = v40m1 (one Mickey, both heroes come back).
# Words after " | ": the engine player and the parking place (0034E948:8), the twin (000F05CC), the parked twin (000E7C00), the recorder.
MS="5200,6400,6700,6900,7000,7100,7200,7400,7700,8000,8500,8900,9500,10000,11000,11900"
for kv in "mkA test-own-v40-snapB-kill65-roll-abort" "mkB test-own-v40m1-snapB-kill65-roll-abort"; do set -- $kv
  PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$MS FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 run-m 29050 28081 $2 "$L/list-sy.txt"
  say "$1 done"
done
PROBE="$T/sweep_probe.py" bash tools/own/dusk_one.sh t15-finaldoor3 "$P/patches/test-own-v33-forms" test-s1-hb13s.iso 7400 "4690,5000,5250,5380,5600,5800,6000,6100,6230,6260,6450,6630,6660,6900,7100,7350" "$O/finaldoor3_p1.txt" "$O/finaldoor3_p2.txt" run-m 29050 28081 > "$B/finaldoor3.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/finaldoor3.log"
cat "$P/local/tests/t15-finaldoor3-probe.txt" >> "$B/finaldoor3.log" 2>/dev/null
say "ffd3 done"
PROBE="$P/tools/own/pos_probe.py" POINTS="1116:-23" SNAPS="4690,4880,4950,5000,5100,5200,5400,5700" FRAMES=6000 LOGDIR=local/sweep/b15 TAG=r8chest2 \
  P1S="$O/ctl_p1.txt" P2S="$O/chest2_p2.txt" bash tools/own/sweep4.sh chest2 run-m 29050 28081 test-own-v33 "$L/list-chest.txt"
say "chest2 done"
# lb4 / sam4: the Large Body and the Samurai, fourth try. In lb3 (party NO_FRIEND) Auron was there all the same and player 2's
# Triangle started his Limit again (actions FC / 101), which kills the Large Body. Now the heroes have NO MP (record bytes 24F6 /
# 24F7 = 0), so no Limit. Both runs with the action timeline (act_poll_probe.py) instead of pictures every 400 frames.
S4="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=15900 SNAPS=$S4 FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8lb4 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh lb4 run-m 29050 28081 test-own-v33-snapB-god-nomp "$L/list-he05.txt"
say "lb4 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=12000 SNAPS=$S4 FRAMES=12500 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8sam4 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh sam4 run-m 29050 28081 test-own-v33-snapB-god "$L/list-hb08b.txt"
say "sam4 done"
say "chain15 through"
