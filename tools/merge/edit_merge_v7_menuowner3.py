r"""One-off (STATE part 141): the seventy-ninth glue's second form compared the message window's return address with 0x001BCBDC
(lui 0x001B); the call at 0x001ACBD4 returns to 0x001ACBDC (lui 0x001A). Found by run r11mo2dbg (tools/own/make_mo_dbg.py: the
other caller during the elf's talk was 0x001ACBDC, while V_MSGSTEP stayed 0).
  python -I tools/merge/edit_merge_v7_menuowner3.py          (run ONCE)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
OLD = "    lui t7,0x001B\n    ori t7,t7,0xCBDC              # a message window asks (the call at 0x001ACBD4): note the counter (a talk goes on)\n"
NEW = "    lui t7,0x001A\n    ori t7,t7,0xCBDC              # a message window asks (the call at 0x001ACBD4): note the counter (a talk goes on)\n"
if t.count(NEW) == 1:
    raise SystemExit("already done")
assert t.count(OLD) == 1
P.write_text(t.replace(OLD, NEW), encoding="utf-8")
print("merge_v7.py: po_pad's message-window address fixed")
