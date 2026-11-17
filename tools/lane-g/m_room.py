"""Lane G: room change with a twin (free-roam disc with twin), then actions in the next room.

  python -I tools/lane-g/m_room.py <test-name> <patch-dir> [frames]
Session frames:  4500 pad 2 walks the twin up and then left through the west door of Merlin's house (the room
change is triggered by the twin on this disc);  in the Borough: 5400 pad 1 stick right 40 frames; 5500 pad 2 stick
left 40 frames; 5600 pad 1 Cross (jump); 5660 pad 2 Cross; 5720 pad 1 Circle x3; 5820 pad 2 Circle x3;
5920 pad 2 DOWN; 5950 pad 1 DOWN; then idle (or random buttons when frames > 6400).
Records S, S2, both pads and - through S->player / S2->player - both heroes in every room.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_ROAM3, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
frames = int(sys.argv[3]) if len(sys.argv) > 3 else 6400


def combo(t, n=3, gap=24):
    return [f"{t + i * gap} 4 O" for i in range(n)]


p1 = NEWGAME + ["5400 40 LX=255", "5600 4 X"] + combo(5720) + ["5950 4 DOWN"]
p2 = ["4500 30 LY=0", "4560 90 LX=0", "5500 40 LX=0", "5660 4 X"] + combo(5820) + ["5920 4 DOWN"]
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "now": (0x0032BAE0, 12), "cur": (0x003527E0, 4),
          "low": (0x000F0C00, 0x400), "low2": (0x000F1B00, 0x500),
          "slots": (SLOT1 - 7 * SLOT_STEP, 8 * SLOT_STEP)}
rec = run(name, ISO_ROAM3, patch, p1, p2, frames=frames, speed=(4 if frames > 6400 else 2), timeout=900, ranges=ranges, start_vc=4300,
          then="random" if frames > 6400 else "idle", bot="none", script_end=(6400 if frames > 6400 else None),
          follow={"obj1": ("S", 0x9E0), "twin": ("S2", 0x9E0)},
          snaps=[4480, 4700, 4900, 5100, 5300, 5460, 5560, 5615, 5675, 5760, 5860, 5935, 5965, 6300] + list(range(7000, frames, 3000)))
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
