#!/bin/bash
# THE WHOLE REGRESSION of the final candidate of the eighth round, one run at a time (tools/own/reg_serial.sh):
#   own screens patches/test-own-v52, shared screen patches/test-v8-t (control patches/test-v8-t-nn), prefix b13.
# About two and a half hours. Progress: local/reg-serial.log and local/sweep/b15/chain99.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
echo "chain99 (regression of test-own-v52 / test-v8-t) start $(date +%H:%M:%S)" >> "$B/chain99.txt"
bash tools/own/reg_serial.sh test-own-v52 test-v8-t b13
echo "chain99 through $(date +%H:%M:%S)" >> "$B/chain99.txt"
