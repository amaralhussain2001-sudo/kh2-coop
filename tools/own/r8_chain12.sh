#!/bin/bash
# TEST ONLY (eighth round, plan row 41): hurt during a Limit, second version of the recorder (make_hurtkit2.py: the
# table is sorted by the action of the hero's step BEFORE the hit; Limit actions seen so far: FC, FD, FE, 100, 101).
#   lm2b  player 2 does the Limit (the 1000 Heartless), player 1 attacks
#   lm1b  player 1 does the Limit, player 2 attacks (the control: what the original rule gives player 1)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/lm2b.log, lm1b.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
# (put in front on 2026-11-14 00:46) kcfix: THE KEYBLADE CHANGE WITH THE FIX (thirty-third glue; candidate test-own-v36, base test-v8-c)
SNAPS="5060,5360,5540,5860,5960,6200,6600,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcfix P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kcfix run-m 29050 28081 test-own-v36-menu "$L/list-hb13.txt"
echo "kcfix done $(date +%H:%M:%S)" >> "$B/chain12.txt"
LIM="5200,5500,5800,6200,6800,7100,7900,8300,8900"
PROBE="$T/hurt_probe.py" SNAPS=$LIM LOGDIR=local/sweep/b15 TAG=r8lm2b P1S="$O/mash_new40_p1.txt" P2S="$O/lim_jump_p2.txt" \
  bash tools/own/sweep4.sh lm2b run-m 29050 28081 test-own-v33-snapB-god-limit-hurt2 "$L/list-hb17.txt"
PROBE="$T/hurt_probe.py" SNAPS=$LIM LOGDIR=local/sweep/b15 TAG=r8lm1b P1S="$O/lim_jump_p1.txt" P2S="$O/mash_long_p2.txt" \
  bash tools/own/sweep4.sh lm1b run-m 29050 28081 test-own-v33-snapB-god-limit-hurt2 "$L/list-hb17.txt"
echo "chain12 through $(date +%H:%M:%S)" >> "$B/chain12.txt"
