r"""One-off (STATE part 143; the user's words 2026-11-18: "okay do 5 8 9 11 2", item 2 = a co-op difficulty choice):
THE EIGHTIETH GLUE, option --difficulty: ORDINARY ENEMIES GET MORE HP WHEN THE HOST CHOOSES "HARD" OR "VERY HARD".
Adds to tools/merge/merge_v7.py the header paragraph, the glue's source (DH_AT .. DH_END) and the builder block (after the
seventy-ninth glue). Without --difficulty the builder writes exactly what it wrote before.
  python -I tools/merge/edit_merge_v7_difficulty.py          (run ONCE; it refuses a second run)
"""
import csv
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
P = HERE / "merge_v7.py"
t = P.read_text(encoding="utf-8")
if "--difficulty" in t:
    raise SystemExit("already done")

# the boss entries of lane B75 (86 raised + 5 left unchanged): they keep the disc's own +75 % and get nothing more
ids = sorted({int(r["entry_id"]) for r in csv.DictReader(open(HERE.parent / "lane-b75" / "data" / "boss_entries.csv", encoding="utf-8"))})
assert len(ids) == 91 and max(ids) < 256, (len(ids), max(ids))
table = bytearray(256)
for i in ids:
    table[i] = 1
words = [int.from_bytes(table[k:k + 4], "little") for k in range(0, 256, 4)]

HEADER_ANCHOR = "\n  python -I tools/merge/merge_v7.py [outDir]"
assert t.count(HEADER_ANCHOR) == 1
HEADER = """
EIGHTIETH GLUE (built only with the option --difficulty): A CO-OP DIFFICULTY FOR ORDINARY ENEMIES. The game fills an enemy's unit
slot from its entry of the enemy table (0x001A0EE0, lane B75): 32 HP values = (level percentage x value + 99) / 100, current =
maximum; then the damage limits from the maximum. The word after that loop (0x001A0F54) jumps to dh_hp: WITH A TWIN, when the
difficulty value V_DIFF (0x000DE810; 0 normal, 1 hard, 2 very hard; one patch line the LAUNCHER sets from the host's choice) is not 0
and the entry is NOT one of lane B75's 91 boss entries (a 256-byte table in the glue; bosses keep the disc's +75 %), the 32 values
become x 1.5 (rounded up) or x 2 before the damage limits are taken from them. One hero, or V_DIFF 0: nothing changes. The HP gauge
above 3400 is lane B75's gauge patch (in the build). Room 0x000DE200 .. 0x000DE400 (0x000D0000 .. 0x000DEFFF: no patch word).
"""
t = t.replace(HEADER_ANCHOR, HEADER + HEADER_ANCHOR, 1)

SRC_ANCHOR = "\ndef main():"
assert t.count(SRC_ANCHOR) == 1
GLUE = '''
# ---- eightieth glue (only with --difficulty) ------------------------------------------------------------------
DH_AT = 0x000DE200
DH_END = 0x000DE400
V_DIFF = 0x000DE810                                # 0 normal, 1 hard (x 1.5), 2 very hard (x 2): set by the launcher's patch line
DH_HOOK = (0x001A0F54, 0x944F0002)                 # lhu t7,2(v0), the first word after the HP loop of 0x001A0EE0
DH_BOSS_WORDS = %r
DH_SRC = """
dh_hp:                            # from 0x001A0F54 (j; its delay slot set t3 = 10000): s0 = the fresh unit slot, s1 = its entry
    lui t9,0x000F
    lw t8,0x05CC(t9)              # the twin: only with two heroes
    beq t8,zero,dh_out
    lui t9,0x000E
    lw t8,-6128(t9)               # V_DIFF (0x000DE810)
    beq t8,zero,dh_out
    lhu t0,0(s1)                  # the entry's id
    sltiu t1,t0,256
    beq t1,zero,dh_out
    lui t2,%%hi(DH_BOSS)
    addiu t2,t2,%%lo(DH_BOSS)
    addu t2,t2,t0
    lbu t2,0(t2)
    bne t2,zero,dh_out            # a boss entry: it has the disc's own +75 %%, nothing more
    move t0,s0
    addiu t4,s0,384               # 32 values of 12 bytes: current, maximum, 0
dh_loop:
    lw t5,4(t0)                   # the maximum
    addiu t6,zero,2
    beq t8,t6,dh_set              # very hard: x 2
    sll t6,t5,1
    addiu t6,t5,1                 # hard: x 1.5, rounded up
    srl t6,t6,1
    addu t6,t5,t6
dh_set:
    sw t6,4(t0)                   # maximum
    sw t6,0(t0)                   # current (a fresh slot is full)
    addiu t0,t0,12
    bne t0,t4,dh_loop
    nop
dh_out:
    lhu t7,2(v0)                  # the instruction that sat at 0x001A0F54
    j 0x001A0F5C
    nop
DH_BOSS:
""" + "".join("    .word 0x%%08X\\n" %% w for w in DH_BOSS_WORDS)
''' % (words,)
t = t.replace(SRC_ANCHOR, GLUE + SRC_ANCHOR, 1)

BLOCK_ANCHOR = """    out.mkdir(parents=True, exist_ok=True)
    head = [
"""
assert t.count(BLOCK_ANCHOR) == 1
BLOCK = '''    if "--difficulty" in sys.argv:                                         # eightieth glue (a co-op difficulty)
        assert V_DIFF == 0x000E0000 - 6128
        code, labels = assemble(DH_AT, DH_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert DH_AT + 4 * len(code) <= DH_END, "the eightieth glue does not fit"
        clash = [a for a in words if DH_AT <= a < DH_END]
        assert not clash, "patch words in 0x000DE200 .. 0x000DE3FF: %08X" % clash[0]
        assert V_DIFF not in words, "the difficulty word is written by the launcher's line, not by the builder"
        for i, w in enumerate(code):
            a = DH_AT + 4 * i
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (a co-op difficulty for ordinary enemies)"
        a, w0 = DH_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["dh_hp"] >> 2) & 0x3FFFFFF), "the HP loop of an enemy's unit slot is done: dh_hp (difficulty)")
        n_glue += len(code) + 1

'''
t = t.replace(BLOCK_ANCHOR, BLOCK + BLOCK_ANCHOR, 1)
P.write_text(t, encoding="utf-8")
print("merge_v7.py: the eightieth glue (--difficulty) added; boss ids", len(ids))
