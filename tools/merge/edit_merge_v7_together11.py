"""One-off: the EXPERIMENT --together of tools/merge/merge_v7.py (fiftieth glue), ELEVENTH form: THE RIGHT WORK
MEMORY POINTER.
A fault of my reading in the ninth and tenth form: I took the word at script context + 52 for the work memory.
READ now, in the context's set-up routine (0x0016C97C .. 0x0016C9B4): + 52 is only the HANDLE of the work memory
(made by 0x0016D1A0(work size) when it is 0); 0x0016D1D8(handle) gives the memory itself, and THAT pointer is kept
at context + 16. So the ninth form put back the handle's own head too (hence its 50 fault lines) and hit the
numbers only because its 4,432 bytes overlapped them; the tenth form (three words from + 52) missed them: runs
tg30 .. tg34 (candidate v73) had no fault line but the clash's short timing of v70 again (306 frames) and the
gate fell again.
Now th_tick takes the work memory from context + 16.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_together11.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
old = "    lw t4,52(a0)                  # the work memory (the boss's own: the hooked script shares it)"
new = "    lw t4,16(a0)                  # the work memory (the boss's own: the hooked script shares it; + 52 is only its handle)"
if new in s:
    raise SystemExit("already there")
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
