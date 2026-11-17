"""One-off: THE SEVENTY-SECOND GLUE of tools/merge/merge_v7.py (--drivesave): PLAYER 2'S OWN DRIVE GAUGE IN THE SAVE
(tenth round, the user's answer to the inspection proposals of 2026-11-15 night: "do 1 and 4", proposal 4).
BEFORE (build 21, READ in merge_v6.py's drive glue): the twin's Drive values live in memory only (0x000F47D0); a save
on the memory card holds player 1's values; after a Load Game both heroes start with player 1's gauge and bars.
THE GLUE:
  dv_tick (head of the controller task's calls at 0x00167E90, every frame): while the twin exists (0x000F05CC), his
    slot has the second hero's mark (slot+0x250 bit 31) and Sora's save block (slot+0x260 = 0x0032E020), his gauge
    and bars (slot+0x1B0, +0x1B1) are copied into King Mickey's record + 0x52 / + 0x53 with the mark 0x5037 at
    + 0x50. Those 4 bytes are free (STATE part 89: Mickey's record + 0x40 .. + 0x53 is never written by the game;
    + 0x40 .. + 0x4F are taken by glues 63, 62, 69, 71). They are part of the save data, so a save holds them.
  dv_load (snap_none's end, in "the load menu fills the snapshot" 0x001CD2B8, i.e. a Load Game): if the save data
    has the mark, "what player 1 wrote last" := the save's 12 Drive bytes, the twin's copy := the same 12 bytes with
    HIS gauge and bars (bars never above the common most bars), valid := 1. His next slot load takes them.
  dv_ext (in dr_load's dl_ext, the path for "the save data does not hold what player 1 wrote last": a loaded save,
    a Continue whose snapshot has no twin values, the story): the same restore when the mark is there; without
    the mark (New Game, a save from build 21 or older) both heroes take the save's values as before.
Max bars and Drive levels stay common. Code at 0x000EE800 .. 0x000EE900 (free, inside this round's room).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_drivesave.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "--drivesave" in s:
    raise SystemExit("already there")

DOC = '''SEVENTY-SECOND GLUE (built only with the option --drivesave): PLAYER 2'S OWN DRIVE GAUGE IN THE SAVE. dv_tick (head of
the controller task's calls at 0x00167E90) copies the twin's gauge and bars into King Mickey's record + 0x52 / + 0x53 with
the mark 0x5037 at + 0x50 (free bytes, STATE part 89), so a save holds them; dv_load (end of the twenty-second glue's
snap_none: a Load Game) and dv_ext (in the drive glue's dl_ext) give them back to the twin's own copy. Without the mark
(New Game, an older save) both heroes take the save's values as before.

'''
a = "  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn]"
assert s.count(a) == 1
s = s.replace(a, DOC + a)

SRC = '''# ---- seventy-second glue (only with --drivesave) -------------------------------------------------------------
DV_AT = 0x000EE800
DV_END = 0x000EE900
DV_SRC = """
dv_tick:                          # from 0x00167E90 (the controller task, every frame): the twin's gauge and bars into the save data
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin's object (lane E; 0 = none)
    beq t6,zero,dvt_go
    nop
    lw t6,0x48C(t6)               # his slot
    beq t6,zero,dvt_go
    nop
    lw t5,0x250(t6)               # the second hero's mark (bit 31)
    bgez t5,dvt_go
    lui t4,0x0033
    lw t5,0x260(t6)               # his save block: Sora's record (0x0032E020), whose Drive bytes the game keeps
    addiu t4,t4,-8160
    bne t5,t4,dvt_go
    lui t7,0x0033
    lbu t5,0x1B0(t6)              # his gauge
    lbu t4,0x1B1(t6)              # his bars
    sb t5,-7250(t7)               # King Mickey's record + 0x52 (0x0032E3AE)
    sb t4,-7249(t7)               # + 0x53
    ori t5,zero,0x5037
    sh t5,-7252(t7)               # + 0x50: the mark
dvt_go:
    j DV_NEXT
    nop

