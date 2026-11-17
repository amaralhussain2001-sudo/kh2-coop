#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 17 CANDIDATE v88 (build 16 + a second hero in
# the three one-hero small games: the glues 53 to 56 and the own-screen option --cannon1view)
# (patches/test-own-v88 / patches/test-v13-a, control patches/test-v13-a-nn), one run at a time, about two hours.
# Build 16 logs of the same steps are kept in local/reg-b16/. HIDDEN.
# Progress: local/reg-serial.log (an old one is moved to a name of its own first, never over a saved log).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log "local/reg-serial-old-$(date +%H%M%S).log"
echo "chain98 start $(date +%H:%M:%S)" >> local/sweep/b15/chain98.txt
bash tools/own/reg_serial.sh test-own-v88 test-v13-a b17
echo "chain98 through $(date +%H:%M:%S)" >> local/sweep/b15/chain98.txt
