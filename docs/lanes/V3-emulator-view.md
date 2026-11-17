# Lane V3: the emulator shows each PC only its own player's view

Status 2026-11-10: DONE for the emulator side. **Full-size own views work end to end** with lane V1's
"two full pictures" patch (layout 2): each PC shows its own player's full-size picture, the game stays in sync,
nothing in the emulated PS2 changes. Side-by-side halves (layout 1) work too. Alternate video frames (layout 3)
work in the emulator but no game patch produces them yet.

Everything below was tested on ONE PC with two emulator copies and scripted or random buttons. Nothing was tested
over a real network or with two people. Labels: VERIFIED = measured in a named test; HYPOTHESIS = reasoned, not
measured.

| What | Where |
|---|---|
| New emulator exe | `emulator-src\builds\view10\pcsx2-qtx64.exe` (14,925,312 bytes, SHA-256 `8FB06E70D920CAAB789D696569596B042C61BF5E214DFA0AD63D28FAE00802FB`) |
| The change as a patch file | `emulator-src\patches\ownview.patch` (against the digimon-online emulator source; 8 files, 632 lines added, 9 removed; SHA-256 `c13889d6…e0d9`) |
| The same change as a script | `tools\lane-v3\apply_ownview_patch.py` |
| Settings file for this game | `patches\lane-v3-view\SLPM-66675_F266B00B.view` |
| Pictures | `local\tests\v3-mk7-cmp\`, `v3-mk6-cmp\`, `v3-acc-cmp\`, `v3-mk9-cmp\` |

---

## FOR LANE V1 (read this first)

Your patch `lane-v1-c` (frozen copy used here: `patches\lane-v3-v1c-copy`, SHA-1 `8c1896e1bff0…`) works with the
new exe and this settings file:

```
LayoutAddress = 000F6F00
MarkerValue = 2
MarkerId = 56310002
MarkerPlayer = 2
MarkerBuffer = display
MarkerHold = 0
```

VERIFIED (v3-fin2-l2view, v3-mk7-1x): player 1's PC shows player 1's full picture, player 2's PC shows player 2's
full picture, each with the whole HUD; 81 digests, never out of sync.

What I found that is yours to look at:

1. **Player 1's 3D picture stays at the PS2's own resolution when a PC uses a sharper picture setting.**
   VERIFIED (v3-mk7-4x, `local\tests\v3-mk7-cmp\sheet_detail_4x.png`): at 4x, player 2's picture is as sharp as
   the one-view game at 4x (edge strength ratio 1.00), player 1's is not (0.81; it looks like the 1x picture
   with a sharp HUD). At 1x both are equal to the one-view game (0.99 to 1.01). Your listing says why: player 1's
   picture is read back to main memory and loaded again. A copy that stays inside the graphics chip (drawing the
   draw buffer into the second buffer as a texture) would keep it sharp.
2. **While the layout byte is 0 after START, both PCs show player 2's view, frozen, and no menu.**
   VERIFIED as seen (v3-mk9-d0, script `tests\scripts\lane-v3\p1_menu.txt`, frames 5405 to 5625;
   `local\tests\v3-mk9-cmp\sheet_menu_open.png`, `sheet_menu_close.png`). With `lane-v1-a` the same script opened
   the pause menu. Cause not looked into.
3. **The layout byte and the picture it describes arrive together.** VERIFIED (v3-mk9-d0 against v3-mk9-d1): with
   no delay each PC has the right picture on the first two-view frame after a one-view period; with a delay of one
   video frame player 2's PC shows player 1's picture for one frame. Keep writing the byte where you write it now.
4. The marker is caught wherever it comes after your first display copy and before the second, because
   `MarkerBuffer = display` copies the frame buffer that is on display (base 0x00000), not the one FRAME names.
   One marker per two-view step, none in other steps: that is what your patch does, and what the emulator needs.
5. Side by side (`lane-v1-a`): when the pause menu opens or closes, the byte is already 0 while the scene behind
   the fading menu is still drawn as two squeezed halves, for about 20 video frames
   (`local\tests\v3-v1a-view\sheet_p1_open.png`, `sheet_p1_close.png`). The emulator shows what the byte says.

If you ever build alternate video frames (layout 3), the emulator needs one more byte, the OWNER byte: 0 = the
picture on display now is player 1's, 1 = player 2's, any other value = everybody's. Write it in the same place and
at the same moment as the layout byte. Facts that help (seen in the emulator's log during the marker tests on
the plain game): the game shows one frame buffer at base 0x00000 (512 x 448) and fills it with one draw, the
first or second draw of a video frame, in about every video frame; the scene is drawn elsewhere (base 0x01B00).
So alternating means: in one video frame copy player 1's finished picture to the display, in the next one
player 2's.

## FOR LANE V2

In layout 2 each player's picture already carries the whole HUD (lane V1 draws it into both pictures), so nothing
is cut and no HUD split is needed there. It is the same HUD in both pictures (`local\tests\v3-mk6-cmp\sheet_f4600.png`).
In layout 1 the HUD is drawn once across both halves, so each player sees half of it at double width.

## FOR THE MAIN LANE AND LANE T

- **What to ship:** replace `emulator\pcsx2-qtx64.exe` and add `emulator\patches\SLPM-66675_F266B00B.view` next
  to the game's `.pnach`. Nothing else. Both change the package id (it is a hash of the program files), so make a
  new package for both players.
- **Both players need the new exe.** The new exe can still play with the old one (protocol 4 unchanged;
  VERIFIED v3-fin2-l1mix, v3-fin2-l2mix, v3-fin2-dgmix: never out of sync), but a PC with the old exe does not
  get its own view: with layout 2 it shows player 1's picture, with layout 1 both halves.
- **The `.view` file is not part of the patch check** between the PCs (that check hashes `*.pnach` only). A PC
  without it simply shows the unchanged picture.
- **The launcher needs no change.** Optional session keys: `View = off` (this PC shows the unchanged picture),
  `View = N` (show player N's view, for tests), `SnapView = 1` (test snapshots show what this PC shows).
- **Both PCs must use the same picture quality (upscale) for this game, or the sync check gives a false alarm.**
  VERIFIED, and it is not caused by my change (the package's own exe does the same, v3-c1): the game reads
  pictures back into main memory. In the plain game only 0x00464780-0x004E6380 differs (after the first pause or
  skip screen); in two-view mode only 0x00457584-0x004F3580, every step (v3-u1-exact, v3-u2-exact). Everything
  else in memory is identical. With equal upscale there is no alarm.
- **Layout 2 needs a hardware renderer** (tests ran on Direct3D 12, the automatic choice on this PC). The
  renderer is already part of the settings check, so both PCs use the same kind.
- **Other games are not affected.** Without a `.view` file for the running game nothing is switched on. Digimon
  Rumble Arena 2: new exe and package exe in one session, 140 digests in sync, pictures byte-identical on both
  (v3-fin2-dgmix).
- Observation, not checked further: the "memory card" value in the lobby line was the same before and after a
  Digimon save was written to the test copies' card. If it is meant to cover the card's contents, it does not.
  The leftover save shifted later test runs by a couple of video frames (same on both copies, so no sync effect).

---

## Which layout is the most robust from the emulator's side

| | Layout 2: full-size, marker | Layout 3: full-size, alternate video frames | Layout 1: side-by-side halves |
|---|---|---|---|
| State | Works end to end with lane V1's patch | Emulator part works; no game patch yet | Works end to end |
| What the game must give | Layout byte = 2; both finished pictures copied to the display one after the other, a LABEL write between them | Layout byte = 3; an owner byte; the two pictures on alternating video frames | Layout byte = 1; which part is whose |
| What the emulator does | At the marker, copies the frame buffer on display; that player's PC shows the copy, the other PC the final picture | Shows a video frame only on its owner's PC and holds the previous picture on the other; the deinterlacer is bypassed | Shows this PC's part stretched over the normal picture area |
| Picture size per player | Full | Full | Half the columns |
| Same as the one-view picture | Yes (measured, see below) | Yes for what was measured (unchanged pictures equal the truth) | Framing yes; sharpness 0.86 to 0.89; HUD cut in half |
| Renderer | Hardware only | Any (software not tested) | Any (software not tested) |
| Cost on the PC | One full-picture copy per step on one PC | One full-picture copy per own video frame | None |
| Weak point | Depends on the hardware renderer finding the display buffer at the marker; one PC's picture is a copy | Player 2's picture is one video frame (17 ms) later; needs the game to alternate exactly | Half sharpness, HUD needs splitting |

My ranking: **layout 2 is the one to use now**, because it is the only full-size layout proven with the real game
patch, and both players get their picture in the same video frame. Layout 3 is the simplest in the emulator and
does not depend on the renderer, so it is the fallback if layout 2 misbehaves in some scene. Layout 1 stays as the
proven last resort.

## Acceptance: does each player's picture match the one-player game?

Method: same disc and same button scripts (`test-m-roam.iso`, `tests\scripts\lane-k\a_p1.txt`, `a_p2.txt`), once
with the merged base in one view (reference), once with two views; `tools\lane-v3\register.py` matches edge
profiles and reports zoom per axis, shift, aspect and edge strength. Player 2's reference is the one-view game
with the camera aimed at the twin (`patches\lane-v3-ref-twincam`, a reference aid only).

**Layout 2, full-size (lane V1's patch `lane-v1-c`):** pictures `local\tests\v3-mk7-cmp\sheet_p1.png`,
`sheet_p2.png`, `sheet_detail_4x.png`, and `local\tests\v3-mk6-cmp\sheet_f4600.png`.

| Compared | Zoom across / down | Shift | Aspect | Sharpness (view / reference) |
|---|---|---|---|---|
| Player 1, 1x, frame 4600 | 1.000 / 1.000 | 0.0 px | 1.000 | 0.99 |
| Player 1, 1x, frame 5100 | 1.000 / 0.994 | 0.5 px | 1.006 | 1.01 |
| Player 2, 1x, frame 4600 | 1.000 / 1.004 | 1.5 px | 0.996 | 1.00 |
| Player 2, 1x, frame 4900 | 1.000 / 1.000 | 0.0 px | 1.000 | 1.00 |
| Player 1, 4x, frame 4600 | 1.000 / 1.004 | 0.5 px | 0.996 | **0.81** (lane V1, point 1 above) |
| Player 2, 4x, frame 4900 | 1.000 / 1.000 | 0.0 px | 1.000 | 1.00 |

Plainly: same zoom, same field of view, same viewpoint, circles stay circles, nothing cut, whole HUD. The one
difference is player 1's 3D sharpness on a PC with a sharper picture setting, and that is removable on the game
side.

**Layout 1, halves (lane V1's patch `lane-v1-b`):** pictures `local\tests\v3-acc-cmp\sheet.png`.
Zoom 1.000 to 1.002 across and 0.994 to 1.000 down, shift at most 1.5 px, aspect 0.998 to 1.006. Sharpness 0.86
to 0.89 of the one-view picture at 1x and 0.87 at 4x; a view at 4x is about as sharp as the one-view game at 1x
(1.04). What differs: half the columns per player, and the HUD is drawn once across both halves so each player
sees half of it at double width. The emulator cannot render only wider; the lever is the general upscale.

## What was changed in the emulator

Display only. The change adds nothing to the emulated machine and writes nothing into it.

- New `pcsx2/GS/GSPresentView.h`: the small state "what this PC shows".
- `pcsx2/PS2Net/PS2Net.cpp/.h`: reads the `.view` file when a session starts; once per video frame, just before
  the finished picture is handed to the graphics thread, reads the layout byte (and owner byte) and passes the
  result along in order, so it applies to exactly that picture. Session keys `View`, `SnapView`, and the
  test-only `DumpFrames`.
- `pcsx2/Counters.cpp`: the one call that does the above.
- `pcsx2/GS/Renderers/Common/GSRenderer.cpp`: layout 1 narrows the source rectangle after the screen rectangle
  was computed from the whole picture; layout 3 keeps a copy of this PC's last picture and skips the deinterlacer;
  snapshots keep the unchanged picture unless asked otherwise.
- `pcsx2/GS/GSState.cpp`, `pcsx2/GS/Renderers/HW/GSRendererHW.cpp/.h`: a write to the LABEL register (0x62, until
  now ignored by the graphics thread) with the configured id makes a copy of the frame buffer; the output of
  that frame buffer is replaced by the copy on the PC that shows it.

Why it cannot affect sync: the only reads are the two bytes and the video mode register; the copies live in the
PC's graphics card. The LABEL register still goes to its old handler. VERIFIED by mixed sessions with the
package exe (above; in them the package exe's PC shows byte-identical pictures wherever both show the whole
picture) and by default snapshots being byte-identical to runs without any settings file (v3-alt-truth against
v3-mk5-full, v3-alt2-truth against v3-alt2-full).

Two things fixed on the way: player 2's PC showed a stale picture in layout 3 because the emulator skipped
repeated frames (fixed, v3-alt-view); player 2's PC showed player 1's picture for the first two-view step after
every one-view period in layout 2, because the marker arrives before the layout value (fixed, v3-mk9-old against
v3-mk9-d0).

## How to build

Build tools found on this PC (Visual Studio 18 Build Tools); nothing was installed.

```
git -C emulator-src\pcsx2 checkout -- pcsx2          (back to the digimon-online state; its changes are staged)
del emulator-src\pcsx2\pcsx2\GS\GSPresentView.h
git -C emulator-src\pcsx2 apply ..\patches\ownview.patch
powershell -NoProfile -ExecutionPolicy Bypass -File emulator-src\build.ps1 -Log emulator-src\logs\build.log
```

Result: `emulator-src\pcsx2\bin\pcsx2-qtx64.exe`. A full build takes about 2 minutes, a rebuild after a change
about 1. The patch file and the script give the same source (VERIFIED by hash). `emulator-src` is 3.9 GB, of
which 2.3 GB is `pcsx2\build` (build leftovers; can be deleted, the next build is then a full one).

An unchanged rebuild behaves like the package exe: VERIFIED v3-same01 (one of each in a session, 12,000 frames,
187 digests in sync, screenshots identical). `emulator-src\builds\unchanged\` holds it.

## The settings file

`<patches folder>\<SERIAL>_<CRC>.view`, plain text, `;` or `#` starts a comment. The emulator holds no
game-specific numbers.