dv_load:                          # from snap_none's end (0x001CD2D0 in "the load menu fills the snapshot" 0x001CD2B8, a Load
    lui t1,0x0033                 # Game). Only t1 .. t4 are free there: t5 / t6 / t7 must stay
    lhu t2,-7252(t1)              # King Mickey's record + 0x50: the mark
    ori t3,zero,0x5037
    bne t2,t3,dvl_out             # no values of player 2 in this save: as before
    lui t4,0x000F
    lw t2,-4008(t1)               # the save's 12 Drive bytes (0x0032F058 ..): "what player 1 wrote last" from now on,
    sw t2,0x47C4(t4)              # and the twin's copy starts from them
    sw t2,0x47D0(t4)
    lw t2,-4004(t1)
    sw t2,0x47C8(t4)
    sw t2,0x47D4(t4)
    lw t2,-4000(t1)
    sw t2,0x47CC(t4)
    sw t2,0x47D8(t4)
    lbu t2,-7250(t1)              # his gauge
    sb t2,0x47D0(t4)
    lbu t2,-7249(t1)              # his bars, never more than the most bars (common: the save's)
    lbu t3,-4006(t1)
    sltu t3,t3,t2
    beq t3,zero,dvl_bars
    nop
    lbu t2,-4006(t1)
dvl_bars:
    sb t2,0x47D1(t4)
    ori t2,zero,1
    sw t2,0x47C0(t4)              # valid: his next slot load takes his own values
dvl_out:
    jr ra
    nop

dv_ext:                           # from 0x000F4668 in the drive glue's dl_ext (the save data does not hold what player 1 wrote
    lw t3,0x1040(t5)              # last). t5 = Sora's record, t4 = 0x000F0000; only t2 / t3 are free. First the two steps
    sw t3,0x47CC(t4)              # that the jump took the place of
    lhu t3,0x038C(t5)             # King Mickey's record + 0x50 (= Sora's record + 0x38C): the mark
    ori t2,zero,0x5037
    bne t3,t2,dve_out             # no values of player 2: both take the save's (as before)
    nop
    lw t3,0x1038(t5)              # his copy := the save's 12 bytes ..
    sw t3,0x47D0(t4)
    lw t3,0x103C(t5)
    sw t3,0x47D4(t4)
    lw t3,0x1040(t5)
    sw t3,0x47D8(t4)
    lbu t3,0x038E(t5)             # .. with his gauge
    sb t3,0x47D0(t4)
    lbu t3,0x038F(t5)             # .. and his bars, never more than the most bars
    lbu t2,0x103A(t5)
    sltu t2,t2,t3
    beq t2,zero,dve_bars
    nop
    lbu t3,0x103A(t5)
dve_bars:
    sb t3,0x47D1(t4)
    ori t3,zero,1
    sw t3,0x47C0(t4)              # valid
    lui t5,0x000F                 # out: his own copy (base + 0x1038 = 0x000F47D0)
    jr ra
    addiu t5,t5,0x3798
dve_out:
    jr ra
    nop
"""

'''
a = "# ---- sixty-sixth glue (only with --ship2score) ----"
assert s.count(a) == 1
s = s.replace(a, SRC + a)

STEP = '''    if "--drivesave" in sys.argv:                                          # seventy-second glue (player 2's own Drive gauge in the save)
        assert words.get(0x000F4668) == 0x8DAB1040 and words.get(0x000F466C) == 0xAD8B47CC, "the drive glue's dl_ext is not there"
        assert words.get(0x000F4670) == 0x03E00008 and words.get(0x000F4654) == 0xAD8047C0, "the drive glue's dl_ext is not there"
        assert words.get(0x000F49E4) == 0x3C09000F and words.get(0x000F49E8) == 0xAD207F34, "the snapshot glue's snap_none is not there"
        assert words.get(0x000F49F0) == 0x35AD0FC0 and words.get(0x001CD2D0) == 0x0C03D279, "the snapshot glue's snap_none is not there"
        dv_next = words[0x00167E90]
        assert (dv_next >> 26) == 3
        labels, n = add_code(DV_AT, DV_END, DV_SRC, {"DV_NEXT": (dv_next & 0x3FFFFFF) << 2},
                             "player 2's own Drive gauge in the save")
        hook_base(0x00167E90, dv_next, jal(labels["dv_tick"]), "the controller task: first, the twin's gauge and bars into the save data")
        hook_base(0x000F49EC, 0x03E00008, (2 << 26) | ((labels["dv_load"] >> 2) & 0x3FFFFFF), "a Load Game: the twin's own Drive values from the save")
        hook_base(0x000F4668, 0x8DAB1040, (2 << 26) | ((labels["dv_ext"] >> 2) & 0x3FFFFFF), "dl_ext: the twin's own Drive values from the save data")
        n_glue += n

'''
a = "    out.mkdir(parents=True, exist_ok=True)\n    head = ["
assert s.count(a) == 1
s = s.replace(a, STEP + a)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
