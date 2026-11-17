"""One-off: THE SEVENTY-THIRD GLUE (--itemtarget), second form: "YOURSELF" WHILE YOUR PARTNER IS DOWN = THE DOWN PARTNER.
SEEN (candidate v131, tests kn-v131 on test-s1-hb9f and kb2-v131 on test-m-fight, 2026-11-16): player 1 picks the FIRST "Sora"
(himself) while the twin is down: player 1 is healed (10 -> 18), and the down twin stands up at the same moment with player 1's
HP from BEFORE the Potion (10; 6 in kb2). The path is the game's own routine 0x001A2A50 on the heroes' id while the twin is down,
which build 21 never took (lane N gives a down twin the Potion). Cause not looked into (HYPOTHESIS: the common character record /
the slot sync of 0x001A2A50).
THE DECISION (the user's standing rule: take my recommended option and note it): when the user picks HIMSELF and his partner is
down (lane N's flag: object + 0x7F8 bit 2), the item goes by lane N's rule = to the down partner, as in build 21 and as the
shortcuts do. A pick of the partner, or of oneself while the partner stands, is exact. ih_find follows the same rule.
Verified before: picks of the partner revive him (km-v131, kj-v131); the self pick of player 2 while player 1 is down did not
show the side effect (kk-v131), but the rule is the same for both players (simpler to explain).
The record of the edit; run once:
  python -I tools/merge/edit_merge_v7_itemtarget3.py"""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "merge_v7.py"
s = p.read_text(encoding="utf-8")
if "ip_selfchk" in s:
    raise SystemExit("already there")

old = """    bne a1,t0,ip_old              # a friend is the target: lane N's rule (the game's routine)
    nop
    beq t1,t3,ip_hero
"""
new = """    bne a1,t0,ip_old              # a friend is the target: lane N's rule (the game's routine)
    nop
    bne t1,t4,ip_whom             # the user picked his partner: exactly that
    nop
    beq t4,t3,ip_selfp1           # the user picked himself:
    lw t0,0x7F8(t3)               # (the user is the twin: is player 1's hero down?)
    b ip_selfchk
    nop
ip_selfp1:
    lw t0,0x7F8(t5)               # (the user is player 1's hero: is the twin down?)
ip_selfchk:
    andi t0,t0,4
    bne t0,zero,ip_old            # his partner is down: lane N's rule (the down partner gets it, as in build 21)
    nop
ip_whom:
    beq t1,t3,ip_hero
"""
assert s.count(old) == 1
s = s.replace(old, new)

old = """    beq t0,zero,if_game
    nop
    jr ra
    move v0,t1
if_game:
"""
new = """    beq t0,zero,if_game
    nop
    bne t1,t4,if_ok               # the partner was picked: drawn on him
    nop
    beq t4,t3,if_selfp1           # the user picked himself: if his partner is down, lane N's rule decides (the game's
    lw t0,0x7F8(t3)               # search)
    b if_selfchk
    nop
if_selfp1:
    lw t0,0x7F8(t5)
if_selfchk:
    andi t0,t0,4
    bne t0,zero,if_game
    nop
if_ok:
    jr ra
    move v0,t1
if_game:
"""
assert s.count(old) == 1
s = s.replace(old, new)

old = "  ih_pick (0x001BA624, was lane N's jal n_heal)"
if old in s:
    pass
p.write_text(s, encoding="utf-8", newline=chr(10))
print("ok")
