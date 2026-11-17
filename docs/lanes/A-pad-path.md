# Lane A: how a player object gets its controller, and giving the twin controller 2

Written 2026-11-10. Disc: English-text copy build 2 (game program unchanged, CRC F266B00B). All tests SINGLE-PC,
sandbox emulator copies in `local\run-a`, scripted buttons. Twin scene = variant t1 (object 0x5A added to
`ard/tt07.ard` group `b_40`), disc `local\iso\test-t1.iso` (lane A used an identical copy, now deleted).

## Result

**WORKS (first stage).** With the patch below, player 1's controller moves and jumps only the first Roxas, and
player 2's controller moves and jumps only the second Roxas. Two linked copies stay in sync.

| Test | Setup | Result |
|---|---|---|
| a-v3-pad | 2 copies; P1 stick right 6300-6390, P2 stick up 6500-6590, P2 Cross 6700, P1 Cross 6900; positions read by PINE | VERIFIED: object 1 moved/jumped only for P1, twin only for P2; in sync; screenshots equal on both copies |
| a-camx | same + camera pointers forced to object 1 (experiment) | VERIFIED visually (`local\tests\a-camx\sheet.png`): frame 6716 the twin is in the air while object 1 stands; frame 6916 the reverse |
| a-sync-v3 | 2 copies, 30,000 frames, BOTH controllers random after reaching play, patch on | VERIFIED: 468 digests compared, never out of sync; 6 screenshots equal on both copies |

Not tested: attacks, commands, reaction commands, being hit, room change, cutscenes (this scene has no weapon,
no enemies and no open exits).

## The patch

File: `patches\lane-a-p2pad-v3\SLPM-66675_F266B00B.pnach` (made by `tools\lane-a\make_p2pad3.py <dir> pad`).
Used with the harness option `--patch-dir`. It changes game code, so every PC needs the same file (the join
check already compares the patches folder).

| Line | Meaning |
|---|---|
| `000F0000 3C0F0035` | lui t7,0x35 |
| `000F0004 8DEE2400` | lw t6,0x2400(t7): the game's pointer to the last built player object (0x00352400), 0 if none |
| `000F0008 08059FC6` | j 0x00167F18: continue into the game's "get logical controller" routine |
| `000F000C 000E202B` | sltu a0,zero,t6: controller index = 1 if a player object already exists, else 0 |
| `000F0020 8C8E0B38` | lw t6,0xB38(a0): this player object's own controller pointer |
| `000F0024 ADEE09E4` | sw t6,0x9E4(t7): shared control object S: S->pad = that pointer |
| `000F0028 08075AE8` | j 0x001D6BA0: continue into S's update (what the game did here) |
| `000F002C 01E0202D` | a0 = S (what the game passed) |
| `00178898 00000000` | was `a0 = S`; moved into the routine above |
| `001788A0 0803C008` | was `j 0x001D6BA0`; now jumps to 0x000F0020 first |
| `0017A000 0C03C000` | player factory: was `jal 0x00167F18` (index 0); now calls 0x000F0000 first |

So two things change: (A) the player factory gives the first player object logical controller 0 and any further
one logical controller 1; (B) every time a player object runs its update, it first puts ITS controller into the
shared control object, whose input copy it then reads.

## What was found (all for CRC F266B00B)

### Controller layers
| Thing | Address | Status |
|---|---|---|
| Physical pad blocks, 0x180 bytes each | pad 1 0x0034D3C0, pad 2 0x0034D540 | VERIFIED (a-in1) |
| Logical controllers, 0x60 bytes each, SAME mapping for both pads | [0] 0x0034D6C0 (from pad 1), [1] 0x0034D720 (from pad 2) | VERIFIED (a-in1): e.g. Cross = 0x08000108, Circle = 0x01000004, stick as floats at +0x30/+0x34, strength +0x3C, "pressed this frame" copy at +0x18 |
| `GetLogicalController(index)` | 0x00167F18, returns 0x0034D6C0 + index*0x60 | VERIFIED: disassembly + test a-gf (forcing it to return [1] makes pad 2 drive menus, skip and both characters) |
| Calls of that routine | 43 call sites, 42 pass index 0 | VERIFIED (`local\analysis\a\callers_getpad.txt`) |

The earlier note "pad 2 has a different re-mapped word (0x0034D722)" was a misreading: 0x0034D720 is logical
controller 1 and uses the same mapping as controller 0. The game fully supports two logical controllers.

### Player objects
| Thing | Address / value | Status |
|---|---|---|
| Player class table | 0x00352410; object size 0xB80 | VERIFIED (dump + factory code) |
| Objects in the t1 scene | first 0x01A90B00, twin 0x01AAB2F0 (position vector at object+0x70) | VERIFIED (a-in1, a-dbg1) |
| Player factory | 0x00179FD0; calls the getter at 0x0017A000, the constructor 0x001D0980 at 0x0017A054 | VERIFIED |
| Object's own controller pointer | object+0xB38 (set by base constructor 0x00177DC8) | VERIFIED |
| Pointers to the shared control object S | object+0xB3C and +0xB44 = 0x01C5F530 | VERIFIED |
| "Last built player" pointers | 0x00352400 (set at 0x001D09CC, cleared by 0x001D0CE8 when a player object is destroyed) and 0x0034E948 | VERIFIED statically; a-dbg1 shows the 2nd construction sees the 1st object there |
| Unit slot | object+0x48C = 0x01C6C750 for BOTH objects; slot+0x25C points back to the last built object | VERIFIED: both player objects share unit slot 1 (so HP/MP are shared today) |

