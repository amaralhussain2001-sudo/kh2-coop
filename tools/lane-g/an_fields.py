"""Lane G: in a recorded attack measurement, list the object / S fields that react to each controller's window.

  python -I tools/lane-g/an_fields.py <test-name> [block ...]      blocks default: obj1 twin S
Windows are session frames (see m_attack.py); the offset between session frames and the game's pad counter is
taken from the first frame where pad 2 holds Circle (session frame 4700).
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load, buttons  # noqa: E402

rec = load(sys.argv[1])
blocks = sys.argv[2:] or ["obj1", "twin", "S"]
S = rec.samples
first = next(s["vc"] for s in S if "O" in buttons(s["pad2"]).split("+"))
C = 4700 - first
print(f"samples {len(S)}, session frame = pad counter + {C}")


def win(a, b):
    return [s for s in S if a <= s["vc"] + C < b]


W = {"idle": win(4450, 4695), "p2": win(4700, 5060), "p1": win(5100, 5460)}
print({k: len(v) for k, v in W.items()})
for blk in blocks:
    n = len(S[0][blk])
    print(f"== {blk}: fields (4 bytes) steady while idle that take new values in a window")
    for off in range(0, n - 3, 4):
        vals = {k: [struct.unpack_from("<I", s[blk], off)[0] for s in v] for k, v in W.items()}
        idle = set(vals["idle"])
        if len(idle) > 2:
            continue
        new2, new1 = set(vals["p2"]) - idle, set(vals["p1"]) - idle
        if not new2 and not new1:
            continue
        if len(new2) > 24 or len(new1) > 24:
            continue

        def fmt(st):
            return "{" + ",".join(f"{v:X}" for v in sorted(st)[:8]) + ("..." if len(st) > 8 else "") + "}"
        print(f"  +0x{off:03X}: idle {fmt(idle)}  pad2-window new {fmt(new2)}  pad1-window new {fmt(new1)}")
