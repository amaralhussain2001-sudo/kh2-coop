"""Lane G: Game Over and Continue with a twin and two control objects (free-roam disc with twin).

  python -I tools/lane-g/m_die.py <test-name> <patch-dir>
The patch folder must contain the TEST line that keeps the heroes' shared HP at 1 (tools/lane-g/make_die.py), so
the first hit in the Borough is lethal on both PCs alike (the session stays in sync).
Session frames: 4500 pad 2 walks the twin out of Merlin's house; 5400 both pads walk toward the Heartless;
from 7000 pad 1 presses Circle every 300 frames (Continue on the Game Over screen); from 9000 pad 2 too (attack).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, press, NEWGAME, ISO_ROAM3, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
p1 = NEWGAME + ["5400 50 LY=0"] + press("O", 7000, 13000, 300)
p2 = ["4500 30 LY=0", "4560 90 LX=0", "5400 50 LY=0"] + press("O", 9000, 13000, 300)
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "now": (0x0032BAE0, 12), "cur": (0x003527E0, 4),
          "low": (0x000F0C00, 0x400), "low2": (0x000F1B00, 0x500), "btl": (0x01C61958, 4),
          "slots": (SLOT1 - 7 * SLOT_STEP, 8 * SLOT_STEP)}
rec = run(name, ISO_ROAM3, patch, p1, p2, frames=13200, speed=4, timeout=600, ranges=ranges, start_vc=4300,
          follow={"obj1": ("S", 0x9E0), "twin": ("S2", 0x9E0)},
          snaps=[5300, 6000, 6500, 7000, 7250, 7500, 8000, 8500, 9000, 9500, 10000, 11000, 12000, 13000])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
