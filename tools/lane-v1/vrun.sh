#!/bin/bash
# Lane V1: one test run with the two-view probe attached through PINE.
# usage: vrun.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <players> <p1script> <p2script|-> <then> <patchDir|-> [extra harness options...]
#   then = what both pads do after their script ends: idle | random
#   env: VFULL=1 (per-frame camera/position file), VCAVE=1 (watch the lane's memory range), VEE=n (emulated CPU step),
#        VDUMP=f1,f2 (raw camera / view memory at these frames)
#        VMEM="<frame> <addr:len> ..." (memdump.py first -> memdump.txt, then the probe)
# Results: local/tests/<name>/ (screenshots, logs, vprobe.txt, harness.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; snaps=$5; players=$6; s1=$7; s2=$8; then=$9; pdir=${10}
shift 10 2>/dev/null
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --snap "$snaps" --then "$then" --bot "$then" --fresh-card --pine 28171 --run-dir run-v1 --port 29950
      --timeout 1500 --tail 4)
[ "$s1" != "-" ] && args+=(--script "$s1")
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ "$pdir" != "-" ] && args+=(--patch-dir "$pdir")
[ -n "$VEE" ] && args+=(--ee-rate "$VEE")
args+=("$@")
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
popts=()
[ -n "$VFULL" ] && popts+=(--full)
[ -n "$VCAVE" ] && popts+=(--cave)
[ -n "$VDUMP" ] && popts+=(--dump "$VDUMP")
[ -n "$VMEM" ] && python -I "$P/tools/lane-v1/memdump.py" 28171 ${VMEM%% *} "$T/memdump.txt" ${VMEM#* } > "$T/memdump-console.txt" 2>&1
python -I "$P/tools/lane-v1/vprobe.py" 28171 $((frames - 30)) "$T/vprobe.txt" "${popts[@]}" > "$T/vprobe-console.txt" 2>&1
for i in $(seq 1 900); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -4
tail -1 "$T/vprobe-console.txt"
