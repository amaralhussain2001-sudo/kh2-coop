#!/bin/bash
# TEST ONLY (eighth round, part 77): THE BUILD 17 CANDIDATE WITH THE FIFTY-SEVENTH GLUE (--hudowner): v89
# (patches/test-own-v89 / patches/test-v14-a), the v5 test disc.
#  one16: the toy cannon for 60,000 frames (fire, reload, sweep): the game's end must come with "TLB misses 0".
#  one17: the toy cannon for 9,000 frames, probe hud_probe.py: the HUD's owner must be nobody.
#  one18: the carpet escape and the sidecar, probe hud_probe.py: the HUD's owner must stay player 1's hero.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/one16.log .. one18.log; progress chain107.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain107.txt"; }
say "chain107 start"
SN=$(python -c "print(','.join(str(f) for f in range(6000, 60000, 3000)) + ',59900')")
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS=$SN FRAMES=60000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/b15 TAG=r8one16 P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh one16 run-m 29050 28081 test-own-v89-snapB "$L/list-nm63.txt"
say "one16 done"
ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one17 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one17 run-m 29050 28081 test-own-v89-snapB "$L/list-nm63.txt"
say "one17 done"
ISO=test-v5-tt137.iso PROBE="$T/hud_probe.py" SNAPS="4900,5600,6200,6800,7400,8000,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one18 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one18 run-m 29050 28081 test-own-v89-snapB "$L/list-one2.txt"
say "one18 done"
say "chain107 through"
