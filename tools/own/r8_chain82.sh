#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 16 CANDIDATE v74 (both heroes in Shan-Yu's clash)
# (patches/test-own-v74 / patches/test-v10-l, control patches/test-v10-l-nn), one run at a time, about two hours.
# Build 15 logs of the same steps are kept in local/reg-b15/. HIDDEN.
# Progress: local/reg-serial.log (the old one is moved to local/reg-b15/reg-serial-b15.log first).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log local/reg-b15/reg-serial-b15.log
echo "chain82 start $(date +%H:%M:%S)" >> local/sweep/b15/chain82.txt
bash tools/own/reg_serial.sh test-own-v74 test-v10-l b16
echo "chain82 through $(date +%H:%M:%S)" >> local/sweep/b15/chain82.txt
