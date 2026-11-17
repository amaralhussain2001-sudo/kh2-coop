"""One-off (ninth round): THE CAPTURE RECORDER'S RING IS 8 ENTRIES, NOT 16.
Found with tools/own/hold_state_probe.py (run fzB): the ring of tools/own/make_rec_cap3.py (16 x 32 bytes from
0x000F1D10) reached into the recorder's own routine at 0x000F1F00: the sixteenth capture of a run wrote over its
first four instructions, and a second capture in the same frame (before the patch lines were written again)
ran them: the game's main loop hung (the picture stood from frame 16646 in the armoured Xemnas run of
r9_chain17.sh). A fault of the TEST RECORDER, not of a build.
This edit: the recorder's ring index is "and 7" (8 entries, 0x000F1D10 .. 0x000F1E0F), and the probes that read
the ring (cap_log_probe.py, cap_log_probe2.py, freeze_probe.py, hold_state_probe.py) read 8 entries.
Kits made before this edit (patches\\*-cap) must be made again. Run once:
  python -I tools/own/edit_cap_ring8.py"""
import pathlib

here = pathlib.Path(__file__).resolve().parent
NL = chr(10)


def edit(name, pairs):
    p = here / name
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new, count in pairs:
        assert s.count(old) == count, (name, old, s.count(old))
        s = s.replace(old, new)
    p.write_bytes(s.replace("\n", "\r\n").encode("utf-8") if crlf else s.encode("utf-8"))


edit("make_rec_cap3.py", [
    ("    andi t6,t6,15" + NL, "    andi t6,t6,7                  # a ring of 8 (16 would reach into this routine: edit_cap_ring8.py)" + NL, 1),
    ("works together with the fiftieth glue) and notes each call in a ring of 16:", "works together with the fiftieth glue) and notes each call in a ring of 8:", 1),
    ("  0x000F1D10  16 x 32 bytes:", "  0x000F1D10  8 x 32 bytes:", 1),
])
for name in ("cap_log_probe.py", "cap_log_probe2.py"):
    edit(name, [
        ("            ring = p.read(0x000F1D10, 16 * 32)" + NL, "            ring = p.read(0x000F1D10, 8 * 32)" + NL, 1),
        ("            for k in range(max(seen, n - 16), n):" + NL, "            for k in range(max(seen, n - 8), n):" + NL, 1),
        ("struct.unpack_from(\"<8I\", ring, (k & 15) * 32)", "struct.unpack_from(\"<8I\", ring, (k & 7) * 32)", 1),
    ])
for name in ("freeze_probe.py", "hold_state_probe.py"):
    edit(name, [
        ("ring = p.read(0x000F1D10, 16 * 32)", "ring = p.read(0x000F1D10, 8 * 32)", 1),
        ("ring, (k & 15) * 32)", "ring, (k & 7) * 32)", 1),
    ])
print("ok")
