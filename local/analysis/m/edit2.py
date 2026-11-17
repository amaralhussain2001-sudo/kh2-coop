"""One-off edit of tools/merge/make_all.py: build() and main() learn --v2 (lane G section + extended glue)."""
import pathlib
import sys

p = pathlib.Path(sys.argv[1])
t = p.read_text()


def rep(old, new):
    global t
    assert t.count(old) == 1, "expected exactly one: " + old[:70]
    t = t.replace(old, new)


rep('''def build(without=()):
    sections = []   # (name, title, rows)''', '''COMMANDS_S2 = 0x000F1000          # lane G: data of the second control object, 0xB00 bytes (reserved)


def commands_section():
    """Lane G's routines, assembled by lane G's own generator code (copy: tools/merge/g_cmd.py), unchanged."""
    import g_cmd
    a = g_cmd.build(hud_pin=True)
    code = a.build()
    lb = a.labels
    by_addr = {}
    for name, addr in lb.items():
        by_addr.setdefault(addr, []).append((name, ""))
    rows = [(addr, code[addr], by_addr.get(addr, []), "", a.notes.get(addr, "")) for addr in sorted(code)]
    j, jl = g_cmd.j_word, g_cmd.jal_word
    hooks = [
        (0x001781C4, j(lb["attach"]), 0x3C0401C6, "tail of the player's attach routine: a hero on controller 2 attaches to S2, any other to S"),
        (0x001781C8, 0x0200282D, 0xDFBF0008, "delay slot: a1 = player object (was ld ra,8(sp))"),
        (0x001D6A10, j(lb["detach_tail"]), None, "end of the control object's detach: 'current control object' = S if S still has a hero, else 0"),
        (0x00179BFC, j(lb["reset"]), jmp(0x001D68F8), "room reset wrapper: reset S, then S2 if it exists"),
        (0x00179BDC, j(lb["ginit"]), jmp(0x001D68E0), "start-up reset wrapper: the same for the start-up reset"),
        (0x00174400, j(lb["enable"]), None, "script command 'player commands on': applies to S and S2"),
        (0x00174404, 0, None, "delay slot (was lui t7,0x35)"),
        (0x001D6C58, j(lb["disable"]), None, "global 'commands off': applies to S and S2"),
        (0x001D6C5C, 0, None, "delay slot (was addiu sp,sp,-16)"),
        (0x001D6C88, j(lb["enable"]), None, "global 'commands on': applies to S and S2"),
        (0x001D6C8C, 0, None, "delay slot (was addiu sp,sp,-16)"),
        (0x0013B258, j(lb["setdisp"]), None, "on-screen menu 'use this control object': if S2 asks, S is shown"),
        (0x0013B25C, 0, None, "delay slot (the store moved into setdisp)"),
        (0x001BDC64, jl(lb["hudshow"]), jal(0x0013B2F8), "control object shows the menu: skipped for S2"),
        (0x001BDCA4, jl(lb["hudhide"]), jal(0x0013B320), "control object hides the menu: skipped for S2"),
        (0x001BDE30, jl(lb["hudfade"]), jal(0x0013B2B8), "control object sets the menu's fade value: skipped for S2"),
    ]
    return rows, hooks


def build(without=(), v2=False):
    sections = []   # (name, title, rows)''')
