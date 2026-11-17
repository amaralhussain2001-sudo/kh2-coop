"""Lane G: Reaction Command for player 2. In Merlin's house hero 1 stands on the save point ("Save" reaction).
Player 2 walks hero 2 onto the save point and presses Triangle.

  python -I tools/lane-g/m_react.py <test-name> <patch-dir> <frames-of-right-stick> [p2|p1|none]
Session frames: 4700 pad 2 stick right for N frames; 4900 Triangle from the chosen pad (default pad 2);
5100 pad 1 Cross, 5160 pad 1 Cross (leave the menu if it opened).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_ROAM3, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
who = sys.argv[4] if len(sys.argv) > 4 else "p2"
OBJ1, TWIN = 0x01A7C170, 0x01A96580
p1 = NEWGAME + (["4900 4 TRI"] if who == "p1" else []) + ["5100 4 X", "5160 4 X"]
p2 = [f"4700 {n} LX=255"] + (["4900 4 TRI"] if who == "p2" else [])
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "obj1": (OBJ1, 0xB80), "twin": (TWIN, 0xB80),
          "now": (0x0032BAE0, 12), "slots": (SLOT1 - 1 * SLOT_STEP, 2 * SLOT_STEP)}
rec = run(name, ISO_ROAM3, patch, p1, p2, frames=5260, speed=2, ranges=ranges, start_vc=4400,
          snaps=[4690, 4890, 4915, 4935, 4960, 5000, 5060, 5130, 5200, 5250])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
