#!/bin/bash
# TEST ONLY: on run-v3b after the batch nt3: the Atlantica musical (LM01_MS201) three times with the same
# snapshot frames: nobody presses, player 1 taps Circle, player 2 taps Circle. Then the pictures are compared:
# "player 2 taps" must give the pictures of "player 1 taps" (twenty-eighth glue).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "sp batch done" local/sweep/nt3.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
python -I tools/own/make_jumpkit.py patches/test-own-v33-snapB patches/test-mus-run-v3b 0B 51 > /dev/null
SN="5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900"
G="$P/local/sweep/mus.log"
for t in "mus-none gum_new_p1 idle" "mus-p1 mash_new_p1 idle" "mus-p2 gum_new_p1 mash_only_p2"; do
  set -- $t
  out=$(PROBE="$P/tools/own/sp_probe.py" bash "$P/tools/own/dusk_one.sh" "$1" patches/test-mus-run-v3b test-s1-tt137.iso 9000 "$SN" "$O/$2.txt" "$O/$3.txt" run-v3b 30350 28062 2>&1 | head -n 1)
  echo "$1 | $out | TLB misses $(grep -c 'TLB Miss' "$P/local/run-v3b/p1/logs/emulog.txt")" >> "$G"
done
for f in $(echo $SN | tr ',' ' '); do
  n=$(printf "p1_f%06d.png" $f)
  a=$(sha1sum "local/tests/mus-none/$n" | cut -c1-12); b=$(sha1sum "local/tests/mus-p1/$n" | cut -c1-12); c=$(sha1sum "local/tests/mus-p2/$n" | cut -c1-12)
  echo "f$f none $a p1 $b p2 $c $([ "$b" = "$c" ] && echo 'p1=p2' || echo 'p1!=p2') $([ "$a" = "$b" ] && echo 'none=p1' || echo 'none!=p1')" >> "$G"
done
echo "mus done" >> "$G"
