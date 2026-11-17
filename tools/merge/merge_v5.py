"""Merged build 5 = merged-v4 + one glue routine: player 2's small gauge hides its rings together with player 1's.

What the user saw: in the first town the game shows player 1's gauge as a face only (no HP ring, no MP bar),
but player 2's small gauge kept its green and blue rings.

How the game does it (VERIFIED by reading the program and by a memory probe, tests g1-town / g1-roam):
the player gauge hides its parts when its character's unit slot has bit 1 (value 2) in the flag word at
slot+0x250 (routine around 0x001567B0: hero+0x48C -> slot, slot+0x250 & 2). In the first town the word is 7,
in a normal room 1. The friend gauge (the class player 2's small gauge is made of) has no such rule.
Which parts are the rings (VERIFIED by hiding each part in turn, tests g2-parts and g4-parts-town): the part at
gauge+0x6CC is the HP ring, the part at gauge+0x868 is the MP ring, the part at gauge+0x394 is the dark ring
under them (flag words at +12; flag 0x40 = hidden). The face is the part at gauge+0x40 and stays.

The glue: a new "update" method for the twin gauge. It runs lane V2's update first, then looks at PLAYER 1's
hero (HUD party slot 0, 0x00348638) and sets or clears flag 0x40 on the three ring parts. So the two gauges always
agree. Routine at 0x000F3440 (free: lane R verified 0x000F3000-0x000F37FF unused; the merge-3 glue ends at
0x000F3427); the only changed word of merged-v4 is the method pointer in lane V2's class table (0x000F7004).

  python -I tools/merge/merge_v5.py [outDir] [--no-rings]

Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v5.
"""
import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from asm import assemble  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
BASE = ROOT / "patches" / "merged-v4"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})\s*(?://.*)?$")
GLUE_AT = 0x000F3440
TG_CLASS_UPDATE = 0x000F7004      # lane V2: class table of the twin gauge, word 1 = its update method
PARTY = 0x00348638                # HUD party table, slot 0 = player 1's hero

SRC = """
tg_rings:                         # class method "update" of the twin gauge. a0 = gauge
    addiu sp,sp,-16
    sd ra,0(sp)
    sd s0,8(sp)
    jal TG_UPDATE                 # lane V2's update (it ends in the game's own friend gauge update)
    move s0,a0
    lw t7,0x34(s0)                # the gauge's character: 0 = no twin, the gauge is hidden as a whole
    beq t7,zero,tr_done
    lui t7,%hi(PARTY)
    lw t7,%lo(PARTY)(t7)          # player 1's hero
    beq t7,zero,tr_done
    nop
    lw t6,0x48C(t7)               # his unit slot
    beq t6,zero,tr_done
    nop
    lw t6,0x250(t6)               # slot flags: bit 1 = the game hides the player gauge's rings
    andi t6,t6,2
    lw t5,0x6D8(s0)               # flag word of the HP ring part (part at gauge+0x6CC)
    lw t4,0x874(s0)               # flag word of the MP ring part (part at gauge+0x868)
    lw t2,0x3A0(s0)               # flag word of the dark ring under them (part at gauge+0x394)
    beq t6,zero,tr_show
    li t3,-65
    ori t5,t5,0x40
    ori t4,t4,0x40
    b tr_store
    ori t2,t2,0x40
tr_show:
    and t5,t5,t3
    and t4,t4,t3
    and t2,t2,t3
tr_store:
    sw t5,0x6D8(s0)
    sw t4,0x874(s0)
    sw t2,0x3A0(s0)
tr_done:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,16
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = ROOT / (args[0] if args else "patches/merged-v5")
    order, words = [], {}
    for raw in (BASE / NAME).read_text(encoding="utf-8").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        a = int(m.group(2), 16)
        assert m.group(1) == "1" and m.group(3).lower() == "word" and a not in words, raw
        order.append(a)
        words[a] = int(m.group(4), 16)
    origin = {}
    for raw in (BASE / "listing.txt").read_text(encoding="utf-8").splitlines():
        parts = raw.split(None, 2)
        if len(parts) == 3:
            origin[int(parts[0], 16)] = parts[2]

    n_glue = 0
    if "--no-rings" not in sys.argv:
        if TG_CLASS_UPDATE not in words:
            raise SystemExit("lane V2's class table word 0x000F7004 is not in merged-v4")
        tg_update = words[TG_CLASS_UPDATE]
        if not (0x000F7000 <= tg_update < 0x000F7240):
            raise SystemExit("0x000F7004 does not point into lane V2's gauge code: %08X" % tg_update)
        code, labels = assemble(GLUE_AT, SRC, {"TG_UPDATE": tg_update, "PARTY": PARTY})
        code = [w if isinstance(w, int) else w[1] for w in code]
        for i, w in enumerate(code):
            a = GLUE_AT + 4 * i
            if a in words:
                raise SystemExit("glue address already used: %08X" % a)
            words[a] = w
            order.append(a)
            origin[a] = "glue (player 2's gauge rings hide with player 1's)"
        words[TG_CLASS_UPDATE] = GLUE_AT
        origin[TG_CLASS_UPDATE] = "glue (was lane V2: update method %08X)" % tg_update
        n_glue = len(code)

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, MERGED BUILD 5: merged build 4 (twin on pad 2, own HP, commands, exits, enemy",
        "comment=targeting, down and rescue, gauge for player 2, enemy HP gauge above 3400 HP for bosses +75 %)",
        "comment=+ player 2's gauge rings hide with player 1's. Every PC in an online game must have this same file.",
    ]
    body = ["patch=1,EE,%08X,word,%08X" % (a, words[a]) for a in order]
    (out / NAME).write_text("\n".join(head + body) + "\n", encoding="utf-8")
    listing = ["%08X %08X  %s" % (a, words[a], origin.get(a, "merged-v4")) for a in sorted(words)]
    (out / "listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    print("merged-v4 words:", len(order) - n_glue, "+ glue words:", n_glue, "=", len(order))
    print("written:", out / NAME)
    print("sha1:", hashlib.sha1((out / NAME).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
