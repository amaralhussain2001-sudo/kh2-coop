"""Lane G: Hollow Bastion fight with Donald, Goofy AND a twin (disc local/iso/test-g-friends.iso).
Checks that the helpers and two control objects live together, and what happens when the mission's cutscene starts.

  python -I tools/lane-g/m_friends.py <test-name> <patch-dir> [frames]
Session frames: 4700-5000 pad 1 Circle every 30; 5100-5400 pad 2 Circle every 30; then random buttons on both pads.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, press, NEWGAME, ROOT, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
frames = int(sys.argv[3]) if len(sys.argv) > 3 else 12000
iso = str(ROOT / "local" / "iso" / "test-g-friends.iso")
p1 = NEWGAME + press("O", 4700, 5000, 30)
p2 = press("O", 5100, 5400, 30)
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "now": (0x0032BAE0, 12), "cur": (0x003527E0, 4),
          "low": (0x000F0C00, 0x400), "low2": (0x000F1B00, 0x500),
          "slots": (SLOT1 - 7 * SLOT_STEP, 8 * SLOT_STEP)}
rec = run(name, iso, patch, p1, p2, frames=frames, speed=4, timeout=700, ranges=ranges, start_vc=4200,
          then="random", script_end=5500, follow={"obj1": ("S", 0x9E0), "twin": ("S2", 0x9E0)},
          snaps=[4690, 4800, 5000, 5200, 5400] + list(range(6000, frames, 1000)))
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
