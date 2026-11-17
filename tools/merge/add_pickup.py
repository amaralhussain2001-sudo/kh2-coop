"""One-off: put a "PICK UP HERE" section at the top of docs/STATE.md (for a fresh chat)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
old = "# Project state (handoff)\n"
assert t.startswith(old)
if "## PICK UP HERE" in t:
    raise SystemExit("already there")
head = r"""# Project state (handoff)

## PICK UP HERE (written 2026-11-10, before the chat was cleared)

Read this section first, then `..\KH2-COOP-PLAN.md` (plan, rules, all user decisions) and
`REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in `docs\lanes\`.
The parity checklist is `docs\PARITY-CHECKLIST.md`.

Where things stand:
- Newest tested build: patch `patches\merged-v3` (SHA-1 ea1ad99792b5e94ae33e4ad3a918a31e8e757b7b) on disc
  `local\iso\kh2-coop-v1.iso` (English build 3, twin in every room). All combined tests passed on one PC
  (section "Merge 3"). No humans have played anything yet.
- The test package in `dist\` still holds the OLDER patch merged-v2.
- No lane (agent) is running. The user said: do NOT open extra lanes. Work one job at a time in the main session
  until the user asks for parallel lanes again.

Waiting for the user's answers (asked three times, not answered yet):
1. Boss HP +75 %: (A) add lane B75's small gauge patch so every boss gets the full +75 % (recommended), or (B) cap
   boss HP at 3400 (the game's HP gauge freezes above 3400)?
2. Pete in the collapsing cave (90 s limit): +40 % instead of +75 %?
The user may also say "test now without the boss HP".

Next jobs, in order:
1. With the answers: build the disc with boss HP (`tools\lane-b75\`, see `docs\lanes\B75-boss-hp.md`), add the
   gauge patch lines if A (check them against lane V2's HUD hooks), make merged-v4, repeat the suite
   (`tools\merge\suite_v3.sh <patchDir>`), then rebuild the test package for the first two-human test: copy
   lane T's `tools\lane-t\make_test_package.py` and its kit README (they point at merged-v2 and list the old
   known problems), make a new disc patch with `tools\lane-t\make_disc_patch.py`, and tell the user the steps.
2. Small fix the user noticed: player 2's gauge always shows its rings while the game hides player 1's in the
   opening town; they should hide together (lane V2's gauge code, `docs\lanes\V2-hud-per-player.md`).
3. Own screens (the user chose them: full-size views, nothing cut): join lane V1's patch
   (`patches\lane-v1-two-views`), lane V2's per-view HUD and lane V3's emulator exe
   (`emulator-src\builds\view10`). Open problems: player 1's 3D stays at native sharpness when the emulator
   upscales (lane V3 suggests a copy that stays inside the graphics chip); pressing START freezes the view;
   per-player HUD only partly done; a new emulator exe means a new package for both players.
4. Still missing for "player 2 exactly like player 1": helpers go with both heroes; HP orbs for the twin; a menu
   and prompts on screen for player 2; START and menus for player 2; boss moves written against "the player";
   Twilight Thorn and the other carried-hero Reaction Commands (the user wants BOTH heroes in the move).
5. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order (done so far: Twilight Town
   prologue, Gummi Ship study, special-mode "second copy" checks).

Working habits that matter here: plain English, short sentences, lettered options with a recommendation; every
claim VERIFIED or HYPOTHESIS; never touch the original disc file, `Desktop\PS2-ONLINE`, `Desktop\openkh` or
`Desktop\New folder\digimon-online`; use absolute paths in shell commands; never put backslashes into inline
heredoc Python (write script files instead, like this one); tests run minimised.

---
"""
p.write_text(head + t[len(old):], encoding="utf-8")
print("pick-up section written")
