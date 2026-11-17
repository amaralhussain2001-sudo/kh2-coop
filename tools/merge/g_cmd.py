"""Lane G: "each hero has its own command controller" patch for Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B).

  python -I tools/lane-g/make_cmd.py <outDir> [--no-pad-rule] [--list]

Background (docs/lanes/G-commands.md): every player object talks to ONE control object S (0x01C5F530, class table
0x00351260): command menu, cursor, shortcut mode, command request, lock-on manager (S+0xAC0). Player objects reach
it only through their own pointers (object+0xB3C, +0xB44, +0xB40).

This patch gives the hero that uses logical controller 2 (object+0xB38 == 0x0034D720) a SECOND control object S2,
built with the game's own constructor in spare memory, so nothing in S is shared any more:
  - S  keeps player 1, controller 1, the on-screen command menu;
  - S2 has player 2, controller 2, its own cursor / shortcut / request / lock-on state (not drawn).
Lane A's per-update hook (0x00178898 / 0x001788A0, routine 0x000F0020) is NOT used any more: with one control
object per hero the original code is right again. Lane A's controller rule at the player factory (0x0017A000 ->
0x000F0000) is kept unless --no-pad-rule is given (lane E owns that hook).

Memory used:  routines 0x000F0800-0x000F0BFF,  S2 data 0x000F1000-0x000F1AFF (0xB00 bytes, must start as zero).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from g_asm import Asm, j_word, jal_word  # noqa: E402

S = 0x01C5F530
S_LO = -2768                 # S = (0x01C6 << 16) - 2768
S2 = 0x000F1000
LOG2 = 0x0034D720            # logical controller 2
CUR_HI, CUR_LO = 0x0035, 0x27E0   # 0x003527E0: the game's "current control object" pointer
VT_S = 0x00351260
F_CTOR_BASE = 0x001BCF80     # base constructor of the control object
F_LISTINIT = 0x00190128
F_LOCKINIT = 0x0019C920      # constructor of the lock-on manager (member at +0xAC0)
F_GLOBALINIT = 0x001BDE88    # what the game's start-up reset does to S
F_GLOBALINIT_WRAP = 0x001D68E0   # the routine the game's start-up reset jumps to (calls 0x001BDE88)
F_ROOMRESET = 0x001D68F8     # what every room load does to S
F_ATTACH = 0x001D6938        # attach(control object, player object)
F_DISABLE = 0x001D6A80
F_ENABLE = 0x001D6AB0
CAVE, CAVE_END = 0x000F0800, 0x000F0C00


F_HUD_SHOW, F_HUD_HIDE, F_HUD_FADE = 0x0013B2F8, 0x0013B320, 0x0013B2B8


def build(hud_pin=True):
    a = Asm(CAVE, CAVE_END)

    # ---- ensure: build S2 once (its first word, the class table pointer, is 0 until then) ----
    a.label("ensure")
    a.li32("t7", S2, "t7 = S2")
    a.lw("t6", 0, "t7")
    a.bne("t6", "zero", "ensure_done", "already built")
    a.nop()
    a.addiu("sp", "sp", -32)
    a.sd("ra", 0, "sp")
    a.sd("s1", 8, "sp")
    a.daddu("s1", "t7", "zero")
    a.jal(F_CTOR_BASE, "base constructor(S2)")
    a.daddu("a0", "s1", "zero")
    a.lui("t7", VT_S >> 16)
    a.addiu("t7", "t7", VT_S & 0xFFFF)
    a.sw("t7", 0, "s1", "S2 class table = 0x00351260")
    for off in (0xA68, 0xA7C, 0xA90):
        a.jal(F_LISTINIT, "list init(S2+0x%X)" % off)
        a.addiu("a0", "s1", off)
    a.jal(F_LOCKINIT, "lock-on manager constructor(S2+0xAC0)")
    a.addiu("a0", "s1", 0xAC0)
    a.sw("zero", 0xAF0, "s1")
    a.jal(F_GLOBALINIT, "start-up reset(S2)")
    a.daddu("a0", "s1", "zero")
    a.jal(F_ROOMRESET, "room reset(S2)")
    a.daddu("a0", "s1", "zero")
    a.ld("ra", 0, "sp")
    a.ld("s1", 8, "sp")
    a.addiu("sp", "sp", 32)
    a.label("ensure_done")
    a.jr("ra")
    a.nop()

    # ---- fixcur: "current control object" pointer = S if S has a player, else 0 ----
    a.label("fixcur")
    a.lui("t6", 0x01C6)
    a.addiu("t6", "t6", S_LO, "t6 = S")
    a.lw("t5", 0xAF4, "t6", "S->attached player")
    a.lui("t7", CUR_HI)
    a.beq("t5", "zero", "fixcur_zero")
    a.nop()
    a.jr("ra")
    a.sw("t6", CUR_LO, "t7")
    a.label("fixcur_zero")
    a.jr("ra")
    a.sw("zero", CUR_LO, "t7")

    # ---- attach: tail of the player's "attach to control object" routine (0x001781C4) ----
    # here: s0 = player object, a1 = player object, stack frame of the caller: s0 at 0(sp), ra at 8(sp)
    a.label("attach")
    a.lw("t6", 0xB38, "s0", "this object's controller")
    a.li32("t7", LOG2)
    a.bne("t6", "t7", "attach_primary", "controller 1 -> normal path")
    a.nop()
    a.jal("ensure")
    a.nop()
    a.li32("a0", S2)
    a.sw("a0", 0xB3C, "s0", "object->control = S2")
    a.sw("a0", 0xB44, "s0")
    a.addiu("t6", "a0", 0xAC0)
    a.sw("t6", 0xB40, "s0", "object->lock-on manager = S2+0xAC0")
    a.jal(F_ATTACH, "attach(S2, object)")
    a.daddu("a1", "s0", "zero")
    a.jal("fixcur", "the game's current-control pointer stays on S")
    a.nop()
    a.ld("ra", 8, "sp")
    a.ld("s0", 0, "sp")
    a.jr("ra")
    a.addiu("sp", "sp", 16)
    a.label("attach_primary")
    a.lui("a0", 0x01C6)
    a.addiu("a0", "a0", S_LO)
    a.daddu("a1", "s0", "zero")
    a.sw("a0", 0xB3C, "s0")
    a.ld("ra", 8, "sp")
    a.ld("s0", 0, "sp")
    a.j(F_ATTACH, "attach(S, object) as the game did")
    a.addiu("sp", "sp", 16)

    # ---- detach tail (0x001D6A10): after any detach the current-control pointer follows S ----
    a.label("detach_tail")
    a.lui("t6", 0x01C6)
    a.addiu("t6", "t6", S_LO)
    a.lw("t5", 0xAF4, "t6")
    a.lui("t7", CUR_HI)
    a.beq("t5", "zero", "dt_zero")
    a.nop()
    a.sw("t6", CUR_LO, "t7")
    a.ld("s0", 0, "sp")
    a.jr("ra")
    a.addiu("sp", "sp", 16)
    a.label("dt_zero")
    a.sw("zero", CUR_LO, "t7")
    a.ld("s0", 0, "sp")
    a.jr("ra")
    a.addiu("sp", "sp", 16)

    # ---- room reset (0x00179BFC): reset S as before, then S2 if it exists ----
    a.label("reset")
    a.addiu("sp", "sp", -16)
    a.sd("ra", 0, "sp")
    a.jal(F_ROOMRESET, "room reset(S), a0 = S from the caller")
    a.nop()
    a.li32("a0", S2)
    a.lw("t6", 0, "a0")
    a.beq("t6", "zero", "reset_out", "S2 never built")
    a.nop()
    a.jal(F_ROOMRESET, "room reset(S2)")
    a.nop()
    a.label("reset_out")
    a.ld("ra", 0, "sp")
    a.jr("ra")
    a.addiu("sp", "sp", 16)

    # ---- start-up reset (0x00179BDC): what the game does to S when it (re)starts, also for S2 if it exists ----
    a.label("ginit")
    a.addiu("sp", "sp", -16)
    a.sd("ra", 0, "sp")
    a.jal(F_GLOBALINIT_WRAP, "start-up reset(S), a0 = S from the caller")
    a.nop()
    a.li32("a0", S2)
    a.lw("t6", 0, "a0")
    a.beq("t6", "zero", "ginit_out", "S2 never built")
    a.nop()
    a.jal(F_GLOBALINIT_WRAP, "start-up reset(S2)")
    a.nop()
    a.label("ginit_out")
    a.ld("ra", 0, "sp")
    a.jr("ra")
    a.addiu("sp", "sp", 16)

    # ---- global "commands off" / "commands on" (0x001D6C58 / 0x001D6C88): apply to S and to S2 ----
    for name, fn in (("disable", F_DISABLE), ("enable", F_ENABLE)):
        a.label(name)
        a.addiu("sp", "sp", -16)
        a.sd("ra", 0, "sp")
        a.lui("t7", CUR_HI)
        a.lw("a0", CUR_LO, "t7")
        a.beq("a0", "zero", name + "_1")
        a.nop()
        a.jal(fn, name + "(current control object)")
        a.nop()
        a.label(name + "_1")
        a.li32("a0", S2)
        a.lw("t6", 0xAF4, "a0", "S2 has a player? (0 while S2 is unused)")
        a.beq("t6", "zero", name + "_2")
        a.nop()
        a.jal(fn, name + "(S2)")
        a.nop()
        a.label(name + "_2")
        a.ld("ra", 0, "sp")
        a.jr("ra")
        a.addiu("sp", "sp", 16)
    if hud_pin:
        # ---- the on-screen command menu always belongs to S (player 1); S2 never takes it, shows, hides or fades it ----
        a.label("setdisp")            # replaces 0x0013B258: display->control (display+0x29C) = a1
        a.li32("t7", S2)
        a.bne("a1", "t7", "setdisp_store")
        a.nop()
        a.lui("a1", 0x01C6)
        a.addiu("a1", "a1", S_LO, "S2 asked: show S instead")
        a.label("setdisp_store")
        a.jr("ra")
        a.sw("a1", 0x29C, "a0")
        for name, fn, reg in (("hudshow", F_HUD_SHOW, "s0"), ("hudhide", F_HUD_HIDE, "s0"), ("hudfade", F_HUD_FADE, "s1")):
            a.label(name)             # called in place of the game's routine; reg = control object doing the call
            a.li32("t7", S2)
            a.beq(reg, "t7", name + "_skip", "S2 does not touch the on-screen menu")
            a.nop()
            a.j(fn, "S: the game's routine as before")
            a.nop()
            a.label(name + "_skip")
            a.jr("ra")
            a.nop()
    return a


def lane_a_pad_rule():
    """Lane A's rule at the player factory: first player object -> controller 1, any further -> controller 2."""
    code = {0x000F0000: 0x3C0F0035, 0x000F0004: 0x8DEE2400, 0x000F0008: 0x08059FC6, 0x000F000C: 0x000E202B}
    hooks = {0x0017A000: (0x0C03C000, "player factory: was jal 0x00167F18; now through 0x000F0000 (lane A rule)")}
    return code, hooks


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    out = pathlib.Path(args[0])
    hud_pin = "--no-hud-pin" not in sys.argv
    a = build(hud_pin)
    code = a.build()
    lb = a.labels
    hooks = {
        0x001781C4: (j_word(lb["attach"]), "player attach routine: was lui a0,0x1C6; now jumps to 'attach'"),
        0x001781C8: (0x0200282D, "delay slot: a1 = player object (was ld ra,8(sp))"),
        0x001D6A10: (j_word(lb["detach_tail"]), "detach: was lui t7,0x35; now jumps to 'detach_tail' (0x001D6A14 ld ra stays)"),
        0x00179BFC: (j_word(lb["reset"]), "room reset wrapper: was j 0x001D68F8"),
        0x00179BDC: (j_word(lb["ginit"]), "start-up reset wrapper: was j 0x001D68E0"),
        0x00174400: (j_word(lb["enable"]), "script command 'player commands on' (acted on the last-built player only): now S and S2"),
        0x00174404: (0x00000000, "delay slot (was lui t7,0x35)"),
        0x001D6C58: (j_word(lb["disable"]), "global 'commands off': was lui t7,0x35"),
        0x001D6C5C: (0x00000000, "delay slot (was addiu sp,sp,-16)"),
        0x001D6C88: (j_word(lb["enable"]), "global 'commands on': was lui t7,0x35"),
        0x001D6C8C: (0x00000000, "delay slot (was addiu sp,sp,-16)"),
    }
    if hud_pin:
        hooks.update({
            0x0013B258: (j_word(lb["setdisp"]), "on-screen menu 'use this control object': was jr ra / sw a1,0x29C(a0)"),
            0x0013B25C: (0x00000000, "delay slot (the store moved into 'setdisp')"),
            0x001BDC64: (jal_word(lb["hudshow"]), "control object 'show menu': was jal 0x0013B2F8"),
            0x001BDCA4: (jal_word(lb["hudhide"]), "control object 'hide menu': was jal 0x0013B320"),
            0x001BDE30: (jal_word(lb["hudfade"]), "control object update 'menu fade value': was jal 0x0013B2B8"),
        })
    lines = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, lane G: a second command controller (S2) for the hero on controller 2.",
        "comment=Every PC in an online game must have this same file (it changes game code).",
    ]
    if "--no-pad-rule" not in sys.argv:
        ca, ha = lane_a_pad_rule()
        code.update(ca)
        hooks.update(ha)
    for addr in sorted(code):
        lines.append(f"patch=1,EE,{addr:08X},word,{code[addr]:08X}")
    for addr in sorted(hooks):
        lines.append(f"patch=1,EE,{addr:08X},word,{hooks[addr][0]:08X}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")
    listing = ["routines 0x%08X-0x%08X (%d instructions), labels:" % (CAVE, a.pc - 4, len(a.items))]
    listing += ["  %-16s 0x%08X" % (k, v) for k, v in sorted(lb.items(), key=lambda kv: kv[1])]
    listing += ["hooks:"] + ["  0x%08X = %08X  %s" % (k, v[0], v[1]) for k, v in sorted(hooks.items())]
    listing += ["code:"] + ["  0x%08X  %08X  %s" % (k, code[k], a.notes.get(k, "")) for k in sorted(code)]
    (out / "listing.txt").write_text("\n".join(listing) + "\n")
    if "--list" in sys.argv:
        print("\n".join(listing))
    else:
        print("\n".join(listing[:len(lb) + 2 + len(hooks)]))


if __name__ == "__main__":
    main()
