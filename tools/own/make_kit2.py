"""TEST ONLY: a patch folder = <base patch> + test lines written into memory every frame (same on both PCs).
Never part of the real game patch.

  python -I tools/own/make_kit2.py <basePatchDir> <outDir> [--magic] [--forms=HEX] [--limit] [--drive=BARS] [--drivemax=BARS] [--die=p1|p2|both] [--formkeys] [--limits] [--byte=OFF:HH] [--short=OFF:HHHH]

  --magic       lane G's kit: Guard, Dodge Roll, Aerial Dodge, High Jump, Glide; Fire, Blizzard, Thunder, Cure; shortcuts
  --forms=HEX   the save's Drive Form byte (save + 0x36C0): 02 Valor, 04 Wisdom, 08 Limit, 10 Final, 40 Master
  --drive=BARS  the save's copy of the Drive values (save + 0x3528 gauge, +0x3529 bars, +0x352A most bars)
  --die=...     HP word of the hero's slot (p1 = 0x01C6C750, p2 = the twin's 0x01C6C4E8) held at 1
"""
import pathlib
import sys

NAME = "SLPM-66675_F266B00B.pnach"
SAVE = 0x0032BB30
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
base, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
opts = sys.argv[3:]
lines = [l for l in (base / NAME).read_text(encoding="utf-8").splitlines() if l.strip()]
lines.append("comment=TEST KIT (tools/own/make_kit2.py %s): for tests only." % " ".join(opts))
for o in opts:
    if o == "--magic":
        for i, a in enumerate([0x0052, 0x0234, 0x0066, 0x005E, 0x006A]):
            lines.append("patch=1,EE,%08X,short,%04X" % (SAVE + 0x2544 + 2 * i, a | 0x8000))
        for i in range(4):
            lines.append("patch=1,EE,%08X,byte,01" % (SAVE + 0x3594 + i))
        for i, cmd in enumerate([0x0031, 0x0033, 0x0032, 0x0034]):
            lines.append("patch=1,EE,%08X,short,%04X" % (SAVE + 0x36F8 + 2 * i, cmd))
    elif o.startswith("--forms="):
        lines.append("patch=1,EE,%08X,byte,%02X" % (SAVE + 0x36C0, int(o[8:], 16)))
    elif o == "--limit":          # Limit Form's flag (HYPOTHESIS from memory of the randomizer notes: save + 0x36CA, bit 3)
        lines.append("patch=1,EE,%08X,byte,08" % (SAVE + 0x36CA))
    elif o.startswith("--drive="):
        n = int(o[8:])
        lines.append("patch=1,EE,%08X,byte,00" % (SAVE + 0x3528))
        lines.append("patch=1,EE,%08X,byte,%02X" % (SAVE + 0x3529, n))
        lines.append("patch=1,EE,%08X,byte,%02X" % (SAVE + 0x352A, n))
    elif o.startswith("--drivemax="):     # only the most bars (the gauge then fills at a save point or by hits)
        lines.append("patch=1,EE,%08X,byte,%02X" % (SAVE + 0x352A, int(o[11:])))
    elif o == "--formkeys":       # a Keyblade (Kingdom Key, item 0x0029) in the weapon places of Valor / Master / Final Form
        for off in (0x32F4, 0x339C, 0x33D4):     # (HYPOTHESIS from memory of the randomizer notes; a fresh save has 0 there)
            lines.append("patch=1,EE,%08X,short,0029" % (SAVE + off))
    elif o.startswith("--byte=") or o.startswith("--short="):     # any save byte / short: --byte=36C4:39 (hex, save-relative)
        kind = o[2:o.index("=")]
        off, val = o[o.index("=") + 1:].split(":")
        lines.append("patch=1,EE,%08X,%s,%s" % (SAVE + int(off, 16), kind, val.upper().zfill(2 if kind == "byte" else 4)))
    elif o == "--limits":         # Limit abilities switched on: Donald 0x00C7, Goofy 0x00C9, Sora's Trinity 0x00C6 (round 4, part 7)
        for off, val in ((0x26F4, 0x80C7), (0x280A, 0x80C9), (0x25D8, 0x80C6)):
            lines.append("patch=1,EE,%08X,short,%04X" % (SAVE + off, val))
    elif o.startswith("--die="):
        who = o[6:]
        if who in ("p1", "both"):
            lines.append("patch=1,EE,01C6C750,word,00000001")
        if who in ("p2", "both"):
            lines.append("patch=1,EE,01C6C4E8,word,00000001")
    else:
        raise SystemExit("unknown option " + o)
out.mkdir(parents=True, exist_ok=True)
(out / NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(lines), "lines")
