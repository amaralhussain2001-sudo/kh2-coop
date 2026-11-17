"""Lane G, TEST ONLY: a patch folder = <base patch> + lines that give the fresh save some skills, so guard, dodge,
magic and the shortcut buttons can be tested with a level-1 Sora. Never part of the real game patch.

  python -I tools/lane-g/make_kit.py <basePatchDir|-> <outDir>
Adds (every frame, identical on both PCs, so sessions stay in sync):
  ability slots 0..4 of Sora's save (0x0032BB30 + 0x2544): Guard, Dodge Roll, Aerial Dodge, High Jump, Glide (equipped)
  magic: Fire, Blizzard, Thunder, Cure level 1 (save + 0x3594..0x3597, HYPOTHESIS until the menu shows them)
  shortcuts (save + 0x36F8, four 16-bit command numbers): Fire, Blizzard, Thunder, Cure
"""
import pathlib
import sys

SAVE = 0x0032BB30
base, out = sys.argv[1], pathlib.Path(sys.argv[2])
lines = []
if base != "-":
    lines = [l for l in (pathlib.Path(base) / "SLPM-66675_F266B00B.pnach").read_text().splitlines() if l.strip()]
else:
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)"]
lines.append("comment=LANE G TEST KIT (skills for tests only): abilities, magic, shortcuts written into the save.")
abilities = [0x0052, 0x0234, 0x0066, 0x005E, 0x006A]       # Guard, Dodge Roll, Aerial Dodge, High Jump, Glide
for i, a in enumerate(abilities):
    lines.append(f"patch=1,EE,{SAVE + 0x2544 + 2 * i:08X},short,{a | 0x8000:04X}")
for i in range(4):
    lines.append(f"patch=1,EE,{SAVE + 0x3594 + i:08X},byte,01")
for i, cmd in enumerate([0x0031, 0x0033, 0x0032, 0x0034]):
    lines.append(f"patch=1,EE,{SAVE + 0x36F8 + 2 * i:08X},short,{cmd:04X}")
out.mkdir(parents=True, exist_ok=True)
(out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
print(out, len(lines), "lines")
