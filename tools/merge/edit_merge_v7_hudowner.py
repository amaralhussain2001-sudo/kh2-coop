"""One-off: tools/merge/merge_v7.py gets the FIFTY-SEVENTH GLUE (built only with --hudowner): THE HUD'S OWNER IS
PLAYER 1's HERO, OR NOBODY, NEVER THE TWIN, AND NEVER A HERO WITHOUT AN HP RECORD.
What was there (eighth round, parts 76 and 77; candidate v88 = the build 17 patch, the toy cannon with two
cannons, runs one10, one12, one13, one15):
- The toy cannon (object 0x03C8, its own class) attaches itself with the game's attach 0x001D6938, which makes
  the hero the HUD's owner (slot 0 of the party table 0x00348638) only "if he has an HP record". The first cannon
  has none; the second one, as the twin, has lane D's own unit slot (HP 0/0). So from the moment the second
  cannon is made the HUD's owner is THE TWIN (hud_probe: "HUD slot 0 = 01B1B1F0 (THE TWIN)").
- When the game ends, the second cannon goes away first. The base build's m_dtor (0x000F0D34) releases its
  control object and then puts "party slot 0 (HUD owner) back to player 1's hero" with no test: the first
  cannon, WITHOUT an HP record, becomes the owner. Player 1's own gauge takes it (refresh 0x00156E48, HP read
  0x001575C0) and asks "is his HP low" (0x001A2478) twice a step until the room ends: 50 fault lines.
The glue:
gh_tick (the call at 0x00138538, each step): the HUD's owner is the twin while player 1's hero is there: the
  owner becomes player 1's hero if he has an HP record, else the slot is emptied (the game's own state with
  one cannon).
gh_set (the call at 0x000F0D8C in m_dtor, was jal 0x0013DDC0): only a hero with an HP record becomes the owner.
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_hudowner.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "gh_tick" in s:
    raise SystemExit("already there")

a = "  python -I tools/merge/merge_v7.py [outDir]"
assert s.count(a) == 1
hdr = '''FIFTY-SEVENTH GLUE (built only with the option --hudowner): THE HUD'S OWNER IS PLAYER 1's HERO, OR NOBODY. The
game's attach 0x001D6938 makes a hero the HUD's owner (slot 0 of the party table 0x00348638: the hero the
game's own gauge shows) only if he has an HP record. A second toy cannon (glue 56) attaches itself that way
and, as the twin, has lane D's unit slot: it became the owner; and when it went away the base build's m_dtor
made the first cannon, which has NO HP record, the owner: fault lines in the gauge (0x001575C0, 0x001A2478).
gh_tick (the call at 0x00138538): the owner is the twin while player 1's hero is there: the owner becomes
  player 1's hero if he has an HP record, else the slot is emptied.
gh_set (the call at 0x000F0D8C, was jal 0x0013DDC0): m_dtor makes only a hero with an HP record the owner.

'''
s = s.replace(a, hdr + a)
b = " [--twinmake]"
assert s.count(b) == 1, s.count(b)
s = s.replace(b, b + " [--hudowner]")

i = s.index("def main():")
src = '''# ---- fifty-seventh glue (only with --hudowner) -------------------------------------------------------------
GH_AT = 0x000EBC00
GH_END = 0x000EBD00
GH_SRC = """
gh_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gh_go
    lui t5,0x0035
    lw t4,-31176(t5)              # 0x00348638: the HUD's owner (the hero the game's own gauge shows)
    bne t4,t6,gh_go               # not the twin: nothing to put right
    lw t2,-5816(t5)               # the engine's player = player 1's hero
    beq t2,zero,gh_go             # he is not there (yet): his own attach comes
    nop
    beq t2,t6,gh_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    lw t3,0x48C(t2)               # his HP record
    beq t3,zero,gh_clr
    move a1,t2
    jal 0x0013DDC0                # the owner = player 1's hero (the "changed" mark is set: the gauge takes him)
    move a0,zero
    b gh_done
    nop
gh_clr:
    jal 0x0013DDE8                # no HP record (the toy cannon): the slot is emptied, as the game has it
    move a0,zero
gh_done:
    ld ra,0(sp)
    addiu sp,sp,16
gh_go:
    j TICK_NEXT
    move a0,zero

gh_set:                           # the call at 0x000F0D8C (m_dtor; was jal 0x0013DDC0). a0 = 0, a1 = the engine's player
    lw t7,0x48C(a1)
    beq t7,zero,gh_ret
    nop
    j 0x0013DDC0
    nop
gh_ret:
    jr ra                         # no HP record: the game's own attach does not make him the owner either
    nop
"""


'''
s = s[:i] + src + s[i:]

e = "    out.mkdir(parents=True, exist_ok=True)" + NL + "    head = ["
assert s.count(e) == 1
step = '''    if "--hudowner" in sys.argv:                                           # fifty-seventh glue (the HUD's owner is player 1's hero or nobody)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GH_AT, GH_END, GH_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "the HUD's owner is player 1's hero or nobody, never the twin, never a hero without an HP record")
        hook_base(0x00138538, tick_next, jal(labels["gh_tick"]), "the field's START look-out: first, is the HUD's owner right")
        hook_base(0x000F0D8C, jal(0x0013DDC0), jal(labels["gh_set"]), "the twin goes away: player 1's hero becomes the HUD's owner only with an HP record")
        n_glue += n

'''
s = s.replace(e, step + e)
p.write_text(s, encoding="utf-8", newline=NL)
print("ok")
