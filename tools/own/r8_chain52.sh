#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 14 CANDIDATE v58
# (patches/test-own-v58 / patches/test-v8-z, control patches/test-v8-z-nn), one run at a time, about two hours.
# Build 13's logs of the same steps are kept in local/reg-b13/ (copied before this run writes over them).
# Progress: local/reg-serial.log (the old one is moved to local/reg-b13/reg-serial-b13.log first).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log local/reg-b13/reg-serial-b13.log
echo "chain52 start $(date +%H:%M:%S)" >> local/sweep/b15/chain52.txt
bash tools/own/reg_serial.sh test-own-v58 test-v8-z b14
echo "chain52 through $(date +%H:%M:%S)" >> local/sweep/b15/chain52.txt
