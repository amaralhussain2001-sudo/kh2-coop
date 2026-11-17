"""One-off: record the third part of the 2026-11-10 session in docs/STATE.md (own-screen test batch, the door fix,
package rebuilt)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "## Own screens: test batch and the door fix" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("expected one place for %r (found %d)" % (old[:60], t.count(old)))
    t = t.replace(old, new)


# pick-up section: the facts that changed
rep("""  * OWN SCREENS = `patches\\merged-v6-own` (2,683 words, SHA-1 59f86b04e7b55d4cbd4fb9b215e7bf2e8d7adb5a) = merged""",
    """  * OWN SCREENS = `patches\\merged-v6-own` (2,691 words, SHA-1 3b1cd74eee3062ac174474bc9e0d51c9bdbfcb8c; with
    the door fix of the late evening, section "Own screens: test batch and the door fix") = merged""")
rep("""- The test package in `dist\\` is BUILD 3 = OWN SCREENS (package id 35228b5c127c), with the shared-screen patch""",
    """- The test package in `dist\\` is BUILD 3 = OWN SCREENS (package id c8028c052f0a, rebuilt with the door fix),
  with the shared-screen patch""")
rep("""2. Own screens, still open: text boxes and the "Waiting for the other player." sign are on both screens;
   player 2's command menu sub-menus (Magic, Items) and the L1 shortcut list untested; the menu's open and close
   movements run twice per step; a small orange glint beside player 2's gauge in the first town; shop, journal,
   Continue after Game Over, the game's own cross-fades, a room round trip and 16:9 untested with two views; the
   2-3 step return of two views after a death or mission event; pace in busy fights (the world is drawn twice and
   player 1's picture still passes through main memory); sound listener stays with player 1's camera
   (HYPOTHESIS); START and the full-screen menus for player 2.""",
    """2. Own screens, still open, most important first:
   a. THE COMMAND MENU'S LISTS LEAK (VERIFIED, test u4-menu): when one player opens Magic, the other player's
      picture shows that list too (without a cursor) until it is closed; the page flip of the menu is shared the
      same way. The root menu's cursor and the L1 shortcut list ARE right per player. Cause: one display object
      for two players (lane V2, section 5.1). Fix = a second display object (constructor 0x0013B088, creation
      0x0013B348) or swapping the display's state around player 2's HUD run.
   b. text boxes and the "Waiting for the other player." sign are on both screens;
   c. the menu's open and close movements run twice per step; a small orange glint beside player 2's gauge in the
      first town; the 2-3 step return of two views after a death or mission event;
   d. untested with two views: shop, journal, the game's own cross-fades; sound listener (HYPOTHESIS: stays with
      player 1's camera); START and the full-screen menus for player 2.
   DONE since the first write-up: room changes through doors (the door fix), Continue after a Game Over in a
   free-roam room, 16:9, pace at normal speed in a fight at 4x, a 34,000-frame random run with the own-view
   emulator on both copies.""")
rep("""5. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission. Every mission test
   disc starts with a shortcut jump, and there Continue crashes also in the UNMODIFIED game (section "Merge 4").""",
    """5. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission. Every mission test
   disc starts with a shortcut jump, and there Continue crashes also in the UNMODIFIED game (section "Merge 4").
   Found 2026-11-10 (test c1-fightmem): the game keeps location records after "Now" (0x0032BAE0) at 0x0032BAF0,
   0x0032BB00 and 0x0032BB10 (world, room, door, a byte, three 16-bit event numbers); on a shortcut-start disc
   the one at 0x0032BB00 is all FF. A first try to fill it with a test line (`tools\\merge\\make_retrytest.py`,
   test c2-retry-stock, no mod) did NOT give a working retry: the game still went to room FFFF, about 2 s after
   a fault at pc 0x001D69EC (address 0x48C) and before any Continue press. Not understood yet.""")

notes = r"""## Own screens: test batch and the door fix (2026-11-10 late evening, after the user said tests may run)

All runs on the hidden desktop; two linked copies; own-view emulator (view12) on both unless noted;
`tools\own\run_own.sh` (snapshots show what each PC shows).

- FOUND AND FIXED: AFTER A DOOR BOTH PCs SHOWED PLAYER 1's VIEW. VERIFIED fault (u3-roundtrip first run,
  u1-long-roam first run: "whole picture from frame 5004" and never two views again; d1-doorstate: our flag
  0x000F6F04 = 1 and the layout byte 0 after the door; d2-doorflag: the game's own flag 0x0033CC44 = 0 there).
  Cause: a room change through an exit removes the scene's draw tasks, lane V1's two-view tasks included, without
  calling "remove the two-view tasks", so lane V1's flag "two views are on" stayed set and they were never asked
  for again. (Lane V1's own room changes all came after an event had already switched to one view.)
  Fix in `tools\own\fork_views.py` (step 0b): the camera task sees "our flag set, the game's flag clear", clears
  our flag and asks again. Patch `patches\merged-v6-own` is now 2,691 words, SHA-1
  3b1cd74eee3062ac174474bc9e0d51c9bdbfcb8c.
- Results on the fixed patch:
  | Test | Result |
  |---|---|
  | u3-roundtrip (both pads the same door script, 4x) | PASS: three room changes, own views again in every room (view log: two views resume after each change), 115 digests |
  | u1-long-roam (34,000 frames, random buttons on both pads, 4x, doors) | PASS: 531 digests, never out of sync; own views after the doors (pictures at 7300, 18000, 33900) |
  | u2-cont (both heroes' HP held at 1 by a test line; Game Over, Continue, several times) | PASS: Game Over menu on both PCs, Continue brings both back with own views; 249 digests |
  | u4-menu (test kit with magic; player 2 opens Magic, later holds L1; player 1 opens Magic) | in sync; root menu cursor and L1 shortcut list per player: RIGHT; an opened list shows in BOTH pictures: FAULT (pick-up list 2a) |
  | u5-169 (the package's patch file, Screen 16:9) | PASS: both pictures widescreen, own views, 79 digests |
  | u6-pace (Port Royal fight at normal speed, 4x, both copies on this PC) | PASS: 30.0 pictures and 59.9 video frames per second in the fight |
  | u7-newgame (kh2-coop-v2.iso, two Roxas, random buttons after the start) | PASS: 140 digests |
  | suite_v6.sh on the fixed patch | ALL NINE runs never out of sync, pairs identical; windows 141/0, 130/0, 113/137; one player alone as before (two early frames differ from build 5) |
- Package rebuilt with the fixed patch: package id c8028c052f0a, friend kit SHA-1
  076c9e19f33edf9ba6ba7512a46474f2b78cb82b, KH2 patch file SHA-1 34fcd75a7fef2b59df7d68f514ff3d09b9ff15c1; the
  read-me now names the list leak and says 16:9 worked in one test. Rehearsal p4-rehearsal-own through the
  launchers: join code, 9,000 frames, 140 digests, never out of sync, host "shows the final picture", friend
  "shows the copy taken at the marker", memory cards identical.
- A mistake of mine on the way: the first batch skipped three runs because `run_own.sh` shifted its arguments
  wrongly when no patch folder was given (fixed; the runs were repeated).
- Test-only patch folders left: `patches\test-own-die2` (both heroes' HP held at 1), `patches\test-own-kit`
  (skills and magic for a fresh save), `patches\test-retry-*` (the retry record try). None is for play.

"""
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")
print("state updated")
