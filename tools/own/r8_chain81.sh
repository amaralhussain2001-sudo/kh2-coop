#!/bin/bash
# TEST ONLY (eighth round, the vehicle items: a carpet under player 2): WHAT BINDS THE CARPET TO A HERO?
# Build 15 (candidate v62) + the recorder at the paired-move routine 0x00180378 (ring: return address, a0 = the
# captor's motion part, a1 = the victim; the stack of the first call), on the v5 test disc, the carpet fight
# al14 86 (two carpet riders, one carpet). Is the carpet a "victim" of the hero in a paired move?
#   carp1  both players move and attack (sp_p1 / sp_p2), 7,200 frames
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/carp1.log; progress chain81.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain81.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain81 start"
ISO=test-v5-tt137.iso PROBE="$T/rec_probe.py" SNAPS="5000,5200,5600,6000,6500,7000" FRAMES=7200 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8carp1 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh carp1 run-m 29050 28081 test-own-v62-snapB-cap "$L/list-carp86.txt"
tlb carp1; say "carp1 done"
say "chain81 through"
