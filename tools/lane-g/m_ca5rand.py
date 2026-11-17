"""Lane G: Port Royal fight disc (Sora + twin), random buttons on BOTH pads from frame 4690 to 7800
(stops before the heroes die: Continue after Game Over crashes on mission jump discs, a known test-disc artifact).

  python -I tools/lane-g/m_ca5rand.py <test-name> <patch-dir> [frames]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_CA5, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
frames = int(sys.argv[3]) if len(sys.argv) > 3 else 7800
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "now": (0x0032BAE0, 12), "cur": (0x003527E0, 4),
          "low": (0x000F0C00, 0x400), "low2": (0x000F1B00, 0x500),
          "slots": (SLOT1 - 7 * SLOT_STEP, 8 * SLOT_STEP)}
rec = run(name, ISO_CA5, patch, NEWGAME, [], frames=frames, speed=4, timeout=600, ranges=ranges, start_vc=4300,
          then="random", script_end=4690, follow={"obj1": ("S", 0x9E0), "twin": ("S2", 0x9E0)},
          snaps=[4680, 5200, 5800, 6400, 7000, 7600])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