rep('''    use = lambda n: n not in without  # noqa: E731
''', '''    use = lambda n: n not in without  # noqa: E731
    cmds = v2 and use("commands")
''')
rep('''        hooks.append((0x00178294, jal(s["e_dtor"]), jal(0x001781E8), "identity", "base destructor: a dying twin does not unregister player 1's hero"))
''', '''        if not cmds:
            hooks.append((0x00178294, jal(s["e_dtor"]), jal(0x001781E8), "identity", "base destructor: a dying twin does not unregister player 1's hero"))
''')
rep('''    if use("identity") and use("ownhp"):
        s = add("glue", "merge glue: the fresh marked slot goes to the TWIN by lane E's roles, not by build order", GLUE_AT, GLUE_SRC)
''', '''    if cmds:
        rows, ghooks = commands_section()
        sections.append(("commands", "lane G commands: second control object S2 for the hero on controller 2 (routines unchanged)", rows))
        for addr, w, orig, meaning in ghooks:
            hooks.append((addr, w, orig, "commands", meaning))
    if use("identity") and use("ownhp"):
        src = GLUE_GETPAD + (GLUE_WRAP_V2 if cmds else GLUE_WRAP_V1) + GLUE_SLOT + (GLUE_DTOR if cmds else "")
        s = add("glue", "merge glue: the fresh marked slot goes to the TWIN by lane E's roles, not by build order"
                + ("; a twin built first is moved onto S2; S2 is released when a twin goes away" if cmds else ""), GLUE_AT, src)
        if cmds:
            hooks.append((0x00178294, jal(s["m_dtor"]), jal(0x001781E8), "glue", "base destructor: release a dying twin's control object S2, then lane E's e_dtor"))
''')
rep('''    check = "--check" in args
    args = [a for a in args if a != "--check"]
    out = pathlib.Path(args[0]) if args else ROOT / "patches" / "merged-v1"
    sections, hooks = build(without)
''', '''    check = "--check" in args
    v2 = "--v2" in args
    if v2 and "--keep-base" not in args:
        without.add("base")
    args = [a for a in args if a not in ("--check", "--v2", "--keep-base")]
    out = pathlib.Path(args[0]) if args else ROOT / "patches" / ("merged-v2" if v2 else "merged-v1")
    sections, hooks = build(without, v2)
''')
rep('''             "comment=Two-player project, merged build v1: " + " + ".join(names) + " (tools/merge/make_all.py).",''',
    '''             "comment=Two-player project, merged build %s: " % ("v2" if v2 else "v1") + " + ".join(names) + " (tools/merge/make_all.py).",''')
rep('''    lst = ["Merged patch v1 for CRC F266B00B. Every word the patch file writes, with its meaning.", ""]''',
    '''    lst = ["Merged patch %s for CRC F266B00B. Every word the patch file writes, with its meaning." % ("v2" if v2 else "v1"), ""]''')
rep('''    lst.append("SAVE DATA BYTES used: %08X (twin HP), %08X (twin MP + 1)" % (SYM["SAVE_HP"], SYM["SAVE_MP"]))''',
    '''    lst.append("SAVE DATA BYTES used: %08X (twin HP), %08X (twin MP + 1)" % (SYM["SAVE_HP"], SYM["SAVE_MP"]))
    if any(n == "commands" for n, _, _ in sections):
        lst.append("RESERVED DATA: %08X-%08X = second control object S2 (built by the game's own constructor on first use)" % (
            COMMANDS_S2, COMMANDS_S2 + 0xAFF))''')
rep('''        print("check against lane D (patches/lane-d-ownhp-v2): %d of %d words equal; different: %s" % (
            len(d) - len(diff_d), len(d), ", ".join("%08X" % a for a in diff_d) or "none"))''',
    '''        print("check against lane D (patches/lane-d-ownhp-v2): %d of %d words equal; different: %s" % (
            len(d) - len(diff_d), len(d), ", ".join("%08X" % a for a in diff_d) or "none"))
        if v2:
            g = lane_words(ROOT / "patches" / "lane-g-cmd-v3-no-pad-rule" / "SLPM-66675_F266B00B.pnach")
            diff_g = sorted(a for a in g if allw.get(a) != g[a])
            print("check against lane G (patches/lane-g-cmd-v3-no-pad-rule): %d of %d words equal; different: %s" % (
                len(g) - len(diff_g), len(g), ", ".join("%08X" % a for a in diff_g) or "none"))''')
p.write_text(t)
print("build() and main() updated for --v2")
