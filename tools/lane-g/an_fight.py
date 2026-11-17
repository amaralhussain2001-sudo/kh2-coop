"""Lane G: summary of a recorded fight measurement (m_attack.py): per window, how many frames each hero spent in
an attack action, how many attack presses each controller made, and how much HP the enemies lost.

  python -I tools/lane-g/an_fight.py <test-name> [--c N] [--windows a-b,c-d,...]
Attack action = object+0x154 in 0x97..0x9F (ground and air attack actions seen in the measurements).
Enemy HP = unit slots 2..8 (slot 1 is the heroes' shared HP).
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load, buttons, SLOT_STEP  # noqa: E402

C = None
if "--c" in sys.argv:
    i = sys.argv.index("--c")
    C = int(sys.argv[i + 1])
    del sys.argv[i:i + 2]
wins = [(4700, 5060, "pad 2 attacks"), (5100, 5460, "pad 1 attacks"), (5500, 5840, "both attack")]
if "--windows" in sys.argv:
    i = sys.argv.index("--windows")
    wins = [(int(a), int(b), f"{a}-{b}") for a, b in (w.split("-") for w in sys.argv[i + 1].split(","))]
    del sys.argv[i:i + 2]
rec = load(sys.argv[1])
S = rec.samples
if C is None:
    first = next((s["vc"] for s in S if "O" in buttons(s["pad2"]).split("+")), None)
    C = 4700 - first if first else 152
nslots = len(S[0]["slots"]) // SLOT_STEP


def hp(s, k):          # k = 1..nslots ; slot 1 is the LAST record in the block (slots go downwards in memory)
    off = (nslots - k) * SLOT_STEP
    return struct.unpack_from("<I", s["slots"], off)[0]


def attacking(b):
    return 0x97 <= struct.unpack_from("<I", b, 0x154)[0] <= 0x9F


print(f"{sys.argv[1]}: session frame = pad counter + {C}; {'in sync' if rec.in_sync else 'sync not confirmed'}")
for a, b, label in wins:
    W = [s for s in S if a <= s["vc"] + C < b]
    if not W:
        continue
    presses = {"pad1": 0, "pad2": 0}
    for pad in presses:
        prev = False
        for s in W:
            cur = "O" in buttons(s[pad]).split("+")
            presses[pad] += cur and not prev
            prev = cur
    f1 = sum(attacking(s["obj1"]) for s in W)
    f2 = sum(attacking(s["twin"]) for s in W)
    e0 = [hp(W[0], k) for k in range(2, nslots + 1)]
    e1 = [hp(W[-1], k) for k in range(2, nslots + 1)]
    h0, h1 = hp(W[0], 1), hp(W[-1], 1)
    print(f"  {label:16s} presses P1 {presses['pad1']:2d} P2 {presses['pad2']:2d} | frames attacking: hero1 {f1:3d}/{len(W)} hero2 {f2:3d}/{len(W)}"
          f" | enemy HP {e0} -> {e1} | heroes' HP {h0} -> {h1}")
