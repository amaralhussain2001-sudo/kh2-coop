"""Lane G reference: ONE Sora, no twin (disc test-b-roam), same button timing as m_roam.py for pad 1.
Shows what a normal combo / jump / air combo / menu key looks like in the recorded fields.

  python -I tools/lane-g/m_ref.py <test-name> <patch-dir|-> [players]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from glib import run, NEWGAME, ISO_ROAM, S, PAD1_RAW, PAD2_RAW, LOG1, LOG2, SLOT1, SLOT_STEP  # noqa: E402

name, patch = sys.argv[1], sys.argv[2]
players = int(sys.argv[3]) if len(sys.argv) > 3 else 1


def combo(t, n=3, gap=24):
    return [f"{t + i * gap} 4 O" for i in range(n)]


p1 = (NEWGAME + combo(4700) + combo(5100) + combo(5300) + ["5500 4 X", "5620 4 X"] + ["5700 4 X"] + combo(5712, 3, 18)
      + ["5900 4 DOWN", "5930 4 UP", "6080 4 TRI", "6140 4 X", "6160 4 X", "6300 60 L1", "6460 4 START", "6490 4 START"])
ranges = {"pad1": (PAD1_RAW, 8), "pad2": (PAD2_RAW, 8), "log1": (LOG1, 0x60), "log2": (LOG2, 0x60), "S": (S, 0xB00), "S2": (0x000F1000, 0xB00),
          "slots": (SLOT1 - 1 * SLOT_STEP, 2 * SLOT_STEP)}
rec = run(name, ISO_ROAM, None if patch == "-" else patch, p1, [], frames=6560, speed=2, ranges=ranges, start_vc=4500,
          players=players, auto_objs=True, snaps=[4716, 4740, 4764, 5512, 5730, 5915, 6100, 6340, 6475])
print(name, "samples", len(rec.samples), "players found:", [hex(b) for b in getattr(rec, "players", [])],
      "in sync" if rec.in_sync else "NOT CONFIRMED IN SYNC")
print(rec.harness.strip().splitlines()[-1][:160])
