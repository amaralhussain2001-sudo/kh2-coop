# Lane T: the test package for two humans

Written 2026-11-10. Goal: let the user and their friend try the current combined build (merged-v2 patch +
`kh2-coop-v1.iso`) online on two PCs, without touching the user's working `Desktop\PS2-ONLINE` folder.
All tests here: SINGLE-PC, bots on the controllers, no humans. Labels: VERIFIED (test id / hash) or HYPOTHESIS.

## Result in short

**Built and rehearsed.** A separate test folder, a disc maker that turns each player's own original disc file into
the two-player disc, a check that refuses two different disc files, a README, and a zip for the friend.
Nothing was written into `Desktop\PS2-ONLINE`: its patches folder still holds only the Digimon patch, its
package id is still 9e49d3f8243e, its MY-GAMES is unchanged, and the original disc file still has SHA-1
81c177a374e1bddf8453c8c96493d4e715a19236 (re-checked after the disc maker ran).

## What was built (all under `Desktop\New folder (3)\dist\`)

| Item | What | Size / check |
|---|---|---|
| `PS2-ONLINE-KH2-TEST\` | The test folder for THIS PC. Program files copied from the real package; the user's own BIOS and controller settings (`inis\PCSX2.ini`) copied in; EMPTY `MY-GAMES (never share)`; NO memory card; own `package-id.txt` | 195 MB, package id **ffcae04be01d** ("PS2 Online KH2 TEST package ...") |
| `PS2-ONLINE-KH2-TEST\MAKE-KH2-DISC\` | `MAKE-KH2-DISC.bat` + `Make-KH2-Disc.ps1` (Windows PowerShell 5.1, nothing to install) + `kh2-coop-v1.kh2patch` | patch 28,945,400 bytes (118 runs, 14,133 changed sectors), SHA-1 6f2c1940483b82c7d4f1aab8cc0e174234bdc99a |
| `KH2-TEST-FRIEND-KIT.zip` | What the friend unzips into a COPY of their own PS2-ONLINE folder | 22.4 MB, SHA-1 88efb0ed736db2470fcd5f15ca20de6761c8bc44 |
| `HOW-TO-SET-UP (FRIEND).txt` | The friend's steps (also inside the zip) | |

### What differs from the real package
- `emulator\pcsx2-qtx64.exe` and `link\ps2net-link.exe`: **identical** to the real package (SHA-1 59ef3b11...f34d
  and a8375cad...55b2). The emulator was not rebuilt.
- `emulator\patches\`: the Digimon patch (unchanged) plus `SLPM-66675_F266B00B.pnach` = the merged-v2 lines
  (the builder checks they are exactly `patches\merged-v2`) + the official `[Widescreen 16:9]` group for this disc
  copied from the package's own `patches.zip` (14 lines, switched on only when the host picks 16:9). Source file:
  `patches\lane-t-kh2test\`, SHA-1 9c9b96bf23efdb5011b7da0d81153a39ee3aa954.
- `launcher\Launcher.ps1`: a modified copy (SHA-1 4ac5b5b75eda5e04a847bb817f6b8f842c388bda), see below.
- New: `START-KH2-TEST.bat`, `1-READ-ME-FIRST (KH2 TEST).txt`, `PS2-ONLINE general help.txt` (the real package's
  README, for connection help), `MAKE-KH2-DISC\`, `my-settings.txt` with the defaults "2 players, no multitap",
  Screen 4:3, Game = the two-player disc (name, picture and connection choices taken from the user's settings).

### Launcher changes (made by `tools\lane-t\make_test_package.py`, exact text replacements, each must match once)
1. Window title "PS2 Online - KH2 two-player TEST"; default layout "2 players, no multitap", default screen 4:3.
2. `Game-Check`: SHA-1 of the whole game file, computed once per file (remembered in `game-file-checks.txt` by
   name, size and change time).
3. Join-code tag: was layout + flags + file size (8 bytes); now also the first 8 bytes of the game file's SHA-1
   (16 bytes, the helper's limit). The friend's launcher picks the file with the same size AND the same check.
4. `game-file-check.pnach`: before every start the launcher writes the game file's full SHA-1 into this small
   file in `emulator\patches`. It is not a patch. The emulator already compares a hash of every `.pnach` file
   in that folder at the join (`PatchFilesHash` in PS2Net.cpp: file names + contents), so two different game
   files are refused by the emulator itself, also when joining by IP.
5. The status box also shows "Game file check: XXXX-XXXX-XXXX-XXXX", and everything the window says is appended
   to `logs\<date>-launcher.txt`.
6. After a refused join, late helper messages are ignored (the refusal stays the last line).
7. Test-only: `-Test ip:<address>`, and extra session lines from the file named in `PS2ONLINE_TEST_EXTRA` (read
   only when `-Test` is used; used by the rehearsal bots).

### The friend kit (zip contents)
`HOW-TO-SET-UP (FRIEND).txt`, `START-KH2-TEST.bat`, `1-READ-ME-FIRST (KH2 TEST).txt`,
`PS2-ONLINE general help.txt`, `package-id.txt`, `launcher\Launcher.ps1`, `link\ps2net-link.exe`,
`emulator\pcsx2-qtx64.exe`, `emulator\patches\SLPM-66675_F266B00B.pnach`,
`emulator\patches\SLUS-21067_568A5C78.pnach`, `MAKE-KH2-DISC\` (bat, ps1, patch).
The builder refuses to make the zip if it holds a disc image, a BIOS file, a memory card or anything from
MY-GAMES. VERIFIED: none of those is inside.
Note: the disc patch holds the changed sectors (English text and the room data with the second hero). It is for
the friend, who owns the same disc; it should not be posted publicly.

## Tests

| ID | Setup | Result |
|---|---|---|
| t2-ws169-roam | sandbox, 2 linked copies, the package's KH2 patch file, Screen 16:9, free-roam disc, random buttons on both pads, 20,000 frames | VERIFIED: 312 digests, never out of sync, 4 of 4 screenshot pairs identical; the 16:9 picture looks right by eye |
| t2-ws43-roam | same patch file, Screen 4:3 | VERIFIED: 312 digests, never out of sync, 4 of 4 identical |
| disc maker | run inside a copy of the test folder on the user's original disc file | VERIFIED: result byte-identical to `local\iso\kh2-coop-v1.iso` (`cmp`), SHA-1 a60c8ab94399f276725591bff1d97f6c8e5d6887; the original file unchanged |
| disc maker, wrong input | another game (other size); a file of the same size with other content | VERIFIED: both refused with a clear text ("not the expected disc file", sizes or check numbers shown); nothing written |
| disc maker, .bat | path with spaces and brackets handed to the .bat as a dragged file | VERIFIED: the path reaches the script |
| friend path | copy of the real package without games + unzip the kit + delete the memory card | VERIFIED: all 260 program files identical to the test folder; only leftovers of the normal package are extra (its README, update note and START bat) |
| t2-rehearsal-kh2 | two copies of the test folder, started through their launchers (Host a game -> join code -> Join), earlier launcher build, 16,000 frames at normal speed | VERIFIED: connected by join code, 249 digests, never out of sync, 7 of 7 screenshot pairs identical, both memory cards identical afterwards |
| **t2-final-kh2** | host = copy of the test folder, friend = folder made the friend's way INCLUDING the disc made by the disc maker there; 9,000 frames | VERIFIED: 140 digests, never out of sync, 6 of 6 identical. Both controllers act: at frame 6340 player 1's Roxas has run ahead while the twin still stands; at 6540 the twin has left its spot (moved from the second copy's controller); at 6912 player 1's Roxas jumps (`local\tests\t2-rehearsal-kh2\A\sheet.png`; the same frames are byte-identical in all three rehearsals) |
| **t2-final-digimon** | Digimon Rumble Arena 2 from the same two copies, multitap layout, 16:9, 5,000 frames | VERIFIED: 78 digests, never out of sync, 3 of 3 identical; settings fingerprint c78843b300d13f3d, the same as in the user's real Digimon sessions |
| t2-mismatch-code, -code2 | host has the two-player disc, friend has another file of the same size, join by code | VERIFIED: the friend's launcher says "Your game file has the right size but NOT the same content as the host's (host: A60C-8AB9-4399-F276, yours: 1882-7338-0710-FF0A)..." and no emulator starts |
| t2-mismatch-ip | same, join by IP | VERIFIED: the host's game log says "refused ... Different patch files in the emulator's patches folder", the friend's says "the host refused us" |
| t2-final2-kh2 | the FINAL launcher (SHA-1 4ac5b5b7...), 8,000 frames | VERIFIED: 124 digests, never out of sync, 6 of 6 identical; no process left running |

After the last test only texts changed (README, package id); the final launcher file is byte-identical to the
one rehearsed.

## What the same-file check covers

- **Join by code:** the friend's launcher compares size and 8 bytes of the SHA-1 of the whole file and refuses
  with a clear message. VERIFIED.
- **Join by IP (or any other way through the launcher):** the emulator's own join check refuses, because the
  full SHA-1 sits in the patches folder that it compares. VERIFIED. The text it shows is the emulator's fixed
  "Different patch files in the emulator's patches folder" (it cannot be changed without rebuilding the emulator;
  the README explains it).
- **The right disc, not only the same disc:** the disc maker checks the SHA-1 of the input and of the result.
- NOT covered: starting the emulator by hand without the launcher (the check file is then stale); a file changed
  in place with the same name, size and change time (the remembered check would be reused); the normal package
  (only this test folder has the check).
- HYPOTHESIS (read from the code, not run): a player with the normal launcher and one with the test launcher
  cannot join each other by code (the tag lengths differ; each side says "another package").

## Memory card rule in the test folder

No card is shipped. At the first start the emulator makes a new empty card, the same on both PCs (hash
eec1891f7a9b71c5 in every log). VERIFIED after a session: both cards byte-identical. The friend deletes the card
in their COPY (step 3 of their how-to). The first save asks to format (the corrected English text). If
"Different memory card" appears: both delete the card, or the host sends the one card file (test saves only).

## Exact steps for the user

1. Open `Desktop\New folder (3)\dist\PS2-ONLINE-KH2-TEST\MAKE-KH2-DISC`, double-click `MAKE-KH2-DISC.bat`, choose
   the original disc file in `Desktop\PS2-ONLINE\MY-GAMES (never share)`. About 3 minutes; it writes a new
   4.3 GB file into the TEST folder's MY-GAMES and must end with OK and a60c8ab94399f276725591bff1d97f6c8e5d6887.
2. Send `dist\KH2-TEST-FRIEND-KIT.zip` (22.4 MB) to the friend. The friend follows `HOW-TO-SET-UP (FRIEND).txt`
   (copy their PS2-ONLINE folder, unzip into the copy, delete the copy's memory card, make the disc).
3. Close the normal PS2-ONLINE. Start `START-KH2-TEST.bat`, host as usual. Windows may ask about the firewall
   again for the new folder.
4. Both read `1-READ-ME-FIRST (KH2 TEST).txt`: buttons, what works, the known problems, what to send back
   (the `logs` folders of both PCs).
The test folder can be moved (for example to the Desktop) as a whole.

## Honest limits

- Everything above is one PC with bots. No LAN, no internet, no humans. The connection parts (join code, reply
  code, firewall) are the unchanged helper and emulator, but a new folder means a new firewall question.
- Default Screen is 4:3 because the user asked to keep the game as the original; 16:9 passed one sync test and
  is the host's choice. The widescreen lines are a community camera change.
- The friend's steps assume their normal folder is the same package as the user's (9e49d3f8243e). The kit
  replaces the emulator exe, the link helper and the launcher anyway; other program files (Qt, resources) come
  from the friend's copy. If their package is older, they should update it first.
- The first hours of the game (Roxas) are full of special activities that were never tried with two heroes, and
  the build still has the known problems listed in `docs\lanes\M-merge.md` (enemies attack only player 1's hero,
  either hero at 0 HP is Game Over, no gauge or menu for player 2, camera on player 1, narrow doors). Two humans
  may get stuck early. That is what the test is for; the README says so.
- The join-code tag now uses all 16 bytes the helper allows; nothing more can be added to it.

## Files of this lane

- Tools `tools\lane-t\`: `make_disc_patch.py`, `make_test_package.py` (`--rebuild` keeps the folder's MY-GAMES and
  logs), `rehearse.py`, `mismatch.py`, `kit\` (README, friend how-to, disc maker).
- Scripts `tests\scripts\lane-t\`. Patch source `patches\lane-t-kh2test\`.
- Test results `local\tests\t2-*` (the copied connection logs contain network addresses of this PC; they stay
  local). `local\lane-t\` holds the disc patch and run outputs.
- Deleted: the throw-away rehearsal copies (`local\kit-test-t`, about 16 GB). Left in place: `local\run-t`.
- Not edited: the shared tools, other lanes' folders, `STATE.md`, the plan, the requirement and checklist files,
  memory. Nothing was sent anywhere; the helper asked a public STUN server for this PC's address during the
  rehearsals, as it does in every normal session.
