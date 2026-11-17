#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 15 CANDIDATE v62 (own armour and accessories for player 2)
# (patches/test-own-v62 / patches/test-v9-d, control patches/test-v9-d-nn), one run at a time, about two hours.
# Build 14 logs of the same steps are kept in local/reg-b14/. HIDDEN.
# Progress: local/reg-serial.log (the old one is moved to local/reg-b14/reg-serial-b14.log first).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log local/reg-b14/reg-serial-b14.log
echo "chain63 start $(date +%H:%M:%S)" >> local/sweep/b15/chain63.txt
bash tools/own/reg_serial.sh test-own-v62 test-v9-d b15
echo "chain63 through $(date +%H:%M:%S)" >> local/sweep/b15/chain63.txt
