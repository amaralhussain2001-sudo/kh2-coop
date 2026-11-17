#!/bin/bash
# Lane E: run a Ghidra headless post-script on lane E's COPY of the analysed project (no re-analysis, read-only).
# usage: gh.sh <outfile-relative-to-local/analysis/e> <LaneEDump args...>
P="/c/Users/PC FORCE/Desktop/New folder (3)"; G="/c/Users/PC FORCE/Desktop/New folder/ghidra_12.1.4_PUBLIC"
OUT="$P/local/analysis/e/$1"; shift
java -Djava.system.class.loader=ghidra.GhidraClassLoader -Dfile.encoding=UTF8 -Duser.country=US -Duser.language=en -Duser.variant= -Dsun.java2d.opengl=false -Dsun.java2d.d3d=false -Dlog4j.skipJansi=true -Xshare:off --enable-native-access=ALL-UNNAMED -Xmx6G -cp "$(cygpath -w "$G/Ghidra/Framework/Utility/lib/Utility.jar")" ghidra.Ghidra ghidra.app.util.headless.AnalyzeHeadless "$(cygpath -w "$P/local/ghidra-e")" kh2a -process SLPM_666.75 -noanalysis -readOnly -scriptPath "$(cygpath -w "$P/tools/lane-e/ghidra")" -postScript LaneEDump.java "$(cygpath -w "$OUT")" "$@" > "$P/local/analysis/e/gh-last.log" 2>&1
grep -a "LaneEDump:" "$P/local/analysis/e/gh-last.log" | cut -c1-160
