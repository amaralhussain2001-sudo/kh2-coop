#!/bin/bash
# TEST ONLY (eighth round, job 12): THE WHOLE REGRESSION OF THE BUILD 14 CANDIDATE v58 ONCE MORE FROM STEP 1, HIDDEN.
# r8_chain52.sh was stopped at 06:57 in its step 1 (the user: "make all the tests in the background i'm going to
# play now"; that queue ran with the windows shown). This chain does not move the progress log.
# (patches/test-own-v58 / patches/test-v8-z, control patches/test-v8-z-nn; build 13's logs: local/reg-b13/)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
echo "chain56 start $(date +%H:%M:%S)" >> local/sweep/b15/chain56.txt
bash tools/own/reg_serial.sh test-own-v58 test-v8-z b14 1
echo "chain56 through $(date +%H:%M:%S)" >> local/sweep/b15/chain56.txt
