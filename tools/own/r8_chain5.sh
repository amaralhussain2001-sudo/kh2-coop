#!/bin/bash
# TEST ONLY (eighth round, plan row 39, feasibility): the twin's unit slot reads a SECOND character record
# (tools/own/make_rec2test.py). ONE RUN AT A TIME on sandbox run-m.
#   e1a  record B: most HP 60, Strength 80: do the twin's slot values follow B?  (1000 Heartless)
#   e1b  Second Chance and Once More ONLY in B (the twin): Data Roxas, HP timelines
#   e1c  Second Chance and Once More ONLY in Sora's record (player 1): the same
# Logs: local/sweep/b15/e1a.log ...; progress local/sweep/b15/chain5.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain5.txt"; }
say "chain5 start"
# (put in front on 2026-11-14 00:33) kcbad2: the Keyblade change with the bad-pointer recorder at 0x0017FE10 (judging a1)
PROBE="$T/recbad_probe.py" SNAPS="5060,5540,5860,6200,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcbad2 P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kcbad2 run-m 29050 28081 test-own-v33-menu-bad2 "$L/list-hb13.txt"
say "kcbad2 done"
PROBE="$T/sweepm_probe.py" CHAINS=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4 SNAPS="5200,6000,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8e1a \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh e1a run-m 29050 28081 test-own-v33-snapB-r2a "$L/list-hb17.txt"
say "e1a done"
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8e1b \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh e1b run-m 29050 28081 test-own-v33-snapB-r2b "$L/list-dr.txt"
say "e1b done"
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8e1c \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh e1c run-m 29050 28081 test-own-v33-snapB-r2c "$L/list-dr.txt"
say "e1c done"
say "chain5 through"
