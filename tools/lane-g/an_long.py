"""Lane G: summary of a long recorded run (m_room.py with random buttons): rooms, attachments of both control
objects, HP, what each hero did, menu use of each control object, spare memory.

  python -I tools/lane-g/an_long.py <test-name> [from-frame]
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import load, SLOT_STEP  # noqa: E402

r = load(sys.argv[1])
f0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
ALL = r.samples
print(f"{sys.argv[1]}: {len(ALL)} samples, frames {ALL[0]['vc'] + 152}..{ALL[-1]['vc'] + 152};",
      "in sync" if r.in_sync else "SYNC NOT CONFIRMED")
for line in r.harness.splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print("   " + line[:150])
n = len(ALL[0]["slots"]) // SLOT_STEP
last = None
for s in ALL:
    now = struct.unpack_from("<H", s["now"], 0)[0]
    key = (now, struct.unpack_from("<I", s["S"], 0xAF4)[0] != 0, struct.unpack_from("<I", s["S2"], 0xAF4)[0] != 0,
           struct.unpack_from("<I", s["cur"], 0)[0], s.get("obj1@", 0), s.get("twin@", 0))
    if key != last:
        print(f"  frame {s['vc'] + 152:6d} room {key[0]:04X}  S attached {key[1]!s:5}  S2 attached {key[2]!s:5}  current-control {key[3]:08X}"
              f"  hero1 {key[4]:07X} hero2 {key[5]:07X}")
        last = key
S = [s for s in ALL if s["vc"] + 152 >= f0]
hp = [struct.unpack_from("<I", s["slots"], (n - 1) * SLOT_STEP)[0] for s in S]
print(f"from frame {f0}: heroes' HP min {min(hp)} max {max(hp)} last {hp[-1]}")
for who in ("obj1", "twin"):
    acts, xs = {}, []
    for s in S:
        if s.get(who + "@"):
            a = struct.unpack_from("<I", s[who], 0x154)[0]
            acts[a] = acts.get(a, 0) + 1
            xs.append(struct.unpack_from("<3f", s[who], 0x70))
    if not xs:
        print(f"  {who}: never present")
        continue
    atk = sum(v for k, v in acts.items() if 0x97 <= k <= 0x9F)
    print(f"  {who}: x {min(p[0] for p in xs):.0f}..{max(p[0] for p in xs):.0f}  z {min(p[2] for p in xs):.0f}..{max(p[2] for p in xs):.0f}"
          f"  samples in attack actions {atk}, jump/fall {acts.get(3, 0) + acts.get(4, 0)}, hit reactions {acts.get(6, 0) + acts.get(0xB, 0) + acts.get(0xD, 0)}"
          f"  action ids seen {sorted(acts)[:14]}")
en = {}
for s in S:
    for k in range(2, n + 1):
        en.setdefault(k, set()).add(struct.unpack_from("<I", s["slots"], (n - k) * SLOT_STEP)[0])
print("  enemy slots HP values seen:", {k: sorted(v)[:10] for k, v in en.items() if v != {0}})
for nm in ("S", "S2"):
    cur = sorted({struct.unpack_from("<I", s[nm], 0x90)[0] for s in S})
    depth = sorted({hex(struct.unpack_from("<I", s[nm], 0x8C0)[0]) for s in S})
    flags = sorted({hex(struct.unpack_from("<I", s[nm], 0x20)[0]) for s in S})
    lock = sorted({struct.unpack_from("<I", s[nm], 0xAC0)[0] for s in S})
    print(f"  {nm}: cursor values {cur[:10]}  menu pointer values {depth[:6]}  flag values {flags[:8]}  lock-on states {lock}")
nz = [s["vc"] for s in ALL if any(s["low"]) or any(s["low2"])]
print("  spare memory 0x000F0C00-0FFF / 0x000F1B00-1FFF:", "zero in every sample" if not nz else f"NOT zero at {nz[:3]}")
