"""Lane N, TEST ONLY: extra patch lines for tests (never part of the game patch). The lines are the same on both
PCs and depend only on the game's own frame counter, so a linked session stays in sync.

  python -I tools/lane-n/make_testlines.py <outFile> [hp:SLOTHEX=VALUE@A-B ...] [mp:SLOTHEX=VALUE@A-B ...] [kit] [potions]

  hp:SLOT=V@A-B   hold the unit slot's HP at V while the session frame is in [A, B)  (the next hit is lethal if V = 1)
  mp:SLOT=V@A-B   the same for MP
  kit             lane G's test skills for a fresh save: Guard, Dodge Roll, Aerial Dodge, High Jump, Glide; magic
                  Fire, Blizzard, Thunder, Cure; shortcuts L1 + Circle/Triangle/Square/Cross = Fire/Blizzard/Thunder/Cure
  potions         (after kit) 9 Potions in the stock, Potions in Sora's three item slots, shortcut L1 + Circle =
                  Potion (addresses from the community GoA script, HYPOTHESIS until a test shows a Potion used)
Slots on the twin-first test discs without friends: twin 01C6C750, hero 01C6C4E8.
Session frame = the game's counter (16 bits of 0x0034D4BC) + 152, so tests must stay below frame 65,000.
"""
import pathlib
import sys

SAVE = 0x0032BB30
CNT = 0x0034D4BC


def window(a, b, payload):
    """lines that run `payload` (one code line) only while a <= session frame < b"""
    va, vb = a - 153, b - 152
    if not (0 <= va <= 0xFFFF and 0 < vb <= 0xFFFF):
        sys.exit("frame window out of range")
    return ["patch=1,EE,E002%04X,extended,3%07X" % (va, CNT),   # counter > a-153: run the next 2 lines
            "patch=1,EE,E001%04X,extended,2%07X" % (vb, CNT),   # counter < b-152: run the next line
            payload]


def main():
    out = pathlib.Path(sys.argv[1])
    lines = []
    for arg in sys.argv[2:]:
        if arg == "kit":
            for i, a in enumerate([0x0052, 0x0234, 0x0066, 0x005E, 0x006A]):
                lines.append("patch=1,EE,%08X,short,%04X" % (SAVE + 0x2544 + 2 * i, a | 0x8000))
            for i in range(4):
                lines.append("patch=1,EE,%08X,byte,01" % (SAVE + 0x3594 + i))
            for i, cmd in enumerate([0x0031, 0x0033, 0x0032, 0x0034]):
                lines.append("patch=1,EE,%08X,short,%04X" % (SAVE + 0x36F8 + 2 * i, cmd))
        elif arg == "potions":
            lines.append("patch=1,EE,%08X,byte,09" % (SAVE + 0x3580))          # Potion stock
            for i in range(3):                                                  # Potion (item 1) in Sora's item slots
                lines.append("patch=1,EE,%08X,short,0001" % (SAVE + 0x2524 + 2 * i))
            lines.append("patch=1,EE,%08X,short,0017" % (SAVE + 0x36F8))       # shortcut L1 + Circle = Potion
        elif arg.startswith(("hp:", "mp:")):
            kind, rest = arg.split(":", 1)
            slot, rest = rest.split("=")
            val, rng = rest.split("@")
            a, b = rng.split("-")
            addr = int(slot, 16) + (0 if kind == "hp" else 0x180)
            lines += window(int(a), int(b), "patch=1,EE,2%07X,extended,%08X" % (addr, int(val)))
        else:
            sys.exit("unknown item " + arg)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(chr(10).join(lines) + chr(10))
    print(out, len(lines), "lines")


if __name__ == "__main__":
    main()
