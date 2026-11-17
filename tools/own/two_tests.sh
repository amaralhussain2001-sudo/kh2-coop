#!/bin/bash
# TEST ONLY: two own-screen runs side by side (sandboxes run-v3 and run-v3b), each line of arguments as for
# dusk_one.sh without the sandbox part. usage: two_tests.sh "<args of run A>" "<args of run B>"
P="/c/Users/PC FORCE/Desktop/New folder (3)"
eval "bash \"$P/tools/own/dusk_one.sh\" $1 run-v3 30150 28061" &
eval "bash \"$P/tools/own/dusk_one.sh\" $2 run-v3b 30350 28062" &
wait
