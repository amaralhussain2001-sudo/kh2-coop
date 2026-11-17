#!/bin/bash
# TEST ONLY (tenth round, open item g: a Drive ball taken by player 2). No Drive ball dropped in eight runs of part 116, so the kit
# -hp2dr makes the HP balls (prize kinds 0 / 1) give Drive 1 / 3 (the rows of Drive balls 7 / 8 in the table 0x0036D578): every HP
# ball a hero takes then goes through the game's Drive path (0x001A52A8 -> 0x00179A68 on the receiver). Candidate v130, kit
# -forms-god-strong-pkl-hp2dr (Drive 0 for both at 4900), the 1000 Heartless (hb17 66), player 1 runs far away, player 2 fights
# (as pmB of part 116). Probe prize_probe.py (prizes by kind and receiver, each hero's Drive). Lane run-x10.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
ISO=test-s1-tt137.iso PROBE="$T/prize_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9pdA P1S="$O/walkfar_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh pdA run-x10 32550 28073 test-own-v130-forms-god-strong-pkl-hp2dr "$L/list-hb17.txt"
