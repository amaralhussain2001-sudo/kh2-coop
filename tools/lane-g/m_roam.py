"""Lane G measurement in a quiet room (Merlin's house, Sora + twin, no enemies): combos, jumps, menu keys.

  python -I tools/lane-g/m_roam.py <test-name> <patch-dir> [players]
Session frames:
  4700 P1 three Circle presses 24 frames apart (ground combo)     4900 P2 the same
  5100 both on the same frames                                    5300 interleaved (P2 12 frames later)
  5500 P1 Cross (jump)   5560 P2 Cross   5620 both
  5700 P1 Cross then Circle x3 in the air                         5800 P2 the same
  5900 P1 DOWN (menu cursor)  5930 P1 UP   5960 P2 DOWN   5990 P2 UP
  6020 P2 TRIANGLE   6080 P1 TRIANGLE (P1 stands on the save point: "Save" reaction)   then Cross to leave menus
  6200 P2 L1 held 60   6300 P1 L1 held 60   6400 P2 START  6430 P2 START  6460 P1 START  6490 P1 START
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_ROAM3, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
players = int(sys.argv[3]) if len(sys.argv) > 3 else 2
OBJ1, TWIN = 0x01A7C170, 0x01A96580      # player objects in Merlin's house on test-b-roam3 (test g-disc02)


def combo(t, n=3, gap=24):
    return [f"{t + i * gap} 4 O" for i in range(n)]


p1 = (NEWGAME + combo(4700) + combo(5100) + combo(5300) + ["5500 4 X", "5620 4 X"] + ["5700 4 X"] + combo(5712, 3, 18)
      + ["5900 4 DOWN", "5930 4 UP", "6080 4 TRI", "6140 4 X", "6160 4 X", "6300 60 L1", "6460 4 START", "6490 4 START"])
p2 = (combo(4900) + combo(5100) + combo(5312) + ["5560 4 X", "5620 4 X"] + ["5800 4 X"] + combo(5812, 3, 18)
      + ["5960 4 DOWN", "5990 4 UP", "6020 4 TRI", "6200 60 L1", "6400 4 START", "6430 4 START"])
ranges = {
    "pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
    "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "obj1": (OBJ1, 0xB80), "twin": (TWIN, 0xB80),
    "slots": (SLOT1 - 1 * SLOT_STEP, 2 * SLOT_STEP),
}
rec = run(name, ISO_ROAM3, patch, p1, p2, frames=6560, speed=2, ranges=ranges, start_vc=4400, players=players,
          snaps=[4690, 4716, 4740, 4764, 4916, 4940, 4964, 5116, 5140, 5164, 5340, 5512, 5572, 5632, 5730, 5830,
                 5915, 5975, 6040, 6100, 6240, 6340, 6415, 6475, 6540])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
print(rec.harness.strip().splitlines()[-1][:160])
