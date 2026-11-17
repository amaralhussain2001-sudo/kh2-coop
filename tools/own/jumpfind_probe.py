"""Read-only probe: where in memory is the "jump" record of a test disc's start room (tt01 event program:
01 00 00 00 | 02 00 | world | area | entrance | localset | fade 02 40)? Polls from session frame 3000 on and
writes every address where the record of the given world / localset is found, with the frame.
  JUMP="02:89" python -I tools/own/jumpfind_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
world, ls = (int(x, 16) for x in os.environ.get("JUMP", "02:89").split(":"))
pat = bytes([1, 0, 0, 0, 2, 0, world, 0, 0, 0, 0, 0, ls, 0, 2, 0x40])
p = Pine(int(sys.argv[2]), wait=120)
lines, seen, t0 = [], set(), time.time()
try:
    while time.time() - t0 < 600:
        try:
            fr = p.r32(0x0034D4BC) + 152
        except RuntimeError:
            time.sleep(0.3)
            continue
        if fr < 3000:
            time.sleep(0.2)
            continue
        ram = p.read(0x00400000, 0x01C00000)
        i = ram.find(pat)
        while i >= 0:
            a = 0x00400000 + i
            if a not in seen:
                seen.add(a)
                lines.append("frame %d: record at %08X (world word %08X, localset word %08X)" % (fr, a, a + 6, a + 12))
            i = ram.find(pat, i + 1)
        if fr > 4600:
            break
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
