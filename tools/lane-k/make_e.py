"""Lane E patch generator: player identity, camera owner, exits (CRC F266B00B, KH2 Final Mix SLPM-66675).

  python -I tools/lane-e/make_e.py <outDir> [options...]

Options (all off unless given):
  id        identity rule (default on in every build): see below
  noid      build WITHOUT the identity rule (lane A's order rule instead), for comparison tests
  exit      "both heroes at the exit" rule
  padplayer lane A variant: S->player follows the updating object (default: 'pad' variant, S->player untouched)

Base (lane A, unchanged): before a player object runs the shared control object's update, S->pad = that object's
own controller pointer (hook 0x00178898 / 0x001788A0, routine 0x000F0020).

Identity rule (this lane, replaces lane A's "second built = controller 2"):
  * A player object made through the PLAYER placeholder (object 0x236), or made when the engine has no player,
    is player 1's hero: logical controller 0, and it is/stays the engine's "player".
  * Any other player object is the twin: logical controller 1. After it is built, everything its constructor
    registered as "the player" is given back to player 1's hero (global player pointer, last-built pointer, unit
    slot back pointer, and the game's own attach routine: camera target, party table slot 0, command controller).
  * If a twin was built first and the placeholder hero arrives later, the earlier one is switched to controller 1.
  * When a player object that is not the engine's player is destroyed, the engine's player stays registered.
Code cave used: 0x000F0300-0x000F05FF (variables at 0x000F05C0).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from asm import assemble  # noqa: E402

SYM = {
    "GET_PAD": 0x00167F18,        # game: GetLogicalController(index)
    "S_UPDATE": 0x001D6BA0,       # game: shared control object update wrapper
    "FACTORY": 0x00179FD0,        # game: player factory
    "ATTACH": 0x001781A8,         # game: attach a player object (camera target, party slot 0, S->player)
    "DETACH": 0x001781E8,         # game: detach (called from the base destructor)
    "PH_LOOKUP": 0x001D1438,      # game: player object id for a form (called on the placeholder path only)
    "G_PLAYER": 0x0034E948,       # engine's player object pointer (read at 120 places)
    "G_LASTPLAYER": 0x00352400,   # last built object of the main player class
    "PAD0": 0x0034D6C0,
    "PAD1": 0x0034D720,
    "V_FLAG": 0x000F05C0,         # 1 while a placeholder-made player object is being created
    "V_ISP1": 0x000F05C4,         # role of the object being created
    "V_OLD": 0x000F05C8,          # engine's player before the creation
    "V_TWIN": 0x000F05CC,         # the twin object (0 if none)
}

LANE_A_B = """
    lw t6,0xB38(a0)               # this player object's own controller pointer (a0 = object, t7 = S)
    {padplayer}
    sw t6,0x9E4(t7)               # S->pad = it
    j S_UPDATE
    move a0,t7
"""

IDENTITY = """
e_mark:                           # hook 0x0016F0B0 (placeholder path of the object creator)
    lui t7,%hi(V_FLAG)
    li t6,1
    j PH_LOOKUP
    sw t6,%lo(V_FLAG)(t7)

e_getpad:                         # hook 0x0017A000 (player factory asks for the controller)
    lui t7,%hi(V_FLAG)
    lw t6,%lo(V_FLAG)(t7)
    sw zero,%lo(V_FLAG)(t7)
    lui t5,%hi(G_PLAYER)
    lw t5,%lo(G_PLAYER)(t5)
    sw t5,%lo(V_OLD)(t7)
    sltiu t4,t5,1
    or t6,t6,t4                   # player 1's hero if placeholder-made or no player exists yet
    sw t6,%lo(V_ISP1)(t7)
    j GET_PAD
    xori a0,t6,1                  # controller index 0 for player 1, 1 for the twin

e_wrap:                           # hook 0x0016F0F4 (the only call of the player factory)
    addiu sp,sp,-32
    sd ra,0(sp)
    jal FACTORY
    nop
    sd v0,8(sp)
    lui t7,%hi(V_FLAG)
    lw t6,%lo(V_ISP1)(t7)
    lw t5,%lo(V_OLD)(t7)
    bne t6,zero,e_p1
    nop
    sw v0,%lo(V_TWIN)(t7)         # a twin was built: hand the "player" role back
    lui t4,%hi(G_PLAYER)
    sw t5,%lo(G_PLAYER)(t4)
    lui t4,%hi(G_LASTPLAYER)
    sw t5,%lo(G_LASTPLAYER)(t4)
    lw t3,0x48C(t5)
    beq t3,zero,e_noslot
    nop
    sw t5,0x25C(t3)               # unit slot's back pointer
