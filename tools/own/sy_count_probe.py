"""Read-only probe (ninth round, the user's items 1 and 2 of 2026-11-15 evening): SHAN-YU'S PUSH COUNT. Polled as fast as PINE
answers: the boss's work memory (object + 1156 = its script context, context + 52 = the work memory; the clash's numbers at
work + 148 (push count, a whole number), + 152 (push speed), + 156 (time limit), as read in B_MU100 and STATE part 63) and
both heroes' action words. A line whenever a word of the window work + SY_WIN0 (default 128, 16 words) or a hero's
action changes (the window as hex words; the first form read only work + 148 .. 156, which turned out to hold the clash's
current move, not the count).
  python -I tools/own/sy_count_probe.py <testDir> <pinePort> <frames (not used)> <out.txt>
FROM / TO (frames), SY_OBJ (hex; default 01B0D7B0 = Shan-Yu's object in the mu09 75 jump start, runs syC / syD)."""
import os
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "merge"))
from pine import Pine  # noqa: E402

out = sys.argv[4]
start, end = int(os.environ.get("FROM", "4600")), int(os.environ.get("TO", "11900"))
obj = int(os.environ.get("SY_OBJ", "01B0D7B0"), 16)
WIN0, WINN = int(os.environ.get("SY_WIN0", "128")), int(os.environ.get("SY_WINN", "16"))
p = Pine(int(sys.argv[2]), wait=120)
lines, last, t0 = [], None, time.time()


def ok(a):
    return 0x00100000 <= a < 0x02000000


def act(o):
    return "a%02X" % (p.r32(o + 0x154) & 0xFFFF) if ok(o) else "none"


try:
    while time.time() - t0 < 900:
        try:
            fr = p.r32(0x0034D4BC) + 152
        except RuntimeError:
            time.sleep(0.3)
            continue
        if fr < start:
            time.sleep(0.1)
            continue
        if fr > end:
            break
        ctx = p.r32(obj + 1156)
        work = p.r32(ctx + 52) if ok(ctx) else 0
        win = p.read(work + WIN0, 4 * WINN) if ok(work) else b""
        a1, a2 = act(p.r32(0x0034E948)), act(p.r32(0x000F05CC))
        key = (win, a1, a2)
        if key != last:
            words = struct.unpack("<%dI" % (len(win) // 4), win) if win else ()
            lines.append("f%d P1 %s | P2 %s | work+%d: %s" % (fr, a1, a2, WIN0, " ".join("%08X" % w for w in words)))
            last = key
            if len(lines) % 50 == 0:
                pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
except Exception as e:  # noqa: BLE001
    lines.append("ended: %r" % (e,))
pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
