#!/bin/bash
# TEST ONLY (eighth round, plan row 44): which check dims the other hero's Drive row while one hero is in a form?
# Roam disc + Drive kit + the row recorder (tools/own/make_rowrec.py). ONE RUN AT A TIME on sandbox run-m.
#   rowA  player 1 takes the first form (Limit Form on this disc), then player 2 tries his Drive row
#   rowB  the other way round
# Logs: local/sweep/b15/rowA.log, rowB.log; the recorder's lines: local/tests/t15-rowA-probe.txt, t15-rowB-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; B="$P/local/sweep/b15"
cd "$P" || exit 1
# (put in front on 2026-11-14 00:25) kcbad: the Keyblade change again with the bad-pointer recorder at 0x00193608
L="$P/local/sweep"
PROBE="$P/tools/own/recbad_probe.py" SNAPS="5060,5540,5860,6200,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcbad P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kcbad run-m 29050 28081 test-own-v33-menu-bad "$L/list-hb13.txt"
echo "kcbad done $(date +%H:%M:%S)" >> "$B/chain4.txt"
SN="4690,5000,5380,5450,5540,5620,5800,6400"
PROBE="$P/tools/own/rowrec_probe.py" bash tools/own/dusk_one.sh t15-rowA "$P/patches/test-own-v33-forms-rowrec" test-m-roam.iso 6500 "$SN" "$O/drive1_p1.txt" "$O/drivelate_p2.txt" run-m 29050 28081 > "$B/rowA.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/rowA.log"
PROBE="$P/tools/own/rowrec_probe.py" bash tools/own/dusk_one.sh t15-rowB "$P/patches/test-own-v33-forms-rowrec" test-m-roam.iso 6500 "$SN" "$O/drivelate_p1.txt" "$O/drive_p2.txt" run-m 29050 28081 > "$B/rowB.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/rowB.log"
echo "chain4 through $(date +%H:%M:%S)" >> "$B/chain4.txt"