| Key | Default | Meaning |
|---|---|---|
| `LayoutAddress` | 0 | Address (hex) of the game's layout byte. 0 = none, `TestLayout` is used. |
| `SideValue` (also `ViewsValue`) | 1 | Byte value for layout 1. |
| `Player1` … `Player4` | none | Layout 1: left top right bottom of that player's part, as fractions of the picture. |
| `MarkerValue` | 2 | Byte value for layout 2. |
| `MarkerId` | 0 | Layout 2: low 32 bits (hex) of the LABEL write. 0 = layout 2 off. |
| `MarkerPlayer` | 1 | Layout 2: the player whose picture is complete when the marker comes. |
| `MarkerBuffer` | `frame` | Layout 2: what is copied: `frame` = the buffer being drawn to, `display` = the buffer on display. |
| `MarkerHold` | 8 | Layout 2: video frames a copy is shown without a new marker; 0 = until the next marker. |
| `AlternateValue` | 3 | Byte value for layout 3. |
| `OwnerAddress` | 0 | Layout 3: address (hex) of the owner byte. 0 = even/odd session frames (tests only). |
| `LayoutDelay` | 0 | Video frames (0 to 3) by which the game writes the bytes before the picture is on display. KH2: 0. |
| `TestLayout`, `MarkerTestDraws`, `MarkerTestEvery` | | Tests only. |

