"""TEST ONLY: <base patch> + "whom do the helpers heal" kit. Same lines on both PCs. Never part of the real patch.
  - Donald has "Donald Cure" (ability 0x00A8, switched on) in the last place of his ability list (save + 0x26F6;
    Donald's list starts at save + 0x2658 as Sora's at save + 0x2544).
  - At one video frame the HP of one or both heroes is set to a low value (a one-frame conditional line on the
    game's frame counter 0x0034D4BC = session frame - 152), after that the game is free to heal it.
  python -I tools/own/make_healkit.py <basePatchDir> <outDir> <p1|p2|both> <sessionFrame> [hp] [--p1slot=HEX] [--p2slot=HEX] [--nocure]
Unit slots on the quiet Borough disc (test-s1-hb9f): player 1's hero 0x01C6C4E8, the twin 0x01C6C750 (defaults).
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
SAVE = 0x0032BB30
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
base, out, who, frame = ROOT / args[0], ROOT / args[1], args[2], int(args[3])
hp = int(args[4]) if len(args) > 4 else 3
slot = {"p1": 0x01C6C4E8, "p2": 0x01C6C750}
for a in sys.argv[1:]:
    if a.startswith("--p1slot="):
        slot["p1"] = int(a[9:], 16)
    if a.startswith("--p2slot="):
        slot["p2"] = int(a[9:], 16)
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_healkit.py %s): for tests only." % " ".join(sys.argv[3:]))
if "--nocure" not in sys.argv:
    lines.append("patch=1,EE,%08X,short,80A8" % (SAVE + 0x26F6))
count = (frame - 152) & 0xFFFF
for w in (("p1", "p2") if who == "both" else (who,)):
    lines.append("patch=1,EE,E001%04X,extended,%08X" % (count, 0x0034D4BC))
    lines.append("patch=1,EE,%08X,extended,%08X" % (0x20000000 | slot[w], hp))
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, who, "HP", hp, "at frame", frame)
