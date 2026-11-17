#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 17 CANDIDATE v89 (v88 + the fifty-seventh glue --hudowner; v88 = build 16 + a second hero in
# the three one-hero small games: the glues 53 to 56 and the own-screen option --cannon1view)
# (patches/test-own-v89 / patches/test-v14-a, control patches/test-v14-a-nn), one run at a time, about two hours.
# The logs of v88 for the same steps are kept in local/reg-b17/. HIDDEN.
# Progress: local/reg-serial.log (an old one is moved to a name of its own first, never over a saved log).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log "local/reg-serial-old-$(date +%H%M%S).log"
echo "chain108 start $(date +%H:%M:%S)" >> local/sweep/b15/chain108.txt
bash tools/own/reg_serial.sh test-own-v89 test-v14-a b18
echo "chain108 through $(date +%H:%M:%S)" >> local/sweep/b15/chain108.txt
