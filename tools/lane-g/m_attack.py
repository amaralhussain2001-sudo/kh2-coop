"""Lane G measurement: who swings when each controller presses Circle (attack)?

  python -I tools/lane-g/m_attack.py <test-name> <patch-dir> [disc]
Windows (session frames):  4700-5000 pad 2 presses Circle every 30;  5100-5400 pad 1 does;  5500-5800 both
(pad 2 shifted by 15);  5850 pad 2 Cross (jump);  5910 pad 1 Cross;  5970 pad 2 Square;  6030 pad 1 Square;
6090 pad 2 R1 (lock-on);  6150 pad 1 R1;  6210 pad 2 Triangle;  6270 pad 1 Triangle.
Records both player objects, the shared control object S, both pads and the unit slots once per video frame.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, press, NEWGAME, ISO_CA5, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
iso = sys.argv[3] if len(sys.argv) > 3 else ISO_CA5
OBJ1, TWIN = 0x01AA3FB0, 0x01ABE3C0      # player objects in the ca5 scene (test g-disc01)

p1 = NEWGAME + press("O", 5100, 5400, 30) + press("O", 5500, 5800, 30) + ["5910 4 X", "6030 4 SQ", "6150 4 R1", "6270 4 TRI"]
p2 = press("O", 4700, 5000, 30) + press("O", 5515, 5800, 30) + ["5850 4 X", "5970 4 SQ", "6090 4 R1", "6210 4 TRI"]
ranges = {
    "pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
    "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "obj1": (OBJ1, 0xB80), "twin": (TWIN, 0xB80),
    "slots": (SLOT1 - 7 * SLOT_STEP, 8 * SLOT_STEP),
}
rec = run(name, iso, patch, p1, p2, frames=6400, speed=2, ranges=ranges, start_vc=4300,
          snaps=[4690, 4760, 4850, 5160, 5250, 5560, 5650, 5862, 5922, 5985, 6045, 6110, 6170, 6230, 6290])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
print(rec.harness.strip().splitlines()[-1][:160])