### The shared control object S (0x01C5F530, class table 0x00351260)
This is the command-menu controller. VERIFIED facts:
- Each player object's update calls player method 0x00178888, which calls S's update (0x001D6BA0 -> 0x001BD6A8).
  With two player objects, S's update runs twice per frame.
- S's update reads S->pad (S+0x9E4 = 0x01C5FF14) and copies the stick to S+0xA30..0xA3C and button results to
  flags in S. Normal ground movement (0x001784A8) reads the stick copy S+0xA30, not the pad.
- S->player (S+0x9E0) and S->pad are set when the FIRST player object is attached (0x001D6938 -> 0x001BDF38);
  later attaches only replace S->player. That is why both Roxas followed pad 1.
- Proof by experiment: changing only 0x01C5FF14 to logical controller 1 made BOTH objects follow pad 2 (a-b-ptr3).

## What did NOT work (kept for the record)
| Test | Idea | Result |
|---|---|---|
| a-ptr1 / a-b-ptr1, a-b-ptr2 | change object+0xB38 of the twin (or of the first object) after it is built | FAILED: no effect, both follow pad 1 (the object's own pointer is not used for normal movement) |
| a-p2pad-v1, a-p2pad-v2 | only build the twin with logical controller 1 | FAILED: twin's pointer is controller 1 (checked, a-v1chk) but both still follow pad 1, because of S |
| a-b-s10 | switch only the call at 0x001594A0 | no effect (camera code) |
| a-v4-* (keep1, keep2, keep2slot, keep2s, keep2cam) | after the twin is built, restore 0x00352400, 0x0034E948, slot back pointer, S->player/S+0xAF4, or call 0x0013DDC0(0, first) | control still correct and in sync, but the camera STILL follows the twin (pictures byte-identical to v3) |

Bit-coded search over the 42 call sites (tests a-b-bit0..5, a-b-s14) showed the only call that decides player
control is the factory call at 0x0017A000.

## Open problems (for Phase 1 planning)
1. **Commands and attacks are untested.** S is one object: one command menu, one cursor, one S->player. In the
   delivered variant S->player stays the last attached object (the twin). A second variant
   (`make_p2pad3.py <dir> padplayer`, tests a-v3-padplayer, also correct and in sync for move/jump) sets
   S->player = the updating object too. Which is right for attacks needs a scene with a weapon. HYPOTHESIS: a real
   "P2 exactly like P1" needs a second S (own command menu state) for player 2.
2. **Camera follows the second-built player object.** VERIFIED (a-camx, experiment with fixed heap values): the
   camera follows the object stored at 0x00348638 and 0x00348754; forcing both to the first object makes the
   camera follow player 1. The code that sets them (0x0013DDxx, 0x00140DB8) is not understood yet; a one-time call
   of 0x0013DDC0(0, first) did not change the picture.
3. **Shared unit slot.** Both player objects use unit slot 1 (shared HP/MP/stats). Separate HP for player 2 needs
   its own slot (constructor argument "character id", object+0xB50).
4. **Rule "a player already exists -> controller 2".** Depends on 0x00352400 being 0 when the first object of a
   room is built. Statically the destructor clears it; a room change with the patch is NOT tested.
5. **Memory for the routines.** 0x000F0000-0x000F002F was zero in three dumps of one scene. HYPOTHESIS that the
   game never uses it; to check over long play (or move the code into slack inside the program).
6. **S's update now runs with a different controller on each call.** Menu handling inside it therefore sees
   player 1's buttons on one call and player 2's on the other. Effects on the command menu are untested.
7. Other controller users (camera stick, pause, 41 other call sites) still read controller 1 only.
8. Other creation paths: 0x001B6850 builds a player object with a controller pointer copied from an existing
   object (`lw a3,0xB38(t7)`); special player classes (object ids 0x35B, 0x35C, 0x35D, 0x3BE, 0x3C8, 0x5F5) go
   through the same factory call, so rule A applies to them too. None tested.

## How to repeat
```
python -I tools\kh2_session.py make 2 --run-dir run-a
python -I tools\lane-a\sep_run.py a-v3-pad patches\lane-a-p2pad-v3 run-a 28450 28021 local\iso\test-t1.iso
```
(prints for each object which controller moved it and whether the session stayed in sync).

## Tools added (all under `tools\lane-a\`)
- `elfscan.py`, `callers.py`, `mips.py`: scan/disassemble the game program without Ghidra; small assembler.
- `ghidra\LaneADump.java` + `gh.sh`: decompile chosen functions from the Ghidra project `local\ghidra` (kh2a).
  Ghidra is started by calling Java directly; its .bat launcher fails on paths with spaces/parentheses.
  The Emotion Engine extension already in the user's Ghidra settings is used (language r5900:LE:32:default).
- `pine_ranges.py`: read memory ranges / full memory at chosen frames through PINE (read-only).
- `sep_run.py`: the "who controls whom" test. `bisect.py`: experiment patches for the getter call sites.
- `make_p2pad3.py` (delivered patch), `make_p2pad.py`, `make_p2pad4.py`, `make_dbg.py` (experiments).
- Experiment patches: `local\patches-a\`. Decompiled text: `local\analysis\a\`.

Harness note: appending results from several parallel runs to ONE file loses lines on this system; use one
result file per run.
