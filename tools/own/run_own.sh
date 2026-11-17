#!/bin/bash
# One own-screen test run: two linked copies, own-view emulator (view12) on both, snapshots of what each PC shows.
# Runs on the hidden test desktop (tools/quiet_launch.py). Results: local/tests/<name>/
# usage: run_own.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <p1script> <p2script> <then> <upscale> [patchDir] [extra v3_session options...]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
n=$1; iso=$2; fr=$3; sp=$4; sn=$5; s1=$6; s2=$7; th=$8; up=$9; pd=${10:-$P/patches/merged-v6-own}
if [ $# -ge 10 ]; then shift 10; else shift $#; fi
EXE="$P/emulator-src/builds/view12/pcsx2-qtx64.exe"
VF="$P/patches/own-view/SLPM-66675_F266B00B.view"
python -I "$P/tools/lane-v3/v3_session.py" run "$n" --iso "$P/local/iso/$iso" --players 2 --frames "$fr" --speed "$sp" --snap "$sn" \
  --script "$s1" --script2 "$s2" --then "$th" --bot "$th" --patch-dir "$pd" --fresh-card --exe1 "$EXE" --exe2 "$EXE" --view-file "$VF" \
  --snapview1 1 --snapview2 1 --upscale1 "$up" --upscale2 "$up" --timeout 900 "$@" > "$P/local/tests/$n-harness.txt" 2>&1
echo "$n: $(grep -E 'session closed|OUT OF SYNC|TIMED OUT' "$P/local/tests/$n-harness.txt" | head -1 | cut -c12-90) | p1 TLB misses $(grep -c 'TLB Miss' "$P/local/run-v3/p1/logs/emulog.txt")"
