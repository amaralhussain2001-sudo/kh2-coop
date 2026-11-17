#!/bin/bash
# TEST ONLY: the Struggle rules screen with only player 2 pressing, on the six variants of tools/own/make_padbits.py
# (two sandboxes side by side). Prints the picture layout at the snapshots; the pictures tell the rest.
# usage: rules_bits.sh <prefix> <namePrefix> <iso> <frames> <snaps> <p1script> <p2script>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
half() {  # sandbox port pine bits...
  rd=$1; pt=$2; pn=$3; shift 3
  for b in "$@"; do
    bash "$P/tools/own/dusk_one.sh" "$NP$b" "$P/patches/$PRE$b" "$ISO" "$FRAMES" "$SNAPS" "$S1" "$S2" "$rd" "$pt" "$pn"
  done
}
PRE=$1; NP=$2; ISO=$3; FRAMES=$4; SNAPS=$5; S1=$6; S2=$7
half run-v3 30150 28061 0 2 4 &
half run-v3b 30350 28062 1 3 5 &
wait
