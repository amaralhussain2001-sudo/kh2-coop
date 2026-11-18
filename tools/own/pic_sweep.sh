#!/bin/bash
# TEST ONLY (part 142): DIFFERENT PICTURE QUALITY ON THE TWO PCs. Like sweep4.sh, but player 1's copy draws at UP1 (default 8) and
# player 2's at UP2 (default 3), both copies dump their EE main memory at DUMPS, and tools/own/ramdiff.py writes which address
# ranges differ (the dumps are deleted). One log line per list line: "<list line> | <session result> | f...: ... ; f...: ...".
#   env: DUMPS, FRAMES, P1S, P2S, ISO (default test-v5-tt137.iso), UP1, UP2, EXE (default builds/card1), SNAPS (default = DUMPS),
#        LOGDIR (default local/sweep/r12), TAG, KIT (the patch dir to make the jump kit from; default = arg 4)
# usage: bash tools/own/pic_sweep.sh <worker> <sandbox> <port> <patchDirName> <listFile>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
W=$1; RD=$2; PT=$3; OWN=$4; LIST=$5
D=${DUMPS:-2000,5200,8000,11000}; SN=${SNAPS:-$D}; TG=${TAG:-pic}; DISC=${ISO:-test-v5-tt137.iso}
EXE=${EXE:-$P/emulator-src/builds/card1/pcsx2-qtx64.exe}; VF=${VIEWF:-$P/patches/own-view/SLPM-66675_F266B00B.view}
LD="$P/${LOGDIR:-local/sweep/r12}"; mkdir -p "$LD"; LOG="$LD/$W.log"
cd "$P" || exit 1
while read -r room w prog name party pm pb pe ent; do
  [ -z "$room" ] && continue
  n="$TG-$name-$prog"
  grep -q "^$room $w $prog " "$LOG" 2>/dev/null && continue
  if [ "$w" = "--" ]; then KITDIR="$P/patches/$OWN"; else
    python -I tools/own/make_jumpkit2.py "patches/$OWN" "patches/test-pic-$W" "$w" "$((10#${room:2}))" "$pm" "$pb" "$pe" "${ent:-0}" > /dev/null
    KITDIR="$P/patches/test-pic-$W"; fi
  rm -rf "$P/local/tests/$n"
  python -I "$P/tools/lane-v3/v3_session.py" run "$n" --iso "$P/local/iso/$DISC" --players 2 --frames "${FRAMES:-11100}" --speed 4.0 \
    --snap "$SN" --script "${P1S:-$P/tests/scripts/own/mashrc_long_p1.txt}" --script2 "${P2S:-$P/tests/scripts/own/mashrc_long_p2.txt}" \
    --then idle --bot idle --patch-dir "$KITDIR" --fresh-card --exe1 "$EXE" --exe2 "$EXE" --view-file "$VF" --run-dir "$RD" --port "$PT" \
    --snapview1 1 --snapview2 1 --upscale1 "${UP1:-8}" --upscale2 "${UP2:-3}" --dump "${NODUMP:+}${NODUMP:-$D}" --extra1 "${EXTRA1:-}" --extra2 "${EXTRA2:-}" --timeout 1500 > "$P/local/tests/$n-harness.txt" 2>&1
  r=$(grep -E 'session closed|TIMED OUT' "$P/local/tests/$n-harness.txt" | head -1 | cut -c12-110)
  diff=$(python -I tools/own/ramdiff.py "$P/local/tests/$n" ${KEEP:+--keep} | tr '\n' ';' | sed 's/;/ ; /g')
  echo "$room $w $prog $name $party | $r | $diff" >> "$LOG"
done < "$LIST"
echo "pic worker $W done" >> "$LOG"
