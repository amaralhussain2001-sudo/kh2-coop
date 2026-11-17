"""Lane G: guard / dodge / magic by shortcut / Reaction Command for each hero, in the quiet room
(free-roam disc with twin, test-kit patch that grants the skills).

  python -I tools/lane-g/m_kit.py <test-name> <patch-dir>
Session frames:
  4700 P1 Square (guard)            4780 P2 Square
  4860 P1 stick right + Square (dodge roll)    4960 P2 stick left + Square
  5060 P1 holds L1 and presses Circle (shortcut 1)     5200 P2 the same
  5340 P1 L1 + Triangle             5480 P2 L1 + Triangle
  5620 P1 L1 + Square               5760 P2 L1 + Square
  5900 P1 Cross, Cross again in the air (aerial dodge / high jump)   6000 P2 the same
  6100 P1 opens Magic in the menu (DOWN, Circle) and leaves (Cross);  6260 P2 the same blind
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_ROAM3, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
OBJ1, TWIN = 0x01A7C170, 0x01A96580


def l1(t, button):
    # script lines must not overlap: the harness uses the first line that covers a frame
    return [f"{t} 14 L1", f"{t + 14} 4 L1 {button}", f"{t + 18} 32 L1"]


p1 = (NEWGAME + ["4700 4 SQ", "4860 10 LX=255", "4870 4 LX=255 SQ", "4874 10 LX=255"] + l1(5060, "O") + l1(5340, "TRI") + l1(5620, "SQ")
      + ["5900 4 X", "5914 4 X", "6100 4 DOWN", "6130 4 O", "6180 4 X", "6210 4 X"])
p2 = (["4780 4 SQ", "4960 10 LX=0", "4970 4 LX=0 SQ", "4974 10 LX=0"] + l1(5200, "O") + l1(5480, "TRI") + l1(5760, "SQ")
      + ["6000 4 X", "6014 4 X", "6260 4 DOWN", "6290 4 O", "6340 4 X", "6370 4 X"])
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60),
          "S": (S, 0xB00), "S2": (0x000F1000, 0xB00), "obj1": (OBJ1, 0xB80), "twin": (TWIN, 0xB80),
          "slots": (SLOT1 - 1 * SLOT_STEP, 2 * SLOT_STEP), "save_ab": (0x0032BB30 + 0x2544, 16), "save_mg": (0x0032BB30 + 0x3594, 4),
          "save_sc": (0x0032BB30 + 0x36F8, 8)}
rec = run(name, ISO_ROAM3, patch, p1, p2, frames=6460, speed=2, ranges=ranges, start_vc=4400,
          snaps=[4712, 4792, 4884, 4984, 5086, 5100, 5226, 5240, 5366, 5380, 5506, 5520, 5646, 5786, 5922, 6022, 6120, 6150, 6280, 6310])
print(name, "samples", len(rec.samples), "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
for line in rec.harness.strip().splitlines():
    if "session closed" in line or "OUT OF SYNC" in line or "TIMED OUT" in line:
        print(line[:170])