Layout 2 handles two views (one marker). Layouts 1 and 3 are written for up to four players; only two were tested.

## Snapshots

Default: test snapshots are the unchanged picture, the same on every PC (VERIFIED for all three layouts:
v3-k1-full, v3-alt2-full, v3-fin2-l2full). With `SnapView = 1` they show what that PC shows. In layout 2 a
default snapshot makes the marker PC show the final picture for up to two video frames; that happens only when a
test asks for snapshots.

Reading the logs: a snapshot file named frame N shows the picture presented one video frame after the frame number
in the `view:` log lines.

## Tests

All with `tools\lane-v3\v3_session.py`, results under `local\tests\<name>`. "In sync" = every digest compared,
never out of sync.

| Test | What | Result |
|---|---|---|
| v3-same01 | Unchanged rebuild with the package exe, KH2, 12,000 frames | In sync (187), screenshots identical |
| v3-fin2-l2view | Layout 2, real patch, final build on both, own views | In sync (81); each PC its own full picture |
| v3-fin2-l2full | Same, default snapshots | In sync; snapshots identical on both PCs = final picture |
| v3-fin2-l2mix | Same, final build with the package exe | In sync (81); the old exe shows player 1's picture |
| v3-mk7-1x, v3-mk7-4x | Layout 2 at 1x and 4x for the measurements | In sync (81 each) |
| v3-mk9-d0, -d1, -old | Layout 2 around a switch to one view and back | No wrong frame with the final build and no delay |
| v3-mk5-view, -full | Layout 2 with a pretend marker, plain game | Marker PC shows the held copy; default snapshots = truth |
| v3-fin2-l3, v3-alt-view, -full, -truth | Layout 3, pretend owner, plain game | In sync (99); own frames shown, held in between; snapshots = truth |
| v3-alt2-view, -full, -truth | Layout 3, pretend owner, in play (Merlin's house) | In sync (80); same; snapshots = truth at 10 frames |
| v3-fin2-l1mix, v3-v1a-view | Layout 1 with lane V1's first patch and the layout byte | In sync (92); own half, whole picture while the menu is open |
| v3-k1-view, -full | Layout 1 with lane K's demo | Own half per PC; default snapshots whole |
| v3-m1-mix, v3-m2-opts, v3-m3-169 | Old exe as friend; `View = 2`, `View = off`; 16:9 | In sync; options do what they say; view fills the 16:9 area |
| v3-fin2-dgmix, v3-dg-new, -pkg, -mix | Digimon Rumble Arena 2, new and package exe | In sync (140); pictures identical on both PCs |
| v3-acc-ref, -ref2, -p1view, -p2view | Layout 1 acceptance measurements | Numbers above |
| v3-q-1x4x, v3-q-2x8x, v3-q-raw | Layout 1 at 1x, 2x, 4x, 8x | Views are drawn at the chosen resolution (`v3-q-cmp\sheet.png`) |
| v3-c1 … c4, v3-u1-exact, v3-u2-exact | Different upscale per PC | False "out of sync", package exe too; only picture buffers differ |

Earlier runs of the same scenario are not always byte-identical to today's (v3-v1a-view against v3-fin-l1: the
game runs two video frames apart). The test copies' memory card had gained a Digimon save in between (VERIFIED it
is there; that it is the cause is a HYPOTHESIS). Runs made today repeat exactly.

