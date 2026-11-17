#!/bin/bash
# lane B75: ONE-COPY gauge test (single PC; optional test memory write of a maximum HP or an HP).
# usage: run_gauge.sh <test name> <disc name> <patch folder under patches/> <frames> [watcher options ...]
#   watcher options e.g.:  --setmax 244:3600:4   (ENTRY:MAXHP:SECONDS)   --set 244:2975:6   (ENTRY:HP:SECONDS)
# env: SNAP_FROM (default 4800), SNAP_STEP (default 200), SCRIPT (default b75_attack.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
N="$1"; DISC="$2"; PATCH="$3"; FR="$4"; shift 4
python -I "$P/tools/lane-b75/slots_watch.py" 28201 300 "$P/local/tests/$N-slots.tsv" --boost-heroes 9000 "$@" > "$P/local/tests/$N-watch.out" 2>&1 &
WP=$!
SNAPS=$(python -c "print(','.join(str(x) for x in range(${SNAP_FROM:-4800}, $FR, ${SNAP_STEP:-200})))")
python -I "$P/tools/kh2_session.py" run "$N" --iso "$P/local/iso/test-b75-$DISC.iso" --players 1 --frames "$FR" --speed 3 --snap "$SNAPS" --script "$P/tests/scripts/${SCRIPT:-b75_attack.txt}" --patch-dir "$P/patches/$PATCH" --fresh-card --port 30250 --pine 28201 --run-dir run-b75 --timeout 500 2>&1 | tail -1
kill $WP 2>/dev/null; wait $WP 2>/dev/null
echo "--- slots (last 4 lines)"; tail -4 "$P/local/tests/$N-slots.tsv"
echo "--- screenshots: $(ls "$P/local/tests/$N"/p1_f*.png | wc -l) taken; most repeated content:"; (cd "$P/local/tests/$N" && md5sum p1_f*.png | awk '{print $1}' | sort | uniq -c | sort -rn | head -1)
echo "--- emulator log, TLB misses: $(grep -c 'TLB Miss' "$P/local/run-b75/p1/logs/emulog.txt")"
