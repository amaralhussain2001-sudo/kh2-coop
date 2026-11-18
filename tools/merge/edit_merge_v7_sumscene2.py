r"""One-off (STATE part 144; the user's words 2026-11-18: "finish the 11 9 8 for now", item 8 = player 2's Summon with its entrance
scene): THE EIGHTY-FIRST GLUE, option --sumscene2. Research: local\analysis\agent-summon\notes.txt (read-only agent).
The base patch's sm_skip (call 0x001C8444) skipped the entrance scene for a Summon the TWIN calls, because the scene is written for
"the player": the friend's start entry (run at once inside 0x00188120, called from 0x001C8540) asks trap_sysobj_player (0x00171074 ->
glue 45's tp_player) and captures that hero with motion 252, attaches itself and starts the camera on him.
Now: (1) 0x001C8444 is the game's call again (jal 0x001C8788 "is the entrance played?": the Config's "Summon Effects", per caller);
(2) su_player sits in front of tp_player at 0x00171074: when the script that asks belongs to a SUMMON FRIEND (class 0x00351E18), a
summon is out (0x01D49968 not 0) and the twin called it (V_SUMTW 0x000F47F4), the answer is the twin. Every other script: tp_player.
Without --sumscene2 the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_sumscene2.py          (run ONCE; it refuses a second run)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--sumscene2" in t:
    raise SystemExit("already done")

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTY-FIRST GLUE (built only with the option --sumscene2): PLAYER 2'S SUMMON PLAYS ITS ENTRANCE SCENE. The base patch's sm_skip
(0x001C8444) is replaced by the game's own call again (0x001C8788: the Config's "Summon Effects"), and su_player (in front of glue
45's tp_player at 0x00171074) answers "the player" with the twin for a SUMMON FRIEND's script (class 0x00351E18) while a summon the
twin called is out (V_SUMTW 0x000F47F4, state 0x01D49968 not 0). So the friend's entrance captures, attaches to and films the hero
who called him. Room 0x000DE400 .. 0x000DE480.
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eighty-first glue (only with --sumscene2) -------------------------------------------------------------------
SU_AT = 0x000DE400
SU_END = 0x000DE480
SU_SRC = """
su_player:                        # from 0x00171074 (was jal TP_NEXT = glue 45's tp_player): a script asks for "the player"
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,su_go
    lw t5,0x47F4(t7)              # V_SUMTW: the summon now out was called by the twin
    beq t5,zero,su_go
    lui t5,0x01D5
    lw t5,-26264(t5)              # 0x01D49968: the summon's state (0 = none out)
    beq t5,zero,su_go
    lui t5,0x0035
    lw t5,-10076(t5)              # the running script (0x0034D8A4)
    beq t5,zero,su_go
    nop
    lw t5,56(t5)                  # its object
    srl t4,t5,22
    addiu t4,t4,-6
    bne t4,zero,su_go             # not an object (the same test as tp_player's)
    nop
    lw t5,0(t5)                   # its class
    lui t4,0x0035
    ori t4,t4,0x1E18              # the summon friends' class (0x00351E18)
    bne t5,t4,su_go
    nop
    jr ra
    move v0,t6                    # a summon friend the twin called asks: the twin
su_go:
    j TP_NEXT
    nop
"""
'''
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--sumscene2" in sys.argv:                                          # eighty-first glue (player 2's summon scene)
        tp_next = words[0x00171074]
        assert (tp_next >> 26) == 3, "0x00171074 is not a jal"
        assert words.get(0x001C8444) == 0x0C03DF62, "0x001C8444 is not the base patch's jal sm_skip"
        code, labels = assemble(SU_AT, SU_SRC, {"TP_NEXT": (tp_next & 0x3FFFFFF) << 2})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert SU_AT + 4 * len(code) <= SU_END, "the eighty-first glue does not fit"
        clash = [a for a in words if SU_AT <= a < SU_END]
        assert not clash, "patch words in 0x000DE400 .. 0x000DE47F: %08X" % clash[0]
        for i, w in enumerate(code):
            a = SU_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (player 2's summon plays its entrance scene)"
        hook_base(0x00171074, tp_next, jal(labels["su_player"]), "trap_sysobj_player: first, a summon friend the twin called gets the twin")
        hook_base(0x001C8444, 0x0C03DF62, 0x0C0721E2, "the entrance scene: the game's own call again (also for the twin's summon)")
        n_glue += len(code)

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eighty-first glue (--sumscene2) added")
