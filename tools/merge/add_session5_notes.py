"""One-off: docs/STATE.md, section "Second round on merged build 6" (the work of 2026-11-11, day).
  python -I tools/merge/add_session5_notes.py
The validation lines are added later by add_session5b_notes.py.
"""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "## Second round on merged build 6" in t:
    raise SystemExit("already there")
notes = r"""## Second round on merged build 6 (main session, 2026-11-11 day; the user: "finish all the tasks, then I test once")

All of it is in the builders (`tools\merge\merge_v6.py`, `tools\own\make_own.py`); test folders
`patches\test-v6-e` (shared screen) and `patches\test-own-v6-e` (own screens) hold the state described here.
New test helpers: `tools\own\dusk_one.sh` (one own-screen run with a probe; PROBE=<script> picks the probe),
`two_tests.sh` (two runs side by side in sandboxes run-v3 / run-v3b), `sheet.py` (contact sheet of a test's
pictures; run it WITHOUT -I, it needs PIL), `who_probe.py` (who is the engine's player / the twin, slots, party
table), `drv_probe2.py` (Drive bytes of both slots, save data, own copy, form variables), `make_kit2.py` (test
kits on any base: --magic --forms=HEX --limit --drive=N --drivemax=N --die=p1|p2|both), `rules_bits.sh`.

### 1. The hit counters of the "cannot be damaged" fights: SOLVED (seventh glue)
- How it was found: the mission files carry their own script (BAR entry type 3). `tools\lane-s1\extract_msn_ai.py`
  decodes them (OpenKH's Bdxio, run only): 293 texts in `local\analysis\lane-s1\msn`, survey
  `tools\lane-s1\survey_msn_damage.py` -> `_survey.txt`.
- TT14_MS109's script (`tt_dusk_ignore`) has a trigger OBJ_DAMAGE: it counts (trap_mission_increment_count) only
  when the attacker in the damage record (record+0x10) IS trap_sysobj_player (trap_obj_cmp = 0). The same
  handler, word for word, is in TT04_MS301 and in "ms_attackend" (AL00_MS101, BB01_MS101, CA01_MS101,
  HE06_MS101, HE19_MS204, TT08_MS701). Seifer's tutorial asks trap_sysobj_is_player, so it always counted.
- The call chain: damage code 0x001B3E64 / 0x00176400 -> 0x00186148 -> 0x00196B58 (key 6 to the 8 mission
  script places at 0x00350338) with (damaged object, damage record).
- Glue `dmg_msn` (0x000F4900, jump at 0x00186154): while the mission scripts run, a record whose attacker is the
  twin names the engine's player; then the twin again.
- VERIFIED: test i1-dusk-msn (only player 2 attacks): story scene at frame 8900 (the photo scene), where the
  final patch of build 4 showed none in 12,000 frames. The other seven missions: HYPOTHESIS (same script code).
- The earlier search result "index 25" was a wrong reading: variant 0 worked because index 1 (the getter
  0x0016B0D0, used by trap_sysobj_player) was in it. Why variants 3 and 4 worked is not known.
- The mission scripts never read a controller (no pad trap in any of the 293): the idea "rules and result screens
  use the script engine's button tests" was wrong. Those two traps are used by 7 object scripts only
  (B_EX170_LAST, B_EX370, B_EX420, F_HB090, F_MU070 ...): button-mash moves, still controller 1.

### 2. Prizes that fill a mission gauge: either hero (eighth glue; NOT tested in a game)
- Routine 0x001A5990(prize, gauge number, amount) is the step of two prize classes (called from 0x001C7EA8 and
  0x001D29A0): when the engine's player reaches the prize it is collected and the amount goes into the mission
  gauge (0x001D8D08). The twin was never asked. Glue `gprize` (0x000F4B00, jump at the routine's entry): both
  heroes are asked, every other prize the twin first.
- HYPOTHESIS: these are the morale orbs of the Land of Dragons missions (script trap_obj_scatter_prize_mu).
  Needs a jump disc to such a mission to be seen. The suites show only that nothing else broke.

### 3. Rules screens and the Game Over menu on controller 2
- Struggle rules screen: VERIFIED stuck with only controller 2 (i2-rules-p2). Bit-coded search over the getter
  calls (`tools\own\rules_bits.sh`, tests i3-rulebit0..5: match started in variants 0, 1, 2, 4 = site 23) ->
  call 0x0027DB64 in routine 0x0027DB58. Now on `pad_both`. VERIFIED: i4-rules-fix (Struggle), i5 / j5
  (Grandstander: player 2 closes the rules screen and plays; player 1 presses nothing after New Game).
- Game Over menu: VERIFIED already working from controller 2 (i8-gocont-p2: both down, player 2's Circle chose
  Continue, both heroes back, two views).
- NOT found yet: result screens at the end of a job or match (no test reached one with only controller 2).

### 4. The command menu stayed empty after a rules screen (a fault of step 7; FIXED)
- Seen in i5-grand-p2all and in the older g6-grand-lock: after a mission's rules screen both screens showed the
  menu plate without rows until player 1 pressed a button. The stock game (i6-grand-stock) and the own-screen
  build without step 7 (j1-grand-norows) show the rows.
- Reason: the display hides its whole row group (flags 0x20 and 0x40 on every row, routine 0x0013D3F8) until it
  is "revealed" (display+0xFD): by the first button press on controller 1 (0x0013C738), a Reaction Command, an
  open list, or a one-time flag (0x003484A4, set at a HUD restart, cleared soon after). Player 2's copy of the
  display state had its own +0xFD, missed the one-time flag, and so hid ALL rows (both players') every step.
- Fix: +0xFD is one state for both players (two byte copies in `own_hud`, `tools\own\make_own.py`), and the
  button test of the reveal (call 0x0013C798) is on `pad_both`. VERIFIED: j4-grand-reveal, j5-grand-reveal2.

### 5. Drive Forms for the second hero: WORK (ninth glue)
- Before: player 1's Drive worked (j2-drive-p1). Player 2's Drive ended the two-player state (i7-drive-p2: one
  view of the new body on both screens). A form change builds the new body with the constructor directly
  (0x001B6850 in the form-change routine 0x001B65E0), after the old body's end method (0x001B6810) has run the
  merged build's "a twin ends" rule.
- Glue (0x000F4C40..., `form_end`, `form_wrap`, `form_d2`, `form_slot`, `form_cur`, `form_set`, `form_zero`,
  `form_build`; variables 0x000F47E0 V_FT, 47E4 V_FT2, 47E8 V_TFORM, 47EC V_TFV). The header of
  `tools\merge\merge_v6.py` (NINTH GLUE) explains each. In short: the twin's new body takes his own marked slot,
  stays the twin and gives camera / exits / HUD owner / S back to player 1's hero; the form-change record takes
  the changing hero's own slot (the form's clock ran on player 1's slot before); the twin has his own "current
  form" number (the game has one, in the save data 0x0032F054, which stays player 1's); a new room builds the
  first-built hero (= the twin) in the twin's own form.
- My own fault on the way: the first variables sat at 0x000F47C8 / 47CC, inside the 12 bytes the first glue
  remembers at 0x000F47C4. Seen in the probe (the flag read 0x45160000). Moved.
- VERIFIED (roam disc, kit `--magic --forms=56 --limit --drive=5`): k1-drive-p2 (player 2: Drive > Limit Form:
  red outfit, FORM gauge and menu "Attack / Limit / ? / Revert" on his screen only; player 1's screen and Drive
  values unchanged; then Revert: his normal body and menu again; two views all the time), k4-formdoor (in Limit
  Form through the door to the Borough and back: he stays in the form, his form clock goes on from his own
  copy), k5-formdoor-p1 (player 1 in Limit Form through the door: he keeps it, the twin stays normal).
- Kit facts: Drive row and forms need the form flags (save + 0x36C0: 02 Valor, 04 Wisdom, 10 Final, 40 Master;
  Limit = save + 0x36CA bit 3); the kit's every-frame write of the Drive bars makes "bars 5" come back after a
  load (a kit effect, not the game's).
- OPEN: while one hero is in a form the other's "Drive" row is dim (seen both ways; which check, not examined).
  Not tested: the form's clock running out (about 80 s), Valor / Wisdom / Master / Final (they use up a helper),
  Anti Form, a save or a Game Over while the twin is in a form, the form's own Reaction Commands.
- Seen on the way: on a fresh save the menu rows "Items" and "Drive" show "?" (locked) until the save has them.

"""
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")
print("state updated")
