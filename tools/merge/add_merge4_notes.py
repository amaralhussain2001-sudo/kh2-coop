"""One-off: record merge 4 in docs/STATE.md (pick-up list renumbered + section "Merge 4")."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "## Merge 4 (main session" in t:
    raise SystemExit("already there")

old = r"""4. Still missing for "player 2 exactly like player 1": helpers go with both heroes; HP orbs for the twin; a menu
   and prompts on screen for player 2; START and menus for player 2; boss moves written against "the player";
   Twilight Thorn and the other carried-hero Reaction Commands (the user wants BOTH heroes in the move).
5. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order (done so far: Twilight Town
   prologue, Gummi Ship study, special-mode "second copy" checks).
"""
new = r"""3. Still missing for "player 2 exactly like player 1": helpers go with both heroes; HP orbs for the twin; a menu
   and prompts on screen for player 2; START and menus for player 2; boss moves written against "the player";
   Twilight Thorn and the other carried-hero Reaction Commands (the user wants BOTH heroes in the move); the
   Drive bar (question above).
4. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order (done so far: Twilight Town
   prologue, Gummi Ship study, special-mode "second copy" checks).
5. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission. Every mission test
   disc starts with a shortcut jump, and there Continue crashes also in the UNMODIFIED game (section "Merge 4").
   Continue in a free-roam room works. First thing to watch in the human test.

How to repeat merge 4: `python -I tools\merge\merge_v4.py` (patch), `python -I tools\merge\build_disc_v2.py
kh2-coop-v2.iso` (disc), `bash tools/merge/suite_v4.sh` (suite, log `local\m4-suite.log`),
`bash tools/merge/brun.sh ...` (boss checks), `python -I tools\lane-t\make_disc_patch.py <original> <disc>
local\package\kh2-coop-v2.kh2patch`, `python -I tools\package\make_test_package.py --rebuild`,
`python -I tools\package\rehearse.py ...` (needs two copies of the test folder in `local\kit-test-t\A` and `B`).
"""
assert t.count(old) == 1, "pick-up list not found"
t = t.replace(old, new)

merge4 = r"""## Merge 4 (main session, 2026-11-10 evening): boss HP, gauge patch, no 1P/2P signs, new test package

User answers: boss HP limit = A (gauge patch); Pete in the cave = 40 %. During the work the user also asked to
hide the "1P / 2P" signs over the heroes' heads.