## Not done, not tested

- No test with two PCs, a real network or people.
- Layout 3 with a real game patch (none exists). Its deinterlacer bypass was checked in two scenes by comparing
  unchanged snapshots with the truth: Market Street (the game was in frame mode) and Merlin's house (field mode
  was logged there in other runs of the same scene).
- Software renderer, and hardware back ends other than Direct3D 12.
- Layout 2 above 4x upscale; layouts with more than two players.
- The path that redraws the picture while the session waits for the network handles layouts 1 and 3 in code but
  was not provoked in a test (HYPOTHESIS that it is right). Video recording was not looked at.
- The test copies' memory cards (`local\run-v3`) still hold the Digimon save.

## Files of this lane

- `emulator-src\` : source copy, `build.ps1`, `builds\view10` (final), `builds\unchanged`,
  `package-exe-original.exe` (the package's exe, for mixed tests), `patches\ownview.patch`, `logs\`.
- `tools\lane-v3\` : `apply_ownview_patch.py`, `v3_session.py` (test harness), `register.py`, `png2raw.ps1`,
  `crop.ps1`, `sheet.ps1` (picture comparison), `ramdiff.py`, `dump2.py` (memory comparison).
- `patches\lane-v3-view\` : the settings file to ship. `patches\lane-v3-view-test-*`, `lane-v3-view-always`,
  `lane-v3-view-v1c-d1` : test settings. `patches\lane-v3-v1a-copy`, `-v1b-copy`, `-v1c-copy` : frozen copies of
  lane V1's patches used in the tests. `patches\lane-v3-ref-twincam` : reference aid.
- `tests\scripts\lane-v3\p1_menu.txt`. Test copies: `local\run-v3`, `local\run-v3b`.
