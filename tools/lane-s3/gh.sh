#!/bin/bash
# Lane S3: run the function-dump script on this lane's copy of the analysis project (no re-analysis, read-only).
# usage: gh.sh <program: SLPM_666.75 | ovl_gumibattle.x | ovl_gumimenu.x> <outfile-relative-to-local/analysis/lane-s3> <S3Dump args...>
P="/c/Users/PC FORCE/Desktop/New folder (3)"; G="/c/Users/PC FORCE/Desktop/New folder/ghidra_12.1.4_PUBLIC"
PROG="$1"; shift
OUT="$P/local/analysis/lane-s3/$1"; shift
java -Djava.system.class.loader=ghidra.GhidraClassLoader -Dfile.encoding=UTF8 -Duser.country=US -Duser.language=en -Duser.variant= -Dsun.java2d.opengl=false -Dsun.java2d.d3d=false -Dlog4j.skipJansi=true -Xshare:off --enable-native-access=ALL-UNNAMED -Xmx6G -cp "$(cygpath -w "$G/Ghidra/Framework/Utility/lib/Utility.jar")" ghidra.Ghidra ghidra.app.util.headless.AnalyzeHeadless "$(cygpath -w "$P/local/ghidra-s3")" kh2a -process "$PROG" -noanalysis -readOnly -scriptPath "$(cygpath -w "$P/tools/lane-s3/ghidra")" -postScript S3Dump.java "$(cygpath -w "$OUT")" "$@" > "$P/local/analysis/lane-s3/gh-last.log" 2>&1
grep -a "S3Dump:\|LaneADump:" "$P/local/analysis/lane-s3/gh-last.log" | cut -c1-160
