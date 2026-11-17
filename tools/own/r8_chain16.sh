#!/bin/bash
# TEST ONLY (eighth round, job 10's second half): the three bosses with a state of their own for the hero, with the
# candidate v52 (glues 30 to 43), HP held, strong heroes, both players Circle / Triangle / R1, 24,000 frames each.
#   lux   Luxord, the story fight (eh14 58): the card / the die, the time gauges
#   luxd  Luxord, the data fight (eh14 101)
#   mar   Marluxia (hb38 150) and mar2 (hb38 145): the countdown over the hero
#   xigd  Data Xigbar (eh10 100) and xig (eh10 57, the story fight): the sniper part
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress local/sweep/b15/chain16.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain16.txt"; }
say "chain16 start"
S6="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
run() {  # name, list line
  echo "$2" > "$L/list-$1.txt"
  SNAPS=$S6 FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
    bash tools/own/sweep4.sh $1 run-m 29050 28081 test-own-v52-snapB-god-strong "$L/list-$1.txt"
  say "$1 done"
}
run lux  "eh14 12 58 EH14_MS103 NO_FRIEND 58 58 58 0"
run luxd "eh14 12 101 EH14_MS103 NO_FRIEND 101 101 101 0"
run mar  "hb38 04 150 HB38_FM_MAR DEFAULT 150 150 150 0"
run mar2 "hb38 04 145 HB38_FM_MAR DEFAULT 145 145 145 0"
run xigd "eh10 12 100 EH10_MS102 DEFAULT 100 100 100 0"
run xig  "eh10 12 57 EH10_MS102 DEFAULT 57 57 57 0"
say "chain16 through"
