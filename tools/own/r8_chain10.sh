#!/bin/bash
# TEST ONLY (eighth round, register G5): player 2 opens a chest. hb03, entrance 99: a chest stands about 340 units
# ahead of the twin's place (chest 0x0140 at 1116 / -23; the twin starts at 1159 / 312, facing it).
# ONE RUN on sandbox run-m. Log: local/sweep/b15/chest.log (places of both heroes and their distance to the chest)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
echo "hb03 04 0 HB03_ROAM DEFAULT 0 0 0 99" > "$L/list-chest.txt"
PROBE="$P/tools/own/pos_probe.py" POINTS="1116:-23" SNAPS="4690,4880,4950,5000,5100,5200,5400,5700" FRAMES=6000 LOGDIR=local/sweep/b15 TAG=r8chest \
  P1S="$O/ctl_p1.txt" P2S="$O/chest_p2.txt" bash tools/own/sweep4.sh chest run-m 29050 28081 test-own-v33 "$L/list-chest.txt"
# (added 2026-11-14 00:43) sp2 / sp3: the spawn-zone test again from the Borough's entrance 0 (in sp1 / sp0 the heroes started INSIDE
# a zone, so both runs had enemies at once). Player 2 runs "stick up" for 200 frames alone; places of both heroes as float words.
echo "hb09 04 1 HB09_ROAM DEFAULT 0 1 0 0" > "$L/list-sp2.txt"
for kv in "sp2 test-own-v35" "sp3 test-own-v33"; do set -- $kv
  PROBE="$P/tools/own/sweepm_probe.py" CHAINS=00352400@70:C,000F05CC@70:C SNAPS="4690,4880,5000,5100,5200,5400,6000,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/ctl_p1.txt" P2S="$O/spawn3_p2.txt" bash tools/own/sweep4.sh $1 run-m 29050 28081 $2 "$L/list-sp2.txt"
done
# (added 2026-11-14 00:55) tf2b: run tf2 again (player 2 picks Wisdom while player 1 is in Valor: the screen went black at 5599 and
# the memory read zero). Dense pictures around the pick, the whole emulator log kept.
PROBE="$P/tools/own/heap_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tf2b "$P/patches/test-own-v37-forms-heap" test-s1-hb9f.iso 6000 "4690,5000,5450,5540,5565,5572,5578,5584,5588,5592,5595,5597,5599,5601,5604,5610,5630,5700,5900" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tf2b.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tf2b.log"
cp "$P/local/run-m/p1/logs/emulog.txt" "$B/tf2b-emulog-full.txt" 2>/dev/null
cat "$P/local/tests/t15-tf2b-probe.txt" >> "$B/tf2b.log" 2>/dev/null
# (added 2026-11-14 00:56) gu4 / gu5: plan row 43, third try. Runs gu2 / gu3 (a quiet room) gave 20/20 at once in both builds: outside a
# fight the game refills a fallen hero itself. Now the 1000 Heartless again, heroes with 100 HP and Defense 150 (record bytes), the twin
# falls at 6500, player 1 fights on. Expected at the get-up: 26/100 with the candidate (gu4), 25/100 with build 12 (gu5).
for kv in "gu4 test-own-v37-snapB-hp100-kill65p2" "gu5 test-own-v33-snapB-hp100-kill65p2"; do set -- $kv
  PROBE="$P/tools/own/hp_poll_probe.py" FROM=6400 TO=9900 SWEEP_PROBE_WAIT=900 SNAPS="5200,6600,9100,9300,9900" FRAMES=10000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mash_new40_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh $1 run-m 29050 28081 $2 "$L/list-hb17.txt"
done
# (added 2026-11-14 00:59) lb3 / sam3: the Large Body and the Samurai once more. In lb2 player 2's Triangle started Auron's Limit
# (it cleared the room); in sam2 the Dusks' Reversal came to player 2 but no Samurai took his stance near him. Now: no helpers,
# player 2 presses ONLY Triangle (nothing dies), HP held, 16000 frames, a picture every 400 frames.
echo "he05 06 111 HE05_MS102 NO_FRIEND 111 111 111 0" > "$L/list-he05n.txt"
S3="5200,5600,6000,6400,6800,7200,7600,8000,8400,8800,9200,9600,10000,10400,10800,11200,11600,12000,12400,12800,13200,13600,14000,14400,14800,15200,15600,15900"
SNAPS=$S3 FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8lb3 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh lb3 run-m 29050 28081 test-own-v33-snapB-god "$L/list-he05n.txt"
SNAPS=$S3 FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8sam3 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh sam3 run-m 29050 28081 test-own-v33-snapB-god "$L/list-hb08b.txt"
echo "chain10 through $(date +%H:%M:%S)" >> "$B/chain10.txt"
