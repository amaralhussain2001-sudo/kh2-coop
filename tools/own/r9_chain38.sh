#!/bin/bash
# TEST ONLY (ninth round, job 3): DATA LUXORD (eh14 101) on v107: the whole state of both heroes (tools/own/hold_state_probe.py) around
# player 1's long FE (4940 .. 5100, 6000) and around player 2's short FE (9740 .. 9900). One lane (run-x5).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain38.txt"; }
say "chain38 start"
SN=$(python -c "print(','.join(str(f) for f in list(range(4900, 5120, 20)) + [6000] + list(range(9700, 9920, 20))))")
ISO=test-v5-tt137.iso PROBE="$T/hold_state_probe.py" SNAPS="$SN" FRAMES=10000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9lxN P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lxN run-x5 31550 28068 test-own-v107-snapB-god-cap "$B/list-eh14d.txt"
say "lxN done"