- Patch: `tools\merge\merge_v4.py` -> `patches\merged-v4` (with `listing.txt`), 1,403 words, SHA-1
  5bd158ae8621e49fddd55396adc7ed18f22c045d = merged-v3 (1,529) - the markers (176 words at
  0x000F7240-0x000F74FC removed; hooks 0x0013D9E0, 0x0013DB50, 0x0013DBA8 back to lane V2's gauge-alone routines;
  the result holds exactly lane V2's `patches\lane-v2-p2gauge` form) + lane B75's 50 gauge words (cave
  0x000F3800-0x000F38AF, data word 0x000F3FF0, hooks 0x00154450, 0x00154B98, 0x00154C10).
  Checked by the tool: no address in common; the three hook pairs match the game program.
  VERIFIED by search of the game program: the three gauge routines are entered only from the gauge's own start
  (0x00154B40) and from the two lock-on wrappers (0x0019D3B8, 0x0019D3F8); nothing in merged-v3 calls them; the
  detour clamps the shown HP to 3400 on every path, so two lock-ons sharing the one gauge cannot run past its
  16 bars. `--markers` keeps the signs (that form passed the same suite: `local\m4-suite-with-markers.log`).
- Disc: `tools\merge\build_disc_v2.py kh2-coop-v2.iso` -> `local\iso\kh2-coop-v2.iso`, SHA-1
  12edc56fdb0baac302c373e554185921242e6533 = kh2-coop-v1's recipe + `00battle.bin` from lane B75's tool
  (`--percent 75 --gauge-patch`; row 26 of `tools\lane-b75\data\boss_entries.csv` now carries 40: Pete at
  Olympus, both his missions). 86 entries raised, 5 left alone, battle file SHA-1
  f3d63f098d5c8bb14851f541fa575590d1376a05. VERIFIED: it differs from kh2-coop-v1.iso only in 5 sectors (the
  packed battle file). THIS DISC MUST NEVER BE PLAYED WITH A PATCH WITHOUT THE GAUGE WORDS (merged-v3 or older).
- Suite `tools\merge\suite_v4.sh` (log `local\m4-suite.log`, results `local\tests\m4-*`): ALL NINE runs never
  out of sync, every screenshot pair identical, same numbers as merge 3 (attack windows 146/0, 130/0, 113/137);
  the New Game run uses kh2-coop-v2.iso (16,000 frames); one player alone: four pictures byte-identical to
  merged build 3.
- Boss checks on the final patch (`tools\merge\brun.sh`, two linked copies, read-only watcher):
  | Test | Result |
  |---|---|
  | m4-b-pete (jump HE 116, "Defeat Pete before the cave collapses!") | VERIFIED: Pete 168/168 at battle level 1 (original 120, +75 % would be 210) = +40 %. 140 digests, never out of sync, 12 of 12 picture pairs identical. The 90 s clock runs; both Soras, Donald, Goofy and Hercules fight. |
  | m4-b-shanyu (jump MU 75; run with the with-markers form) | VERIFIED: Shan-Yu 455/455, falcon 105/105 (x1.75); in sync until the mission failed (the script does not guard the gate). |
  | m4-b-threshbig-sync (test disc: Thresholder 3570 HP, Scan test line, both pads lock on and attack) | VERIFIED: 118 digests, never out of sync, 7 of 7 pairs identical, no fault in the emulator log; the gauge with 16 small bars is drawn and drains (3570 -> 2557); player 2's small gauge is there; no 1P/2P signs (`local\tests\m4-b-threshbig-sync\sheet.png`). |
- FOUND AND EXPLAINED: "Continue crashes on mission test discs". After the failed Shan-Yu mission the scripted
  Circle chose Continue, the room value became FFFF and the game stopped (first fault pc 0x001AEBF0, a table
  indexed by the world number). VERIFIED the UNMODIFIED game does exactly the same on the same kind of disc
  (m4-b-shanyu-stock: no patch, no twin, original boss HP; same fault). So it is an effect of the shortcut start
  (no place to go back to), not of the mod. It is also what lane B75 saw on the Lingering Will disc (same pc)
  and very likely lane V2's freeze on `test-m-fight.iso` after frame 7150. NOT shown yet: Continue inside a
  mission that was entered the normal way (job 5 in the pick-up list).
- Test package rebuilt: `tools\package\make_test_package.py --rebuild` (copy of lane T's tool with new sources;
  kit texts in `tools\package\kit`), patch source `patches\test-package-v2` (merged-v4 lines + the official
  widescreen group), disc patch `local\package\kh2-coop-v2.kh2patch` (28,955,648 bytes, 119 runs, 14,138
  sectors, SHA-1 dd0a2cfb38a70ad178accc4252867f7c26e43201). Result in `dist\`: package id 6aee5665abe7, disc
  name "Kingdom Hearts II - Final Mix (2 Players TEST v2).iso", friend kit SHA-1
  ef9dbe19bb0fa4f1c71fd79c2c79b4a531ce559d (22.4 MB, no disc image, BIOS or memory card), launcher
  byte-identical to lane T's rehearsed one (SHA-1 4ac5b5b7...).
  VERIFIED (p2-rehearsal-kh2): the disc maker inside a copy of the package turns the original disc into exactly
  kh2-coop-v2.iso (12edc56f...); two copies joined through their launchers with a join code; 9,000 frames,
  140 digests, never out of sync, 6 of 6 picture pairs identical, both memory cards identical afterwards.
  The real package was only read (id still 9e49d3f8243e, its patches folder holds only the Digimon patch); the
  original disc file still has SHA-1 81c177a374e1bddf8453c8c96493d4e715a19236.
- Seen in the rehearsal pictures: player 2's small gauge shows its rings while player 1's gauge shows only the
  face (the known small fault, next job).
- Deleted again: the test discs of this merge (test-v2-*.iso, test-b75-threshbig.iso) and the rehearsal copies
  (`local\kit-test-t`); their recipes are in `local\variants\v2-*`.

"""
old2 = "## Open items\n"
assert t.count(old2) == 1, "open items heading not found"
t = t.replace(old2, merge4 + old2)
p.write_text(t, encoding="utf-8")
print("merge 4 recorded")
