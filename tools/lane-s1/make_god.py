"""Lane S1: TEST-ONLY patch variants on top of the merged build (never part of the game patch).

  python -I tools/lane-s1/make_god.py
Writes:
  patches/lane-s1-god/   merged-v2 lines + both heroes' HP held at 20 every frame (so a mission cannot end by a
                         defeat while a counter is being watched). On the lane's test discs the twin holds unit
                         slot address 0x01C6C750 and player 1's hero the next one, 0x01C6C4E8 (lane M).
  patches/lane-s1-god-hero/  the same, only player 1's hero held (the twin can be hurt)
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "patches" / "merged-v2" / "SLPM-66675_F266B00B.pnach"
TWIN_HP, HERO_HP = 0x01C6C750, 0x01C6C4E8


def write(name, addrs, note):
    d = ROOT / "patches" / name
    d.mkdir(parents=True, exist_ok=True)
    lines = BASE.read_text().rstrip("\n").split("\n")
    lines.append("comment=LANE S1 TEST ONLY: " + note)
    for a in addrs:
        lines.append("patch=1,EE,2%07X,extended,00000014" % a)
    (d / BASE.name).write_text("\n".join(lines) + "\n")
    print(d, len(lines), "lines")


write("lane-s1-god", [TWIN_HP, HERO_HP], "both heroes' HP held at 20")
write("lane-s1-god-hero", [HERO_HP], "player 1's hero's HP held at 20")
