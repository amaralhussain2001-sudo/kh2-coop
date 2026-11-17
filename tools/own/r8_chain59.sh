#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): DOES A PLACE BEYOND THE HERO'S COUNT DO NOTHING?
# Build 14 (v58) + HP held + one item number written into Sora's record (save + 0x24F0):
#   inA  accessory "Medal" (0x35) in ACCESSORY PLACE 1 (+ 0x24): the control, the stats must change
#   inB  the same in accessory place 5 (+ 0x2C, beyond the count): the stats must NOT change
#   inC  armour "Elven Bandana" (0x43) in ARMOUR PLACE 1 (+ 0x14): the control
#   inD  the same in armour place 5 (+ 0x1C): the stats must NOT change
# Read: both slots' stat words (slot + 0x180, 16 bytes) and + 0x188.. ; compare with run or1 (no item).
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs: local/sweep/b15/inA.log ..; progress chain59.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain59.txt"; }
say "chain59 start"
for n in A B; do
  PROBE="$T/sweepm_probe.py" CHAINS=0034E948+48C@180:20,000F05CC+48C@180:20,0034E948+48C@1A0:20,000F05CC+48C@1A0:20 RANGES=0032E020:40 SNAPS="5200,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8in$n \
    P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh in$n run-m 29050 28081 test-own-v58-snapB-god-acc$n "$L/list-hb17.txt"
  say "in$n done"
done
PROBE="$T/sweepm_probe.py" CHAINS=0034E948+48C@180:20,000F05CC+48C@180:20,0034E948+48C@1A0:20,000F05CC+48C@1A0:20 RANGES=0032E020:40 SNAPS="5200,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8inC \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh inC run-m 29050 28081 test-own-v58-snapB-god-armA "$L/list-hb17.txt"
say "inC done"
PROBE="$T/sweepm_probe.py" CHAINS=0034E948+48C@180:20,000F05CC+48C@180:20,0034E948+48C@1A0:20,000F05CC+48C@1A0:20 RANGES=0032E020:40 SNAPS="5200,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8inD \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh inD run-m 29050 28081 test-own-v58-snapB-god-armB "$L/list-hb17.txt"
say "inD done"
say "chain59 through"
