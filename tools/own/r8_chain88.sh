#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 16 CANDIDATE v81 (build 15 + the glues 50, 51,
# 52: both heroes in Shan-Yu's clash, player 2's Gummi ship can be hit, a carpet under player 2's hero)
# (patches/test-own-v81 / patches/test-v12-a, control patches/test-v12-a-nn), one run at a time, about two hours.
# Build 15 logs of the same steps are kept in local/reg-b15/. HIDDEN.
# Progress: local/reg-serial.log (an old one is moved to a name of its own first, never over a saved log).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
[ -f local/reg-serial.log ] && mv local/reg-serial.log "local/reg-serial-old-$(date +%H%M%S).log"
echo "chain88 start $(date +%H:%M:%S)" >> local/sweep/b15/chain88.txt
bash tools/own/reg_serial.sh test-own-v81 test-v12-a b16
echo "chain88 through $(date +%H:%M:%S)" >> local/sweep/b15/chain88.txt