e_noslot:
    jal ATTACH
    move a0,t5
    b e_done
    nop
e_p1:
    beq t5,zero,e_done
    nop
    beq t5,v0,e_done
    nop
    sw t5,%lo(V_TWIN)(t7)         # an earlier player object becomes the twin
    lui t4,%hi(PAD1)
    addiu t4,t4,%lo(PAD1)
    sw t4,0xB38(t5)
e_done:
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32

e_dtor:                           # hook 0x00178294 (base destructor of player objects), a0 = dying object
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    lui t5,%hi(V_FLAG)
    lw t4,%lo(V_TWIN)(t5)
    bne t4,a0,e_d1
    nop
    sw zero,%lo(V_TWIN)(t5)
e_d1:
    beq t6,a0,e_dnormal
    nop
    beq t6,zero,e_dnormal
    nop
    lui t5,%hi(G_LASTPLAYER)      # another player object dies while the engine's player lives
    sw t6,%lo(G_LASTPLAYER)(t5)
    jr ra
    sw zero,0xB3C(a0)
e_dnormal:
    j DETACH
    sw zero,%lo(G_PLAYER)(t7)
"""

LANE_A_ORDER = """
a_getpad:                         # lane A's rule, kept only for comparison builds
    lui t7,%hi(G_LASTPLAYER)
    lw t6,%lo(G_LASTPLAYER)(t7)
    j GET_PAD
    sltu a0,zero,t6
"""


def jal(t):
    return (3 << 26) | ((t >> 2) & 0x3FFFFFF)


def j(t):
    return (2 << 26) | ((t >> 2) & 0x3FFFFFF)


def build(opts):
    code = {}
    hooks = {}
    notes = []
    words, _ = assemble(0x000F0020, LANE_A_B.format(padplayer="sw a0,0x9E0(t7)" if "padplayer" in opts else ""), SYM)
    for i, w in enumerate(words):
        code[0x000F0020 + 4 * i] = w
    hooks[0x00178898] = 0                       # was: a0 = S (moved into the routine)
    hooks[0x001788A0] = j(0x000F0020)           # was: j 0x001D6BA0
    notes.append("lane A base: S->pad per updating player object")
    if "noid" in opts:
        words, syms = assemble(0x000F0000, LANE_A_ORDER, SYM)
        for i, w in enumerate(words):
            code[0x000F0000 + 4 * i] = w
        hooks[0x0017A000] = jal(0x000F0000)
        notes.append("lane A order rule (comparison)")
    else:
        words, syms = assemble(0x000F0300, IDENTITY, SYM)
        for i, w in enumerate(words):
            code[0x000F0300 + 4 * i] = w
        end = 0x000F0300 + 4 * len(words)
        hooks[0x0016F0B0] = jal(syms["e_mark"])     # was: jal 0x001D1438
        hooks[0x0016F0F4] = jal(syms["e_wrap"])     # was: jal 0x00179FD0
        hooks[0x0017A000] = jal(syms["e_getpad"])   # was: jal 0x00167F18
        hooks[0x0017828C] = 0                       # was: sw zero,G_PLAYER (now done in e_dtor when it applies)
        hooks[0x00178294] = jal(syms["e_dtor"])     # was: jal 0x001781E8
        notes.append("identity rule: routines 0x000F0300-0x%08X" % (end - 1))
        extra = sys.modules.get("e_extra")
    return code, hooks, notes


def main():
    out = pathlib.Path(sys.argv[1])
    opts = set(sys.argv[2:])
    code, hooks, notes = build(opts)
    try:
        import e_exit  # optional module with the exit rule (added later in the lane)
        if "exit" in opts or "exit1" in opts:
            e_exit.add(code, hooks, notes, SYM, opts)
    except ImportError:
        if "exit" in opts or "exit1" in opts:
            sys.exit("exit rule module not present")
    out.mkdir(parents=True, exist_ok=True)
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project, lane E: " + "; ".join(notes) + ".",
             "comment=Every PC in an online game must have this same file (it changes game code)."]
    for a in sorted(code):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hooks):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hooks[a]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    print("%d code words, %d hook words -> %s" % (len(code), len(hooks), out / "SLPM-66675_F266B00B.pnach"))
    for n in notes:
        print("  ", n)


if __name__ == "__main__":
    main()
