# Lane C: the bench list

Every place in the game's own data where a twin of the player character needs special care.
Made on 2026-11-10 from the extracted original Japanese disc (SLPM-66675), without running the emulator.

## Summary

- **Rooms:** 289 room files in 18 worlds; 5535 script programs, 3879 spawn groups, 18947 placed entities.
- **Solo places:** 187 script programs in 44 rooms set `Party NO_FRIEND` (the player is alone). 889 programs set a party value at all; the other 4646 do not mention the party.
- **Where the player is placed:** 1249 player placements (PLAYER placeholder, object 0x0236) in 284 rooms. 303 of them have no friend placeholder beside them, 2 have only one. The data never places two players at once.
- **Special player forms:** 56 objects are of type PLAYER: 50 real ones (characters, Drive Forms, vehicles and special modes), 1 without player stats and 5 markers. The party table (MEMT) has 37 rows that choose the player object per world; 7 player objects are also placed directly by room data.
- **Missions:** 303 mission files, 309 mission names used by room scripts. 138 are flagged as minigame or special mode by name; 178 carry a timer, counter or gauge; 14 switch Drive off; 11 allow the Mickey rescue.

### What stands out for the twin

1. **The data never puts two players in a room.** Every placement is one PLAYER placeholder, usually with two friend placeholders about 141 units away (median). The twin always needs our own placement rule; the friend spacing is a ready model for it.
2. **Solo play is concentrated in Twilight Town:** 142 of the 187 `NO_FRIEND` programs are there (28 rooms). The other worlds have 45 between them.
3. **Whole worlds have no friend placeholders at all:** es End of Sea (1), di Destiny Islands (5), po 100 Acre Wood (45), lm Atlantica (15) (number of placements in brackets). In those worlds nothing in the data ever stands beside the player.
4. **One room uses the real Sora object as the placement:** nm07, group `b_99` (section 3d). A cheap test there shows how the engine treats a real player object in room data.
5. **The party table carries two size fields per world** (section 3b), possibly memory budgets for player and friends.
6. **Which friends a Drive Form or Summon uses up is not in the data tables** (section 5). It has to be found in the game program.
7. **11 missions allow the Mickey rescue:** AL03_MS103, BB05_MS104A, BB05_MS104B, BB11_MS102, BB15_MS203, CA18_MS202, EH24_MS110, HE07_MS103, HE18_MS108, MU08_MS204, MU09_MS108. The flag's meaning ("Mickey spawnable") is from the OpenKH format notes. HYPOTHESIS: these are the fights where the game already lets somebody else take over when Sora falls, a ready pattern for "player 2 saves player 1".

Labels: **VERIFIED** = read directly from the file named. **HYPOTHESIS** = my reading of what the data means; not tested in the game.

Full lists behind every table: `local\analysis\lane-c\out\*.csv`. Script: `tools\lane-c\mine.py`. Tool that reads the game files: `tools\lane-c\LaneC` (uses the OpenKH libraries).

## 0. Worlds overview

VERIFIED: room files `ard\*.ard`; world names from the OpenKH source (`Constants.cs`). Room names: the game's place table (`00place.bin`) gives each room a Japanese name; the system message with that Japanese text was found and the English text of the same message id is shown. 206 of 289 rooms get a name this way; the rest are left blank (rooms past the end of the place table, or rooms whose table name is only a working title).

| World | Name | Rooms | Rooms with a solo program | Solo programs | Player placements | ...without friend placeholders | Missions |
|---|---|---|---|---|---|---|---|
| es | End of Sea | 2 | 0 | 0 | 1 | 1 | 0 |
| tt | Twilight Town | 42 | 28 | 142 | 246 | 38 | 65 |
| di | Destiny Islands | 3 | 0 | 0 | 5 | 5 | 0 |
| hb | Hollow Bastion | 41 | 4 | 12 | 171 | 27 | 32 |
| bb | Beast's Castle | 16 | 0 | 0 | 66 | 4 | 12 |
| he | Olympus Coliseum | 20 | 2 | 7 | 100 | 20 | 64 |
| al | Agrabah | 16 | 0 | 0 | 77 | 21 | 21 |
| mu | The Land of Dragons | 13 | 2 | 6 | 71 | 5 | 16 |
| po | 100 Acre Wood | 11 | 0 | 0 | 45 | 45 | 16 |
| lk | Pride Lands | 17 | 0 | 0 | 52 | 10 | 5 |
| lm | Atlantica | 11 | 0 | 0 | 15 | 15 | 12 |
| dc | Disney Castle | 8 | 2 | 6 | 32 | 8 | 5 |
| wi | Timeless River | 9 | 0 | 0 | 48 | 12 | 8 |
| nm | Halloween Town | 11 | 0 | 0 | 56 | 11 | 12 |
| wm | World Map | 1 | 0 | 0 | 0 | 0 | 1 |
| ca | Port Royal | 26 | 0 | 0 | 90 | 23 | 20 |
| tr | Space Paranoids | 12 | 1 | 2 | 62 | 23 | 12 |
| eh | World That Never Was | 30 | 5 | 12 | 112 | 35 | 16 |

## 1. Where the game changes the party

VERIFIED: `Party` commands in the room scripts (`ard\*.ard`). The six names are the ones the OpenKH script decompiler prints; a seventh, `DONALD_ONLY`, exists in its list but is never used on this disc.

| Party value | Programs | In which script | Meaning (HYPOTHESIS, from the name) |
|---|---|---|---|
| `DEFAULT` | 406 | btl 83, evt 323 | normal party |
| `W_FRIEND` | 238 | btl 87, evt 151 | the world's guest can be in the party |
| `NO_FRIEND` | 187 | btl 90, evt 97 | the player is alone |
| `W_FRIEND_FIX` | 44 | btl 22, evt 22 | the guest is in the party and cannot be taken out |
| `W_FRIEND_ONLY` | 8 | btl 8 | only the guest fights beside the player |
| `W_FRIEND_IN` | 6 | evt 6 | the guest is put in the party |

What this means for a twin: in every `NO_FRIEND` program the original game has one fighter on screen, so the twin has to be added there by our own rule; nothing in the data places a second character.

### 1a. Solo programs (`Party NO_FRIEND`) per world

Program ids are the numbers the room scripts are selected by (the three event ids in memory). A mission name is shown when the same program starts one.

**tt Twilight Town** (142 programs in 28 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| tt00 | The Empty Realm | 1 | 0x33 |
| tt01 | Roxas's Room | 10 | 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D |
| tt02 | The Usual Spot | 10 | 0x02 (TT02_MS201), 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0xA7 |
| tt03 | Back Alley | 7 | 0x01, 0x02, 0x03, 0x49 (TT03_MS601), 0x4A, 0x4B, 0xB4 (TT03_MS400) |
| tt04 | Sandlot | 11 | 0x4C (TT04_MS106), 0x4D (TT04_MS107), 0x4E (TT04_MS108), 0x4F (TT04_MS301), 0x51, 0x52, 0x53, 0xB5 (TT04_MS500), 0xB6 (TT04_MS00), 0xB7 (TT04_MS01), 0xB8 (TT04_MS02) |
| tt05 | Sandlot | 11 | 0x01, 0x02, 0x03, 0x04, 0x05, 0x54 (TT05_MS401), 0x55 (TT05_MS402), 0x56 (TT05_MS403), 0x57 (TT05_MS404), 0x58 (TT05_MS405), 0xBD (TT05_MS401) |
| tt06 | Market Street: Station Heights | 13 | 0x01, 0x02, 0x0D, 0x59 (TT06_WORK_BAGGAGE), 0x5A (TT06_WORK_PERFORM), 0x5B (TT06_WORK_LETTER), 0xA8, 0xBE (TT06_BAGGAGE_01), 0xBF (TT06_PERFORM_01), 0xC0 (TT06_LETTER_01), 0xC1 (TT06_BAGGAGE_02), 0xC2 (TT06_PERFORM_02), 0xC3 (TT06_LETTER_02) |
| tt07 | Market Street: Tram Common | 17 | 0x01, 0x03, 0x04, 0x0D, 0x5F (TT07_MS101), 0x61 (TT07_MS103), 0x63 (TT07_MS105), 0x64 (TT07_WORK_CLEAN), 0x65 (TT07_WORK_WORM), 0x66 (TT07_WORK_POSTER), 0x6A, 0xC4 (TT07_CLEAN_01), 0xC5 (TT07_WORM_01), 0xC6 (TT07_POSTER_01), 0xC7 (TT07_CLEAN_02), 0xC8 (TT07_WORM_02), 0xC9 (TT07_POSTER_02) |
| tt08 | Station Plaza | 13 | 0x01, 0x02, 0x0C, 0x0D, 0x0E, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x73, 0xD1 |
| tt09 | Central Station | 3 | 0x01, 0x0C, 0x75 |
| tt10 | Sunset Terrace | 3 | 0x78 (TT10_WORK_TIMBER), 0x79 (TT10_WORK_MIRROR), 0x7A |
| tt11 | Sunset Station | 1 | 0x7C |
| tt12 | Sunset Hill | 2 | 0x01, 0x7D (TT12_WORK_BOX) |
| tt13 | The Woods | 2 | 0x01, 0x7E |
| tt14 | The Old Mansion | 6 | 0x01, 0x02, 0x03, 0x7F (TT14_MS109), 0x80 (TT14_MS110), 0x82 |
| tt16 | Mansion: Dining Room | 1 | 0x83 |
| tt17 | Mansion: Library | 1 | 0x01 |
| tt18 | Mansion: The White Room | 3 | 0x01, 0x84, 0x85 |
| tt19 | Mansion: Basement Hall | 5 | 0x01, 0x02, 0x86 (TT19_MS602), 0x87, 0x88 |
| tt20 | Mansion: Basement Hall | 3 | 0x89 (TT20_MS603), 0xD3, 0xD5 (TT20_MS603_RE) |
| tt21 | Mansion: Computer Room | 8 | 0x01, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F, 0x90 |
| tt22 | Mansion: Basement Corridor | 1 | 0x01 |
| tt23 | Mansion: Pod Room | 3 | 0x01, 0x02, 0x92 |
| tt24 |  | 1 | 0x94 |
| tt32 | Station of Serenity | 2 | 0x9A (TT32_MS302), 0x9B (TT32_MS303) |
| tt34 | Station of Awakening | 2 | 0x01, 0x9D (TT34_MS304) |
| tt36 | Tunnelway | 1 | 0x9F (TT36_WORK_FIGURE) |
| tt40 | Betwixt and Between | 1 | 0xA1 (TT40_MS003) |

**hb Hollow Bastion** (12 programs in 4 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| hb01 | The Dark Depths | 1 | 0x4B (HB01_MS601) |
| hb08 | Bailey | 2 | 0x34 (HB08_MS102), 0x5B (HB08_MS102) |
| hb16 | Ravine Trail | 8 | 0x3E (HB16_MS404A), 0x3F (HB16_MS404B), 0x40 (HB16_MS404C), 0x41 (HB16_MS404D), 0x57 (HB16_MS404A), 0x58 (HB16_MS404B), 0x59 (HB16_MS404C), 0x5A (HB16_MS404D) |
| hb17 | The Great Maw | 1 | 0x42 (HB17_MS405) |

**he Olympus Coliseum** (7 programs in 2 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| he00 | The Coliseum | 3 | 0x8C (HE00_MS104A), 0x8D (HE00_MS104B), 0xAE (HE00_MS104A) |
| he09 | The Underdrome | 4 | 0xBE (HE_COLOSSEUM_2 +2 more), 0xBF (HE_COLOSSEUM_3), 0xC2 (HE_COLOSSEUM_6 +2 more), 0xC3 (HE_COLOSSEUM_7) |

**mu The Land of Dragons** (6 programs in 2 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| mu07 | Summit | 5 | 0x19, 0x49 (MU07_MS106), 0x4C (MU07_MS201), 0x63 (TEST_MU07_MS999), 0x6A (MU07_MS201) |
| mu08 | Imperial Square | 1 | 0x68 (MU08_MS107) |

**dc Disney Castle** (6 programs in 2 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| dc00 | Audience Chamber | 4 | 0x01, 0x33 (DC00_MS101), 0x40 (DC00_MS101), 0x42 (DC00_MS101) |
| dc02 | Colonnade | 2 | 0x01, 0x02 |

**tr Space Paranoids** (2 programs in 1 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| tr02 | Game Grid | 2 | 0x3D (TR02_MS102A), 0x3E (TR02_MS102B) |

**eh World That Never Was** (12 programs in 5 rooms)

| Room | Name | Count | Programs (mission) |
|---|---|---|---|
| eh14 |  | 3 | 0x3A (EH14_MS103), 0x65 (EH14_MS103), 0x6F |
| eh19 |  | 3 | 0x3B (EH19_MS105), 0x61 (EH19_MS105), 0x67 |
| eh21 |  | 3 | 0x41 (EH21_MS101), 0x63 (EH21_MS101), 0x71 |
| eh22 | Station of Awakening | 2 | 0x48 (EH22_MS111), 0x5A (TEST_EH22_MS111) |
| eh24 |  | 1 | 0x50 |

### 1b. The rarer party values

`W_FRIEND_ONLY` (8 programs): eh20: 0x4A (EH20_MS113), 0x62 (EH20_MS113_RE); eh23: 0x4C, 0x51, 0x49 (EH23_MS112); he07 (Cave of the Dead: Entrance): 0x72 (HE07_MS103); lk15: 0x3B (LK15_MS202); mu05 (Village Cave): 0x48 (MU05_MS105)

`W_FRIEND_FIX` (44 programs): bb05 (Ballroom): 0x51 (BB05_MS104B); ca03 (The Interceptor): 0x38 (CA03_MS106); ca04 (The Interceptor: Ship's Hold): 0x03; ca08 (Isla de Muerta: Rock Face): 0x03; ca10 (Isla de Muerta: Treasure Heap): 0x3C (CA10_MS107), 0x02; ca21: 0x03 (SHIP_BATTLE); ca22: 0x03 (SHIP_BATTLE); he04 (Coliseum Foyer): 0x01; he05 (Valley of the Dead): 0x6F (HE05_MS102), 0x03, 0x6F; he06 (Hades' Chamber): 0x42; he07 (Cave of the Dead: Entrance): 0x01; he10 (Cave of the Dead: Inner Chamber): 0x03, 0x04; lk01 (Stone Hollow): 0x0A; lk04 (The Savannah): 0x03; lk05 (Elephant Graveyard): 0x39 (LK05_MS201), 0x0A; lk14 (Scar's Darkness): 0x37 (LK14_MS103); mu01 (Encampment): 0x46 (MU01_MS103C), 0x43 (MU01_MS101), 0x66 (MU01_MS103C), 0x44 (MU01_MS102), 0x64 (MU01_MS103C), 0x0A, 0x0C, 0x01, 0x0E, 0x07; mu02 (Checkpoint): 0x45 (MU02_MS103A), 0x50 (MU02_MS103B); mu03 (Mountain Trail): 0x1A, 0x47 (MU03_MS104), 0x01; mu04 (Village): 0x01; mu05 (Village Cave): 0x01; mu12 (Village): 0x01; tr02 (Game Grid): 0x48 (TR02_MS102A), 0x49 (TR02_MS102A), 0x4A (TR02_MS102_FREE); tr09 (Central Computer Core): 0x4C, 0x40 (TR09_MS205)

`W_FRIEND_IN` (6 programs): bb15 (Bridge): 0x63; eh10: 0x6C; eh14: 0x70; eh15: 0x6E; eh20: 0x6A; eh21: 0x72

### 1c. Other party-related commands

- VERIFIED: `SetMember` appears 81 times in event scripts, with values 0 (9x), 1 (35x), 2 (9x), 3 (18x), 4 (7x), 5 (2x), 6 (1x). The party table has exactly 7 line-ups (section 3c), numbered 0 to 6. HYPOTHESIS: `SetMember n` selects line-up n.
  - `SetMember 0`: dc01, he00, mu07, tt03, tt11, tt32, tt40
  - `SetMember 1`: bb04, ca25, dc01, dc04, eh01, hb01, hb03, hb10, he00, he03, lk00, tr00, tt04, tt06, tt07, tt23, tt27
  - `SetMember 2`: al14, mu08, mu09
  - `SetMember 3`: al00, al15, bb03, bb04, ca01, ca24, eh16, he13, lk09, mu07, mu12, nm01, nm04, tr00
  - `SetMember 4`: ca04, he06, lk02, lk12, lk13, mu00, mu05
  - `SetMember 5`: eh19, lk15
  - `SetMember 6`: hb04
- VERIFIED: `SetPartyMenu` appears 2408 times: value 0 2367x, value 1 38x, value 2 3x. HYPOTHESIS: it controls whether the party can be changed in the menu.

## 2. Where the game places the player and the friends

VERIFIED: spawn data in `ard\*.ard`. The player is placed by a placeholder entity, object 0x0236 (model name `PLAYER`); the two friends by 0x0237 (`FRIEND_1`) and 0x0238 (`FRIEND_2`). The twin test in `docs\STATE.md` used exactly such a spawn point (room tt07, group `b_40`).

- 1249 player placements (PLAYER placeholder entities) exist, in 1142 spawn points, in 753 spawn groups, in 284 of 289 rooms.
- One spawn point often holds several placements, one per way into the room: each placeholder carries an argument number, and the friend placeholders that belong to it carry the same number (example: room al15, group `m_00`, arguments 99 and 21). The counts below match friends to the player by that number.
- 944 placements have both friend placeholders, 2 have one, 303 have none.
- No spawn point has two PLAYER placeholders with the same type and argument. So the data never places two players at once; a twin always needs our own placement rule.
- Spawn type of the player placeholder: type 0: 211, type 1: 1038. HYPOTHESIS: type 1 with an argument is "arrive through entrance number N"; type 0 is a fixed start position for a fight or an event.
- Distance between the player placeholder and a friend placeholder (ground plane, game units, 1890 pairs): smallest 94, median 141, 90 % below 180, largest 269. Lane A's twin was placed 150 units beside the player. HYPOTHESIS: the friend placeholders' spacing is a safe model for placing the twin.
- 5 rooms have no PLAYER placeholder at all: al08, al14, es01, po10, wm00. HYPOTHESIS: these are cutscene-only rooms, menus or rooms where the player object is placed another way.

### 2a. Per world

| World | Name | Rooms | Player placements | With both friends | With one friend | With no friend |
|---|---|---|---|---|---|---|
| es | End of Sea | 1 | 1 | 0 | 0 | 1 |
| tt | Twilight Town | 42 | 246 | 208 | 0 | 38 |
| di | Destiny Islands | 3 | 5 | 0 | 0 | 5 |
| hb | Hollow Bastion | 41 | 171 | 144 | 0 | 27 |
| bb | Beast's Castle | 16 | 66 | 62 | 0 | 4 |
| he | Olympus Coliseum | 20 | 100 | 80 | 0 | 20 |
| al | Agrabah | 14 | 77 | 56 | 0 | 21 |
| mu | The Land of Dragons | 13 | 71 | 66 | 0 | 5 |
| po | 100 Acre Wood | 10 | 45 | 0 | 0 | 45 |
| lk | Pride Lands | 17 | 52 | 42 | 0 | 10 |
| lm | Atlantica | 11 | 15 | 0 | 0 | 15 |
| dc | Disney Castle | 8 | 32 | 24 | 0 | 8 |
| wi | Timeless River | 9 | 48 | 36 | 0 | 12 |
| nm | Halloween Town | 11 | 56 | 45 | 0 | 11 |
| ca | Port Royal | 26 | 90 | 67 | 0 | 23 |
| tr | Space Paranoids | 12 | 62 | 39 | 0 | 23 |
| eh | World That Never Was | 30 | 112 | 75 | 2 | 35 |

### 2b. How the party value and the placements go together

VERIFIED: for every script program that sets a party value, the spawn groups that same program loads were checked for player placements.

| Party value | Programs | ...that load a player placement with friend placeholders | ...that load a player placement without friends | ...that load no player placement |
|---|---|---|---|---|
| `DEFAULT` | 406 | 142 | 9 | 255 |
| `W_FRIEND` | 238 | 87 | 4 | 147 |
| `NO_FRIEND` | 187 | 81 | 17 | 89 |
| `W_FRIEND_FIX` | 44 | 30 | 0 | 14 |
| `W_FRIEND_ONLY` | 8 | 5 | 3 | 0 |
| `W_FRIEND_IN` | 6 | 0 | 0 | 6 |

Reading (HYPOTHESIS): a program that loads no player placement keeps the party where the room's entrance placement (map script) put it.

### 2c. Player placements with no friend placeholder

These are the places where the twin has no existing pattern to copy. Written as room (name): group x count. Full rows: `player_placements.csv`.

**es End of Sea** (1 placements in 1 rooms): es00: m_00

**tt Twilight Town** (38 placements in 13 rooms): tt00 (The Empty Realm): m_00; tt01 (Roxas's Room): m_00; tt07 (Market Street: Tram Common): s_99; tt09 (Central Station): e_50, m_01 x6; tt14 (The Old Mansion): e_50 x2, m_01 x2; tt15 (Mansion: Foyer): m_01 x4; tt21 (Mansion: Computer Room): e_50 x2, m_01 x3; tt25 (The Tower): e_50, m_01 x2; tt26 (Tower: Entryway): m_01 x3; tt27 (Tower: Sorcerer's Loft): e_50, m_01 x3; tt32 (Station of Serenity): m_00 x2; tt33 (Station of Calling): m_00; tt34 (Station of Awakening): b_40, m_00

**di Destiny Islands** (5 placements in 3 rooms): di00 (Destiny Islands): m_00, m_01; di01: m_00, m_01; di02: m_00

**hb Hollow Bastion** (27 placements in 7 rooms): hb03 (Crystal Fissure): e_50, m_01 x3; hb05 (Ansem's Study): e_50, e_55, m_01 x3; hb06 (Postern): e_52, m_01 x4; hb08 (Bailey): b_40; hb09 (Borough): s_99; hb13 (Merlin's House): e_50, m_01 x2; hb16 (Ravine Trail): b_40, b_41, b_42, b_43, b_45, b_46, b_47, b_48

**bb Beast's Castle** (4 placements in 2 rooms): bb08 (The West Hall): b_10, e_52; bb12 (Secret Passage): e_50, m_01

**he Olympus Coliseum** (20 placements in 6 rooms): he00 (The Coliseum): e_50, e_51, m_01; he02 (Coliseum Gates): b_4a; he03 (Underworld Entrance): e_50, m_01 x5; he09 (The Underdrome): b_z5; he10 (Cave of the Dead: Inner Chamber): e_50, m_01 x4; he12 (The Lock): e_50, m_01 x3

**al Agrabah** (21 placements in 7 rooms): al00 (Agrabah): m_01 x5, s_99; al02 (The Peddler's Shop): e_50, m_01 x2; al04 (Vault): m_00; al05 (Above Agrabah): m_00; al06 (Palace Walls): m_01 x4; al11 (Ruined Chamber): m_01 x2; al15 (The Peddler's Shop): e_50, m_01 x3

**mu The Land of Dragons** (5 placements in 2 rooms): mu07 (Summit): b_60; mu12 (Village): m_01 x4

**po 100 Acre Wood** (45 placements in 10 rooms): po00: e_50 x6, m_00 x8; po01 (Starry Hill): b_40, e_50, m_00, r_20, r_21; po02 (Pooh Bear's House): e_50 x2, m_00; po03 (Rabbit's House): e_50 x2, m_00, r_20, r_21; po04 (Piglet's House): e_50 x2, m_00, r_20, r_21; po05 (Kanga's House): e_50 x2, m_00, r_20, r_21; po06 (A Windsday Tale): m_01; po07 (The Honey Hunt): m_01; po08 (Blossom Valley): m_01; po09 (The Spooky Cave): b_99, e_50, m_00, r_20, r_21

**lk Pride Lands** (10 placements in 6 rooms): lk00 (Pride Rock): e_50; lk06: e_50, m_01 x2; lk09 (Oasis): e_50, m_01 x2; lk10 (Pride Rock): m_00; lk11 (Oasis): m_00; lk12 (Overlook): m_00

**lm Atlantica** (15 placements in 11 rooms): lm00 (Triton's Throne): m_00; lm01 (Ariel's Grotto): m_00; lm02 (Undersea Courtyard): b_40, e_50 x2, m_00 x2; lm03 (Undersea Courtyard): m_00; lm04 (The Palace: Performance Hall): m_00; lm05 (Sunken Ship): m_00; lm06 (The Shore): m_00; lm07 (The Shore): m_00; lm08 (The Shore): m_00; lm09 (Wrath of the Sea): m_00; lm10 (Wedding Ship): m_00

**dc Disney Castle** (8 placements in 3 rooms): dc00 (Audience Chamber): b_41, m_22; dc01 (Library): e_50, m_22 x2; dc02 (Colonnade): e_50, m_22 x2

**wi Timeless River** (12 placements in 1 rooms): wi00: e_50, e_51, e_53, m_01 x9

**nm Halloween Town** (11 placements in 4 rooms): nm02 (Graveyard): e_50 x2, m_01 x3; nm04 (Hinterlands): m_01 x2; nm05 (Yuletide Hill): m_01 x3; nm09 (Toy Factory: Shipping and Receiving): s_99

**ca Port Royal** (23 placements in 7 rooms): ca01 (Harbor): e_51, m_01 x3; ca02 (Town): s_99; ca03 (The Interceptor): e_50, e_51, e_52, e_53, m_00 x2; ca04 (The Interceptor: Ship's Hold): m_01 x2; ca05 (The Black Pearl): e_50, e_51, m_00 x2; ca06 (The Black Pearl: Captain's Stateroom): e_50, m_01 x2; ca11 (Ship Graveyard: The Interceptor's Hold): e_50, m_01 x2

**tr Space Paranoids** (23 placements in 7 rooms): tr00 (Pit Cell): e_50, e_52, e_53, m_01 x3; tr01 (Canyon): e_50, m_01 x3; tr02 (Game Grid): m_00; tr03 (Dataspace): e_50, m_01; tr05 (I/O Tower: Communications Room): e_50, e_52, m_01 x2; tr08 (Central Computer Mesa): e_50, e_51, m_01 x3; tr10 (Solar Sailer Simulation): m_01

**eh World That Never Was** (35 placements in 12 rooms): eh00: m_00; eh01: e_50, m_01 x3; eh04: e_50, m_01 x3; eh09: m_01 x3; eh10: e_50, m_01 x2; eh11: e_50, m_01 x2; eh13: m_01 x5; eh14: e_50, m_01; eh15: e_50, m_01; eh18: e_50, m_01 x4; eh23: b_97, b_99; eh27: m_00

## 3. When the player is a different object

### 3a. All PLAYER-type objects

VERIFIED: `00objentry.bin` (dump: `local\analysis\objentry.txt`). "Uses" = how many times a room's spawn data names the object directly; most player objects are never named in room data because the party table (3b) chooses them.

| Id | Model | Animation set | Form field | Status | Move set | Kind (HYPOTHESIS) | Uses in rooms |
|---|---|---|---|---|---|---|---|
| 0x0054 | P_EX100 | P_EX100.mset | SoraRoxasDefault | 1 | 1 | player character, form or vehicle | 1 |
| 0x0055 | P_EX100_BTLF | P_EX100_BTLF.mset | ValorForm | 1 | 2 | player character, form or vehicle | 0 |
| 0x0056 | P_EX100_MAGF | P_EX100_MAGF.mset | WisdomForm | 1 | 3 | player character, form or vehicle | 0 |
| 0x0057 | P_EX100_TRIF | P_EX100_TRIF.mset | MasterForm | 1 | 4 | player character, form or vehicle | 0 |
| 0x0058 | P_EX100_ULTF | P_EX100_ULTF.mset | FinalForm | 1 | 5 | player character, form or vehicle | 0 |
| 0x0059 | P_EX100_HTLF | P_EX100_HTLF.mset | AntiForm | 1 | 6 | player character, form or vehicle | 0 |
| 0x005A | P_EX110 | P_EX110.mset | SoraRoxasDefault | 14 | 9 | player character, form or vehicle | 0 |
| 0x005B | P_EX200 | P_EX200.mset | Default | 4 | 28 | player character, form or vehicle | 0 |
| 0x0236 | PLAYER | P_EX100.mset | Default | 0 | 0 | marker / placeholder | 0 |
| 0x028A | P_LK100 | P_LK100.mset | LionKingSora | 1 | 7 | player character, form or vehicle | 0 |
| 0x02B5 | P_EX100_NM | P_EX100.mset | SoraRoxasDefault | 1 | 11 | player character, form or vehicle | 0 |
| 0x0318 | P_EX220 | P_EX220.mset | Default | 4 | 28 | player character, form or vehicle | 0 |
| 0x0323 | P_EX110_BTLF | P_EX110_BTLF.mset | RoxasDualWield | 14 | 10 | player character, form or vehicle | 0 |
| 0x035B | PO06_PLAYER | PO06_PLAYER.mset | Default | 1 | 58 | player character, form or vehicle | 2 |
| 0x0386 | LAST_ATTACKER | P_EX100.mset | Default | 0 | 0 | marker / placeholder | 0 |
| 0x03BE | P_LM100 | P_LM100.mset | Default | 1 | 8 | player character, form or vehicle | 0 |
| 0x03C8 | F_NM180 | F_NM180.mset | Default | 0 | 0 | special object, no player stats | 1 |
| 0x03E6 | P_EX100_NM_BTLF | P_EX100_BTLF.mset | ValorForm | 1 | 12 | player character, form or vehicle | 0 |
| 0x03E7 | P_EX100_NM_MAGF | P_EX100_MAGF.mset | WisdomForm | 1 | 13 | player character, form or vehicle | 0 |
| 0x03E8 | P_EX100_NM_TRIF | P_EX100_TRIF.mset | MasterForm | 1 | 14 | player character, form or vehicle | 0 |
| 0x03E9 | P_EX100_NM_ULTF | P_EX100_ULTF.mset | FinalForm | 1 | 15 | player character, form or vehicle | 0 |
| 0x03EA | P_EX100_NM_HTLF | P_EX100_HTLF.mset | AntiForm | 1 | 16 | player character, form or vehicle | 0 |
| 0x04B4 | LAST_HITMARK | P_EX100.mset | Default | 0 | 0 | marker / placeholder | 0 |
| 0x04FF | P_EX100_AL_CARPET | P_EX100_AL_CARPET.mset | SoraRoxasDefault | 1 | 53 | player character, form or vehicle | 14 |
| 0x05E9 | AL14_PLAYER | P_EX100_ESCAPE.mset | Default | 1 | 57 | player character, form or vehicle | 1 |
| 0x05F5 | P_EX100_TR_LIGHTCYCLE | P_EX100_TR_LIGHTCYCLE.mset | Default | 1 | 54 | player character, form or vehicle | 2 |
| 0x0601 | M_EX950_CARD | M_EX950_CARD.mset | Default | 1 | 56 | player character, form or vehicle | 0 |
| 0x0602 | M_EX950_DICE | M_EX950_DICE.mset | Default | 1 | 55 | player character, form or vehicle | 0 |
| 0x0656 | P_EX100_TR | P_EX100.mset | SoraRoxasDefault | 1 | 37 | player character, form or vehicle | 0 |
| 0x0657 | P_EX100_WI | P_EX100.mset | SoraRoxasDefault | 1 | 43 | player character, form or vehicle | 0 |
| 0x0669 | P_EX100_TR_BTLF | P_EX100_BTLF.mset | ValorForm | 1 | 38 | player character, form or vehicle | 0 |
| 0x066A | P_EX100_WI_BTLF | P_EX100_BTLF.mset | ValorForm | 1 | 44 | player character, form or vehicle | 0 |
| 0x066B | P_EX100_TR_MAGF | P_EX100_MAGF.mset | WisdomForm | 1 | 39 | player character, form or vehicle | 0 |
| 0x066C | P_EX100_WI_MAGF | P_EX100_MAGF.mset | WisdomForm | 1 | 45 | player character, form or vehicle | 0 |
| 0x066D | P_EX100_TR_TRIF | P_EX100_TRIF.mset | MasterForm | 1 | 40 | player character, form or vehicle | 0 |
| 0x066E | P_EX100_WI_TRIF | P_EX100_TRIF.mset | MasterForm | 1 | 46 | player character, form or vehicle | 0 |
| 0x066F | P_EX100_TR_ULTF | P_EX100_ULTF.mset | FinalForm | 1 | 41 | player character, form or vehicle | 0 |
| 0x0670 | P_EX100_WI_ULTF | P_EX100_ULTF.mset | FinalForm | 1 | 47 | player character, form or vehicle | 0 |
| 0x0671 | P_EX100_TR_HTLF | P_EX100_HTLF.mset | AntiForm | 1 | 42 | player character, form or vehicle | 0 |
| 0x0672 | P_EX100_WI_HTLF | P_EX100_HTLF.mset | AntiForm | 1 | 48 | player character, form or vehicle | 0 |
| 0x068F | DEAD_BOSS | P_EX100.mset | Default | 0 | 0 | marker / placeholder | 0 |
| 0x06BE | LAST_GIMMICK | P_EX100.mset | Default | 0 | 0 | marker / placeholder | 0 |
| 0x06C1 | P_EX120 | P_EX120.mset | SoraRoxasDefault | 1 | 1 | player character, form or vehicle | 0 |
| 0x0840 | P_EX100_SIDECAR | P_EX100_SIDECAR.mset | Default | 1 | 61 | player character, form or vehicle | 1 |
| 0x0869 | P_EX210 | P_EX210.mset | Default | 4 | 28 | player character, form or vehicle | 0 |
| 0x0955 | P_EX100_XM | P_EX100.mset | SoraRoxasDefault | 1 | 11 | player character, form or vehicle | 0 |
| 0x0956 | P_EX100_XM_BTLF | P_EX100_BTLF.mset | ValorForm | 1 | 12 | player character, form or vehicle | 0 |
| 0x0957 | P_EX100_XM_MAGF | P_EX100_MAGF.mset | WisdomForm | 1 | 13 | player character, form or vehicle | 0 |
| 0x0958 | P_EX100_XM_TRIF | P_EX100_TRIF.mset | MasterForm | 1 | 14 | player character, form or vehicle | 0 |
| 0x0959 | P_EX100_XM_ULTF | P_EX100_ULTF.mset | FinalForm | 1 | 15 | player character, form or vehicle | 0 |
| 0x095A | P_EX100_XM_HTLF | P_EX100_HTLF.mset | AntiForm | 1 | 16 | player character, form or vehicle | 0 |
| 0x095D | P_EX100_KH1F | P_EX100_KH1F.mset | LimitForm | 1 | 66 | player character, form or vehicle | 0 |
| 0x095E | P_EX100_NM_KH1F | P_EX100_KH1F.mset | LimitForm | 1 | 67 | player character, form or vehicle | 0 |
| 0x095F | P_EX100_XM_KH1F | P_EX100_KH1F.mset | LimitForm | 1 | 67 | player character, form or vehicle | 0 |
| 0x0960 | P_EX100_TR_KH1F | P_EX100_KH1F.mset | LimitForm | 1 | 68 | player character, form or vehicle | 0 |
| 0x0961 | P_EX100_WI_KH1F | P_EX100_KH1F.mset | LimitForm | 1 | 69 | player character, form or vehicle | 0 |

### 3b. The party table: which object is the player, per world

VERIFIED: `03system.bin`, table `memt` (Final Mix layout, 18 members per row). A row applies to a world, optionally only when a story flag is set (or not set) or in one area. Empty cells are 0 in the data. HYPOTHESIS: a 0 means "keep the default row's value". Row 0 has world id 0 and is the only row with every member filled. HYPOTHESIS: it is the default for all worlds. High-poly cutscene models (members 12 to 18) are left out here; they are in `memt.yml`.

| Row | World | Flag set | Flag not set | Area | Player | Friend 1 | Friend 2 | World guest | Valor | Wisdom | Limit | Master | Final | Anti | Mickey | PlayerSize | FriendSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | all (default) |  |  |  | P_EX100 | P_EX020 | P_EX030 | P_EH000 | P_EX100_BTLF | P_EX100_MAGF | P_EX100_KH1F | P_EX100_TRIF | P_EX100_ULTF | P_EX100_HTLF | P_EX200 | 4299264 | 1625344 |
| 1 | zz | 4227 |  |  |  |  |  |  |  |  |  |  |  |  | P_EX220 |  |  |
| 2 | zz | 16 |  |  |  |  |  |  |  |  |  |  |  |  | P_EX220 |  |  |
| 3 | tt | 2267 | 2256 |  | P_EX110 |  |  |  | P_EX110_BTLF |  |  |  |  |  |  | 3984640 | 1625344 |
| 4 | tt | 2254 | 2255 |  | P_EX110_BTLF |  |  |  | P_EX110_BTLF |  |  |  |  |  |  | 3984640 | 1625344 |
| 5 | tt | 2256 | 2257 |  | P_EX120 |  |  |  |  |  |  |  |  |  |  | 3984640 | 1625344 |
| 6 | hb |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7 | po |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8 | dc |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9 | wm |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 10 | es |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 11 | di |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 12 | ca |  |  |  |  |  |  | P_CA000_HUMAN_LOW |  |  |  |  |  |  |  | 4299264 | 2149632 |
| 13 | ca | 16478 | 16479 |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 14 | ca | 16480 | 16481 |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 15 | ca | 16474 | 16475 |  |  |  |  | P_CA000_LOW |  |  |  |  |  |  |  | 4299264 | 2411776 |
| 16 | ca | 16476 | 16477 |  |  |  |  | P_CA000_LOW |  |  |  |  |  |  |  | 4299264 | 2411776 |
| 17 | he |  |  |  |  |  |  | P_HE000 |  |  |  |  |  |  |  | 4299264 | 2149632 |
| 18 | he | 6198 | 6199 |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 19 | he | 6202 | 6204 |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 20 | al |  |  |  |  |  |  | P_AL000 |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 21 | nm |  |  |  | P_EX100_NM | P_EX020_NM | P_EX030_NM | P_NM000 | P_EX100_NM_BTLF | P_EX100_NM_MAGF | P_EX100_NM_KH1F | P_EX100_NM_TRIF | P_EX100_NM_ULTF | P_EX100_NM_HTLF |  | 4299264 | 1625344 |
| 22 | nm |  |  | 2 | P_EX100_XM | P_EX020_XM | P_EX030_XM |  | P_EX100_XM_BTLF | P_EX100_XM_MAGF | P_EX100_XM_KH1F | P_EX100_XM_TRIF | P_EX100_XM_ULTF | P_EX100_XM_HTLF |  | 4299264 | 1625344 |
| 23 | nm | 14394 |  |  |  |  |  | P_NM000_SANTA |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 24 | bb |  |  |  |  |  |  | P_BB000 |  |  |  |  |  |  |  | 4299264 | 2097152 |
| 25 | mu |  |  |  |  |  |  | P_MU010 |  |  |  |  |  |  |  | 4299264 | 1939968 |
| 26 | mu | 8216 |  |  |  |  |  | P_MU000 |  |  |  |  |  |  |  | 4299264 | 1992320 |
| 27 | eh |  |  |  |  |  |  | P_EH000 |  |  |  |  |  |  |  | 4299264 | 1887488 |
| 28 | eh | 18499 | 18500 |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 29 | eh | 18501 |  |  |  |  |  | P_EH000_LAST |  |  |  |  |  |  |  | 4299264 | 1887488 |
| 30 | eh | 18506 |  |  |  |  |  |  |  |  |  |  |  |  |  | 4299264 | 1625344 |
| 31 | eh | 18508 |  |  |  |  |  | P_EH000_LAST |  |  |  |  |  |  |  | 4299264 | 1887488 |
| 32 | tr |  |  |  | P_EX100_TR | P_EX020_TR | P_EX030_TR | P_TR000 | P_EX100_TR_BTLF | P_EX100_TR_MAGF | P_EX100_TR_KH1F | P_EX100_TR_TRIF | P_EX100_TR_ULTF | P_EX100_TR_HTLF |  | 4299264 | 1782656 |
| 33 | wi |  |  |  | P_EX100_WI | P_WI020 | P_WI030 |  | P_EX100_WI_BTLF | P_EX100_WI_MAGF | P_EX100_WI_KH1F | P_EX100_WI_TRIF | P_EX100_WI_ULTF | P_EX100_WI_HTLF |  | 4299264 | 1730176 |
| 34 | lk |  |  |  | P_LK100 | P_LK020 | P_LK030 | P_LK000 |  |  |  |  |  |  |  | 2516608 | 2202112 |
| 35 | lm |  |  |  | P_LM100 | N_LM010_PLY | N_LM020_PLY |  |  |  |  |  |  |  |  | 3984640 | 2202112 |
| 36 | wm |  |  |  | WM_CURSOR |  |  |  |  |  |  |  |  |  |  |  |  |

The last two columns are fields the table calls `PlayerSize` and `FriendSize` (VERIFIED values: 2,516,608 / 2,202,112; 3,984,640 / 1,625,344; 3,984,640 / 2,202,112; 4,299,264 / 1,625,344; 4,299,264 / 1,730,176; 4,299,264 / 1,782,656; 4,299,264 / 1,887,488; 4,299,264 / 1,939,968; 4,299,264 / 1,992,320; 4,299,264 / 2,097,152; 4,299,264 / 2,149,632; 4,299,264 / 2,411,776). HYPOTHESIS: they are memory budgets in bytes for the player's and the friends' data in that world. If so, they are the first numbers to look at for "does a second player fit in memory".

Reading it for the twin (HYPOTHESIS): the twin must be "the same object the Player column gives for this world and story point", and when a Drive Form is used, the object in that form's column.

### 3c. Party line-ups in the same table

VERIFIED: `memt`, second part (member index collection). Numbers are positions in the 18-member row (0 = Sora ... 3 = world guest); 18 is past the end. HYPOTHESIS: 18 means "nobody"; values 67 and 131 are 3 plus a flag bit (64, 128).

| Line-up | Player | Friend 1 | Friend 2 | World guest slot |
|---|---|---|---|---|
| 0 | 0 | 18 | 18 | 18 |
| 1 | 0 | 1 | 2 | 18 |
| 2 | 0 | 3 | 2 | 1 |
| 3 | 0 | 67 | 2 | 1 |
| 4 | 0 | 131 | 2 | 1 |
| 5 | 0 | 3 | 18 | 18 |
| 6 | 0 | 1 | 18 | 18 |

### 3d. Player objects named directly in room data

VERIFIED: spawn entities in `ard\*.ard` whose object is of type PLAYER (other than the 0x0236 placeholder), and the missions named by the script programs that load those groups.

| Id | Model | Entities | Room: spawn groups | Missions of the programs that load them |
|---|---|---|---|---|
| 0x0054 | P_EX100 | 1 | nm07 (Christmas Tree Plaza): b_99 | NM07_MS204 |
| 0x035B | PO06_PLAYER | 2 | po06 (A Windsday Tale): b_40, m_00 | PO06_MS100, PO06_MS101, PO06_MS101_FREE |
| 0x03C8 | F_NM180 | 1 | nm10 (Toy Factory: The Wrapping Room): m_50 | - |
| 0x04FF | P_EX100_AL_CARPET | 14 | al05 (Above Agrabah): b_60; al14 (Sandswept Ruins): b_61, b_64, b_67, b_68, b_69, e_50, e_51, e_52, e_53, e_54, e_55, m_00 | AL05_MS203, AL14_MS201A, AL14_MS201B, AL14_MS_P |
| 0x05E9 | AL14_PLAYER | 1 | al14 (Sandswept Ruins): b_70 | AL14_MS202, AL14_MS202_FREE |
| 0x05F5 | P_EX100_TR_LIGHTCYCLE | 2 | tr02 (Game Grid): b_97, b_99 | TR02_MS102A, TR02_MS102B, TR02_MS102_FREE |
| 0x0840 | P_EX100_SIDECAR | 1 | eh22 (Station of Awakening): b_40 | EH22_MS111, TEST_EH22_MS111 |

Worth a test by the other lanes: **nm07, group `b_99`** (loaded by battle program 0x47, mission `NM07_MS204`, `Party W_FRIEND`). VERIFIED: this group holds the real Sora object 0x0054 together with the two friend placeholders and four boss objects, and no PLAYER placeholder. So the game's own data uses a real PLAYER-type object where every other room uses the placeholder. HYPOTHESIS: either the engine treats it as the player's start position, or a second Sora appears in that fight; which one it is tells how the engine decides between "this is the player" and "spawn another one".

The vehicle and special-mode objects (carpet, light cycle, sidecar, `PO06_PLAYER`, `AL14_PLAYER`) are placed the same direct way, each in its own minigame room. A twin there needs a second copy of that object.

Also VERIFIED: 4 spawn entities name a real FRIEND-type object directly (3 different objects), besides the two friend placeholders.

## 4. Missions

VERIFIED: `msn\jp\*.bar` (303 files; header and op-codes read as described in the OpenKH format notes) and the `Mission` commands in the room scripts (477 commands, 309 different names).

- Mission files that no room script names: 8: AL00_SKATE_02, AL14_MS_S, HB09_SKATE_02, HE_COL_8PP_BOSS, NM09_SKATE_02, TT05_AXEL, TT20_AXEL, TT40_KINOKO_AXE.
- Mission names in room scripts with no file: 14: HE00_MS104, PO01_MS500, PO06_MS100, PO07_MS200, PO08_MS300, PO09_MS400, TEST_EH22_MS111, TEST_HE_COLOSSEUM, TEST_HE_COLOSSEUM2, TEST_HE_COLOSSEUM3, TEST_MU07_MS999, TEST_PO08_MS300, TEST_SKATEBOARD, ZZ_HE09_MS201.
- Cross-check: the id written in the room script equals the id in the mission file's header in 375 of 375 uses.
- Name flags are read from the file name only. KINOKO is the Japanese word for mushroom; FM marks names containing `_FM_`; FREE and RE mark `_FREE` and `_RE` variants; COLOSSEUM also covers `HE_COL_` names.

Columns: **Flags** are the mission header bits (boss, noDrive = Drive switched off, noLeave, mickey = Mickey rescue allowed, noExp, noMagic, retry, freeSummon, noSummon, place, showWeapon, noPrize, noPrizebox, hideMap). **Meters** are on-screen counters the mission defines. **Name flag** = the name looks like a minigame or special mode (this is only a reading of the name: HYPOTHESIS). **Party** = party value set by the programs that start it.

Name flags used: COLOSSEUM (45), FREE (15), KINOKO (14), WORK (10), SKATE (9), FM (8), CONFINE (7), MEDAL (6), GIMMICK (4), TRAP (3), RE (3), BAGGAGE (3), LETTER (3), PERFORM (3), CLEAN (3), POSTER (3), WORM (3), AXEL (2), NAZO (1), SWITCH (1), SHIP_BATTLE (1), WORLDMAP (1).

**tt Twilight Town** (65 missions, 31 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| TEST_SKATEBOARD |  | tt06 tt07 | 2 | - | - | - | SKATE |
| TT02_MS201 | 0xB1 | tt02 | 1 | NO_FRIEND | noPrize | - | - |
| TT03_MS400 | 0x126 | tt03 | 1 | NO_FRIEND | boss,noLeave,hideMap | - | - |
| TT03_MS601 | 0xBB | tt03 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Gauge | - |
| TT04_MS00 | 0x128 | tt04 | 1 | NO_FRIEND | boss,noDrive,noLeave,noPrize,hideMap,noExp,noMagic | Counterx2,Timer | - |
| TT04_MS01 | 0x129 | tt04 | 1 | NO_FRIEND | boss,noDrive,noLeave,noPrize,hideMap,noExp,noMagic | Counterx2,Timer | - |
| TT04_MS02 | 0x12A | tt04 | 1 | NO_FRIEND | boss,noDrive,noLeave,noPrize,hideMap,noExp,noMagic | Counterx2,Timer | - |
| TT04_MS106 | 0xAC | tt04 | 1 | NO_FRIEND | - | - | - |
| TT04_MS107 | 0xAD | tt04 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize | Counter | - |
| TT04_MS108 | 0xAE | tt04 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap | Gauge | - |
| TT04_MS301 | 0xB2 | tt04 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge | - |
| TT04_MS500 | 0x127 | tt04 | 1 | NO_FRIEND | boss,noLeave,hideMap | - | - |
| TT04_MS901 | 0xC2 | tt04 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT05_AXEL | 0x19 | - | 0 | - | boss | - | AXEL |
| TT05_MS401 | 0xB6 | tt05 | 2 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,Timer | - |
| TT05_MS402 | 0xB7 | tt05 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,Timer | - |
| TT05_MS403 | 0xB8 | tt05 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT05_MS404 | 0xB9 | tt05 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT05_MS405 | 0xBA | tt05 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,Timer | - |
| TT06_BAGGAGE_01 | 0x147 | tt06 | 1 | NO_FRIEND | noPrize,hideMap | Timer | BAGGAGE |
| TT06_BAGGAGE_02 | 0x14D | tt06 | 1 | NO_FRIEND | noDrive,noPrize,hideMap | Timer,Watch | BAGGAGE |
| TT06_LETTER_01 | 0x149 | tt06 | 1 | NO_FRIEND | noPrize,hideMap | Counter,Timer | LETTER |
| TT06_LETTER_02 | 0x14F | tt06 | 1 | NO_FRIEND | noDrive,noPrize | Counter,Timer,Watch | LETTER |
| TT06_PERFORM_01 | 0x14A | tt06 | 1 | NO_FRIEND | noPrize,hideMap | ComboCounter,Counter | PERFORM |
| TT06_PERFORM_02 | 0x150 | tt06 | 1 | NO_FRIEND | noDrive,noPrize,hideMap | ComboCounter,Counterx2 | PERFORM |
| TT06_WORK_BAGGAGE | 0xCE | tt06 | 1 | NO_FRIEND | noPrize,hideMap | Timer | BAGGAGE WORK |
| TT06_WORK_LETTER | 0xD0 | tt06 | 1 | NO_FRIEND | noPrize,hideMap | Counter,Timer | LETTER WORK |
| TT06_WORK_PERFORM | 0xF4 | tt06 | 1 | NO_FRIEND | noPrize,hideMap | ComboCounter,Counter | PERFORM WORK |
| TT07_CLEAN_01 | 0x14B | tt07 | 1 | NO_FRIEND | noPrize,hideMap | Counterx2 | CLEAN |
| TT07_CLEAN_02 | 0x151 | tt07 | 1 | NO_FRIEND | noDrive,noPrize,hideMap | Counterx3 | CLEAN |
| TT07_MS101 | 0xA7 | tt07 | 1 | NO_FRIEND | noPrize | - | - |
| TT07_MS103 | 0xA9 | tt07 | 1 | NO_FRIEND | noPrize | - | - |
| TT07_MS105 | 0xAB | tt07 | 1 | NO_FRIEND | noPrize | - | - |
| TT07_POSTER_01 | 0x146 | tt07 | 1 | NO_FRIEND | noPrize | Counter,Timer | POSTER |
| TT07_POSTER_02 | 0x14C | tt07 | 1 | NO_FRIEND | noDrive,noPrize | Counter,Timer,Watch | POSTER |
| TT07_SKATE_01 | 0x134 | tt07 | 1 | - | - | Counterx3 | SKATE |
| TT07_WORK_CLEAN | 0xD3 | tt07 | 1 | NO_FRIEND | noPrize,hideMap | Counterx2 | CLEAN WORK |
| TT07_WORK_POSTER | 0xCD | tt07 | 1 | NO_FRIEND | noPrize | Counter,Timer | POSTER WORK |
| TT07_WORK_WORM | 0xF2 | tt07 | 1 | NO_FRIEND | boss,noLeave,noPrize,hideMap | Timer | WORK WORM |
| TT07_WORM_01 | 0x148 | tt07 | 1 | NO_FRIEND | boss,noLeave,noPrize,hideMap | Timer | WORM |
| TT07_WORM_02 | 0x14E | tt07 | 1 | NO_FRIEND | boss,noDrive,noLeave,noPrize,hideMap | Timer,Watch | WORM |
| TT08_MS701 | 0xBE | tt08 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| TT10_WORK_MIRROR | 0xD7 | tt10 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap | - | WORK |
| TT10_WORK_TIMBER | 0xD5 | tt10 | 1 | NO_FRIEND | noPrize,hideMap | - | WORK |
| TT12_WORK_BOX | 0xF3 | tt12 | 1 | NO_FRIEND | noPrize,hideMap | Gauge | WORK |
| TT14_KINOKO_LAR | 0x1A9 | tt14 | 1 | - | place,retry | Counterx2,Timer | KINOKO |
| TT14_MS001 | 0xC3 | tt14 tt41 | 2 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| TT14_MS109 | 0xAF | tt14 | 1 | NO_FRIEND | boss,noLeave,noPrizebox,hideMap | Counter,Gauge | - |
| TT14_MS110 | 0xB0 | tt14 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox | Gauge | - |
| TT19_MS602 | 0xBC | tt19 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT20_AXEL | 0x1A | - | 0 | - | boss | - | AXEL |
| TT20_MS603 | 0xBD | tt20 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT20_MS603_RE | 0x1B5 | tt20 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | RE |
| TT25_KINOKO_AXE | 0x1B7 | tt25 | 1 | - | place,retry | Counterx2 | KINOKO |
| TT25_MS801 | 0xBF | tt25 | 1 | DEFAULT | boss,showWeapon,noPrizebox,hideMap | Gauge | - |
| TT29_MS802 | 0xC0 | tt29 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| TT30_MS803 | 0xC1 | tt30 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| TT32_MS302 | 0xB3 | tt32 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox | Gauge | - |
| TT32_MS303 | 0xB4 | tt32 | 1 | NO_FRIEND | noPrize | - | - |
| TT34_MS304 | 0xB5 | tt34 | 1 | NO_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| TT36_KINOKO_SAI | 0x1A4 | tt36 | 1 | - | place,retry | Timer,Watch | KINOKO |
| TT36_WORK_FIGURE | 0xD6 | tt36 | 1 | NO_FRIEND | boss,noLeave,noPrize,hideMap | - | WORK |
| TT40_KINOKO_AXE | 0x1A5 | - | 0 | - | - | Counterx2 | KINOKO |
| TT40_MS002 | 0xC4 | tt40 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TT40_MS003 | 0xC5 | tt40 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |

**hb Hollow Bastion** (32 missions, 18 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| HB01_MS601 | 0xEC | hb01 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| HB02_KINOKO_ROX | 0x1AA | hb02 | 1 | - | place,retry | - | KINOKO |
| HB04_KINOKO_DEM | 0x1A6 | hb04 | 1 | - | place,retry | Counterx2 | KINOKO |
| HB04_MS403 | 0x90 | hb04 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Timer | - |
| HB07_MS402 | 0x8F | hb18 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| HB08_MS102 | 0x8D | hb08 | 2 | NO_FRIEND | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| HB09_MS101 | 0x8C | hb09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| HB09_MS501 | 0xDA | hb09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| HB09_MS901 | 0x96 | hb09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| HB09_SKATE_01 | 0x130 | hb09 | 2 | - | - | ComboCounter,Counter | SKATE |
| HB09_SKATE_02 | 0x131 | - | 0 | - | - | - | SKATE |
| HB13_MS902 | 0x139 | hb13 | 1 | DEFAULT | noPrize | - | - |
| HB16_MS404A | 0x91 | hb16 | 2 | NO_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| HB16_MS404B | 0x92 | hb16 | 2 | NO_FRIEND | showWeapon,noLeave,noPrizebox | - | - |
| HB16_MS404C | 0x93 | hb16 | 2 | NO_FRIEND | showWeapon,noLeave,noPrizebox | - | - |
| HB16_MS404D | 0x94 | hb16 | 2 | NO_FRIEND | showWeapon,noLeave,noPrizebox | - | - |
| HB17_MS405 | 0xA5 | hb17 | 2 | NO_FRIEND | boss,noPrizebox,hideMap | Counter | - |
| HB20_MS401 | 0x11C | hb20 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| HB22_FM_SWITCH | 0x1B6 | hb22 | 1 | - | place,retry | - | FM SWITCH |
| HB24_CONFINE | 0x1AB | hb24 | 1 | - | place,noLeave,noPrizebox,retry | - | CONFINE |
| HB24_CONFINE_2 | 0x1B3 | hb24 | 1 | - | place,noLeave,noPrizebox,retry | - | CONFINE |
| HB24_CONFINE_3 | 0x1B4 | hb24 | 1 | - | place,retry | - | CONFINE |
| HB25_CONFINE_1 | 0x1AC | hb25 | 1 | - | place,noLeave,noPrizebox,retry | - | CONFINE |
| HB25_CONFINE_2 | 0x1AD | hb25 | 1 | - | place,noLeave,noPrizebox,retry | - | CONFINE |
| HB25_CONFINE_3 | 0x1AE | hb25 | 1 | - | place,noLeave,noPrizebox,retry | - | CONFINE |
| HB25_CONFINE_4 | 0x1B2 | hb25 | 1 | - | place,retry | - | CONFINE |
| HB32_FM_VEX | 0x195 | hb32 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge | FM |
| HB33_FM_LAR | 0x199 | hb33 | 3 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | FM |
| HB33_FM_LEX | 0x196 | hb33 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counterx2 | FM |
| HB33_FM_VEX | 0x1B9 | hb33 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge | FM |
| HB34_FM_ZEX | 0x197 | hb34 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | FM |
| HB38_FM_MAR | 0x198 | hb38 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | FM |

**bb Beast's Castle** (12 missions, 4 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| BB00_MS202 | 0x48 | bb00 | 2 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| BB01_MS101 | 0x35 | bb01 | 1 | DEFAULT | boss,showWeapon,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| BB03_MS103 | 0x46 | bb03 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| BB04_MS201 | 0x01 | bb04 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| BB05_MS104A | 0x47 | bb05 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| BB05_MS104B | 0x16 | bb05 | 2 | W_FRIEND W_FRIEND_FIX | boss,noLeave,noPrizebox,hideMap,mickey | - | - |
| BB08_GIMMICK | 0x97 | bb08 | 1 | - | - | - | GIMMICK |
| BB11_MS102 | 0x15 | bb11 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| BB12_GIMMICK | 0x98 | bb12 | 2 | - | - | Gauge | GIMMICK |
| BB13_KINOKO_XAL | 0x1A0 | bb13 | 1 | - | place,retry | Counterx2 | KINOKO |
| BB15_MS203 | 0x99 | bb15 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap,mickey | - | - |
| BB15_MS203_RE | 0x1B8 | bb15 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | RE |

**he Olympus Coliseum** (64 missions, 46 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| HE00_MS104 |  | he00 | 1 | DEFAULT | - | - | - |
| HE00_MS104A | 0x9D | he00 | 2 | NO_FRIEND | boss,noPrize,hideMap | Counter,Timer | - |
| HE00_MS104B | 0x9E | he00 | 1 | NO_FRIEND | boss,noPrize,hideMap | Counter,Timer | - |
| HE02_MS104C | 0xEA | he02 | 1 | - | noPrize,hideMap | Counter | - |
| HE02_MS104D | 0x113 | he02 | 1 | - | noPrize,hideMap | Counterx2,Timer | - |
| HE05_MS102 | 0x1B | he05 | 1 | W_FRIEND_FIX | boss,noLeave,noPrizebox,hideMap | - | - |
| HE06_MS101 | 0x17 | he06 | 2 | DEFAULT | boss,showWeapon,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| HE06_MS203 | 0x51 | he06 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| HE07_MS103 | 0x4A | he07 | 1 | W_FRIEND_ONLY | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| HE08_MS106 | 0x4C | he08 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Gauge,Timer | - |
| HE08_MS107 | 0x4D | he08 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Timer | - |
| HE09_MS201 | 0x4F | he09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| HE09_MS202 | 0x50 | he09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| HE17_KINOKO_ZEX | 0x1A3 | he17 | 1 | - | place,retry | Timer,Watch | KINOKO |
| HE17_MS105 | 0x4B | he17 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Timer | - |
| HE18_MS108 | 0xE3 | he18 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| HE19_MS204 | 0x125 | he19 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| HE19_MS205 | 0x124 | he19 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| HE_COLOSSEUM | 0x123 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COLOSSEUM_2 | 0x15F | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COLOSSEUM_2_FOG | 0x178 | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COLOSSEUM_3 | 0x15E | he09 | 1 | NO_FRIEND | boss,noDrive,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx3 | COLOSSEUM |
| HE_COLOSSEUM_6 | 0x173 | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COLOSSEUM_6_FOG | 0x186 | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COLOSSEUM_7 | 0x172 | he09 | 1 | NO_FRIEND | boss,noDrive,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | ComboCounter,Counterx3 | COLOSSEUM |
| HE_COLOSSEUM_8 | 0x17B | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COLOSSEUM_8_CEL | 0x17E | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COLOSSEUM_8_ONLY | 0x18B | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COLOSSEUM_8_PP | 0x17C | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COLOSSEUM_8_TIT | 0x17D | he09 | 1 | DEFAULT | boss,noDrive,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | ComboCounter,Counterx3 | COLOSSEUM |
| HE_COL_1_10 | 0x187 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COL_1_8 | 0x170 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,LimitCost,Timer | COLOSSEUM |
| HE_COL_2_10 | 0x192 | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COL_4_1 | 0x164 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_4_10 | 0x16D | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_4_2 | 0x165 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2,Timer | COLOSSEUM |
| HE_COL_4_3 | 0x166 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx3 | COLOSSEUM |
| HE_COL_4_4 | 0x167 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_4_5 | 0x168 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_4_6 | 0x169 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2,Timer | COLOSSEUM |
| HE_COL_4_7 | 0x16A | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx3 | COLOSSEUM |
| HE_COL_4_8 | 0x16B | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | AddDrive,Counterx2,Timer | COLOSSEUM |
| HE_COL_4_9 | 0x16C | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | AddDrive,ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_5 | 0x18F | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COL_5_10 | 0x191 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COL_5_8 | 0x190 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,LimitCost,Timer | COLOSSEUM |
| HE_COL_6_10 | 0x193 | he09 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COL_8PP_BOSS | 0x181 | - | 0 | - | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx3,LimitCost | COLOSSEUM |
| HE_COL_8TI_BOSS | 0x180 | he09 | 1 | DEFAULT | boss,noDrive,showWeapon,noLeave,noPrize,hideMap,noExp,freeSummon | ComboCounter,Counterx3 | COLOSSEUM |
| HE_COL_8_10 | 0x18C | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_8_25 | 0x18E | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COL_8_30 | 0x18A | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,LimitCost | COLOSSEUM |
| HE_COL_8_31 | 0x194 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COL_8_35 | 0x183 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COL_8_40 | 0x188 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2,DriveRefillRatio,Timer | COLOSSEUM |
| HE_COL_8_45 | 0x182 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | Counterx2,Timer | COLOSSEUM |
| HE_COL_8_49 | 0x189 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_8_5 | 0x184 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_8_50 | 0x18D | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| HE_COL_8_6 | 0x185 | he09 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrize,hideMap,noExp | ComboCounter,Counterx2 | COLOSSEUM |
| TEST_HE_COLOSSEUM |  | he09 | 1 | DEFAULT | - | - | COLOSSEUM |
| TEST_HE_COLOSSEUM2 |  | he09 | 1 | DEFAULT | - | - | COLOSSEUM |
| TEST_HE_COLOSSEUM3 |  | he09 | 1 | DEFAULT | - | - | COLOSSEUM |
| ZZ_HE09_MS201 |  | he09 | 2 | DEFAULT | - | - | - |

**al Agrabah** (21 missions, 8 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| AL00_MS101 | 0x40 | al00 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| AL00_SKATE_01 | 0x12D | al00 | 2 | - | - | Counterx2,Timer | SKATE |
| AL00_SKATE_02 | 0x12E | - | 0 | - | - | - | SKATE |
| AL03_MS103 | 0x44 | al03 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| AL05_MS203 | 0x45 | al05 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| AL09_GIMMICK | 0x41 | al09 | 1 | - | boss,showWeapon,hideMap | - | GIMMICK |
| AL10_KINOKO_LEX | 0x1A2 | al10 | 1 | - | place,retry | Timer,Watch | KINOKO |
| AL10_MS102 | 0x43 | al10 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter | - |
| AL13_TRAP | 0x42 | al13 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | Timer | TRAP |
| AL13_TRAP_FREE | 0x9B | al13 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | Timer | FREE TRAP |
| AL13_TRAP_FREE2 | 0xF6 | al13 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | Timer | FREE TRAP |
| AL14_MS201A | 0x23 | al14 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| AL14_MS201B | 0x24 | al14 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| AL14_MS202 | 0xE2 | al14 | 3 | W_FRIEND | noPrize,hideMap | - | - |
| AL14_MS202_FREE | 0x16F | al14 | 1 | W_FRIEND | noPrize,hideMap | Counterx2 | FREE |
| AL14_MS_K | 0x2A | al14 | 1 | - | showWeapon | - | - |
| AL14_MS_L | 0x2B | al14 | 1 | - | showWeapon,noPrizebox,retry | - | - |
| AL14_MS_M | 0x2C | al14 | 1 | - | showWeapon,noPrizebox,retry | - | - |
| AL14_MS_O | 0x2E | al14 | 2 | - | retry | Counter | - |
| AL14_MS_P | 0x2F | al14 | 3 | W_FRIEND | showWeapon | Timer | - |
| AL14_MS_S | 0x12B | - | 0 | - | retry | Counter | - |

**mu The Land of Dragons** (16 missions, 1 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| MU01_MS101 | 0x54 | mu01 | 1 | W_FRIEND_FIX | boss,noLeave,hideMap | - | - |
| MU01_MS102 | 0x55 | mu01 | 1 | W_FRIEND_FIX | boss,noLeave,noPrize,hideMap | Gauge | - |
| MU01_MS103C | 0x58 | mu01 | 3 | W_FRIEND_FIX | boss,noLeave,noPrize,hideMap | Counter,Gauge | - |
| MU02_MS103A | 0x56 | mu02 | 1 | W_FRIEND_FIX | boss,noLeave,noPrize,hideMap | Counter,Gauge | - |
| MU02_MS103B | 0x57 | mu02 | 1 | W_FRIEND_FIX | boss,noLeave,noPrize,hideMap | Gauge | - |
| MU03_MS104 | 0x59 | mu03 | 1 | W_FRIEND_FIX | noPrize | Gauge | - |
| MU05_MS105 | 0x5A | mu05 | 1 | W_FRIEND_ONLY | boss,noLeave,noPrizebox,hideMap | - | - |
| MU07_MS106 | 0x5B | mu07 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Timer | - |
| MU07_MS201 | 0x5E | mu07 | 2 | NO_FRIEND | boss,showWeapon,noPrizebox,hideMap | - | - |
| MU08_MS107 | 0x5C | mu08 | 2 | NO_FRIEND W_FRIEND | boss,noLeave,noPrizebox | - | - |
| MU08_MS202 | 0x5F | mu08 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| MU08_MS204 | 0x18 | mu08 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey | - | - |
| MU09_KINOKO_VEX | 0x1A1 | mu09 | 1 | - | place,retry | Counterx2 | KINOKO |
| MU09_MS108 | 0x5D | mu09 | 1 | W_FRIEND | boss,noLeave,noPrize,hideMap,mickey | Gauge | - |
| MU10_MS203 | 0x60 | mu10 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TEST_MU07_MS999 |  | mu07 | 1 | NO_FRIEND | - | - | - |

**po 100 Acre Wood** (16 missions, 5 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| PO01_MS500 |  | po01 | 1 | - | - | - | - |
| PO01_MS501 | 0x37 | po01 | 1 | - | noPrize,hideMap | Counter,Gauge | - |
| PO01_MS501_FREE | 0x103 | po01 | 1 | - | noPrize,hideMap | Counterx2,Gauge | FREE |
| PO06_MS100 |  | po06 | 1 | - | - | - | - |
| PO06_MS101 | 0x03 | po06 | 2 | - | noPrize,hideMap | Timer | - |
| PO06_MS101_FREE | 0xFF | po06 | 1 | - | noPrize,hideMap | Counterx2 | FREE |
| PO07_MS200 |  | po07 | 1 | - | - | - | - |
| PO07_MS201 | 0x04 | po07 | 2 | - | noPrize,hideMap | Counter | - |
| PO07_MS201_FREE | 0x100 | po07 | 1 | - | noPrize,hideMap | Counterx2 | FREE |
| PO08_MS300 |  | po08 | 1 | - | - | - | - |
| PO08_MS301 | 0x05 | po08 | 1 | - | noPrize,hideMap | Counter,Timer | - |
| PO08_MS301_FREE | 0x101 | po08 | 1 | - | noPrize,hideMap | Counterx3 | FREE |
| PO09_MS400 |  | po09 | 1 | - | - | - | - |
| PO09_MS401 | 0x39 | po09 | 2 | - | noPrize | Gauge,Timer | - |
| PO09_MS401_FREE | 0x102 | po09 | 1 | - | noPrize | Gauge,Timer,Watch | FREE |
| TEST_PO08_MS300 |  | po08 | 1 | - | - | - | - |

**lk Pride Lands** (5 missions, 0 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| LK02_MS102 | 0x6A | lk02 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter,Gauge | - |
| LK05_MS101 | 0x69 | lk05 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| LK05_MS201 | 0x6C | lk05 | 1 | W_FRIEND_FIX | boss,showWeapon,noLeave,noPrizebox,hideMap | Counter | - |
| LK14_MS103 | 0x6B | lk14 | 1 | W_FRIEND_FIX | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| LK15_MS202 | 0x11B | lk15 | 1 | W_FRIEND_ONLY | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |

**lm Atlantica** (12 missions, 5 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| LM01_MS201 | 0x154 | lm01 | 1 | - | - | - | - |
| LM01_MS201_FREE | 0x159 | lm01 | 1 | - | - | - | FREE |
| LM02_MS101 | 0x3E | lm02 | 1 | - | noPrize | - | - |
| LM02_MS102 | 0x152 | lm02 | 1 | - | - | - | - |
| LM03_MS301 | 0x155 | lm03 | 1 | - | - | - | - |
| LM03_MS301_FREE | 0x15A | lm03 | 1 | - | - | - | FREE |
| LM04_MS103 | 0x153 | lm04 | 1 | - | - | - | - |
| LM04_MS103_FREE | 0x158 | lm04 | 1 | - | - | - | FREE |
| LM04_MS501 | 0x157 | lm04 | 1 | - | - | - | - |
| LM04_MS501_FREE | 0x15C | lm04 | 1 | - | - | - | FREE |
| LM09_MS401 | 0x156 | lm09 | 1 | - | - | - | - |
| LM09_MS401_FREE | 0x15B | lm09 | 1 | - | - | - | FREE |

**dc Disney Castle** (5 missions, 1 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| DC00_MS101 | 0x61 | dc00 | 3 | NO_FRIEND | boss,showWeapon,noPrizebox,hideMap | Gauge | - |
| DC02_MS100 | 0xA1 | dc02 | 1 | - | noPrizebox,retry | Gauge | - |
| DC02_MS101 | 0xF5 | dc02 | 1 | - | noPrizebox,retry | Gauge | - |
| DC02_MS102 | 0xF7 | dc02 | 1 | - | retry | - | - |
| DC07_FM_NAZO | 0x19A | dc07 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | FM NAZO |

**wi Timeless River** (8 missions, 1 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| WI01_MS101 | 0x62 | wi01 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| WI02_KINOKO_MAR | 0x1A8 | wi02 | 1 | - | place,retry | Timer,Watch | KINOKO |
| WI02_MS103 | 0x67 | wi02 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| WI03_MS104 | 0x68 | wi03 | 1 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| WI04_MS102C | 0x65 | wi04 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| WI05_MS102D | 0x66 | wi05 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| WI06_MS102B | 0x64 | wi06 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| WI07_MS102A | 0x63 | wi07 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |

**nm Halloween Town** (12 missions, 4 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| NM00_MS101 | 0x6E | nm00 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | Gauge | - |
| NM00_MS202 | 0x73 | nm00 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrize,hideMap | Counter | - |
| NM03_MS103 | 0x70 | nm03 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| NM06_MS102 | 0x6F | nm06 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| NM07_KINOKO_XIG | 0x19F | nm07 | 1 | - | place,retry | Counterx2 | KINOKO |
| NM07_MS204 | 0x75 | nm07 | 2 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| NM09_MS104 | 0x71 | nm09 | 3 | W_FRIEND | boss,showWeapon,noPrizebox,hideMap | - | - |
| NM09_SKATE_01 | 0x132 | nm09 | 1 | - | - | Counterx2,Timer | SKATE |
| NM09_SKATE_02 | 0x133 | - | 0 | - | - | - | SKATE |
| NM10_MS201 | 0x72 | nm10 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | Counter | - |
| NM10_MS203 | 0x74 | nm10 | 1 | W_FRIEND | boss,noPrize,hideMap | Counterx2 | - |
| NM10_MS203_FREE | 0x119 | nm10 | 1 | W_FRIEND | showWeapon,noLeave,noPrize,hideMap | Counterx3,Timer | FREE |

**wm World Map** (1 missions, 1 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| WORLDMAP | 0x0C | wm00 | 15 | - | noPrizebox | - | WORLDMAP |

**ca Port Royal** (20 missions, 9 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| CA01_MS101 | 0x76 | ca01 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Counter,Gauge,Timer | - |
| CA01_MS102 | 0x77 | ca01 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| CA01_MS201 | 0x7D | ca01 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| CA01_MS204 | 0x80 | ca01 | 1 | W_FRIEND | boss,noLeave,noPrize,hideMap | Counterx3 | - |
| CA02_MS103 | 0x78 | ca02 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| CA02_SKATE_01 | 0x12F | ca02 | 1 | - | - | Counter,Timer,Watch | SKATE |
| CA03_MS106 | 0x7B | ca03 | 1 | W_FRIEND_FIX | boss,noPrizebox,hideMap | Counter | - |
| CA07_MS105 | 0x7A | ca07 | 1 | DEFAULT | boss,noLeave,noPrize,hideMap | Timer | - |
| CA09_MEDAL | 0xDB | ca09 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA09_MS104 | 0x79 | ca09 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | Timer | - |
| CA10_MEDAL | 0xDE | ca10 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA10_MS107 | 0x7C | ca10 | 1 | W_FRIEND_FIX | boss,noLeave,noPrizebox,hideMap | - | - |
| CA12_MEDAL | 0xDC | ca12 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA13_KINOKO_LUX | 0x1A7 | ca13 | 1 | - | place,retry | Timer,Watch | KINOKO |
| CA13_MEDAL | 0xDD | ca13 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA14_MEDAL | 0xDF | ca14 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA14_MS203 | 0x7F | ca14 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| CA15_MEDAL | 0xE0 | ca15 | 1 | W_FRIEND | noLeave,noPrize | Counter,Timer | MEDAL |
| CA18_MS202 | 0x12C | ca18 | 1 | W_FRIEND | boss,noPrizebox,hideMap,mickey | - | - |
| SHIP_BATTLE | 0xE1 | ca18 ca19 ca20 ca21 ca22 | 15 | DEFAULT W_FRIEND W_FRIEND_FIX | noLeave | - | SHIP_BATTLE |

**tr Space Paranoids** (12 missions, 2 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| A_SCT_GIMMICK | 0x114 | tr00 | 1 | - | noPrize | Gauge | GIMMICK |
| TR01_MS101 | 0x83 | tr01 | 1 | W_FRIEND | noPrize,hideMap | Gauge,Timer | - |
| TR02_MS102A | 0x32 | tr02 | 3 | NO_FRIEND W_FRIEND_FIX | boss,hideMap | Counter | - |
| TR02_MS102B | 0x33 | tr02 | 1 | NO_FRIEND | boss,noPrize,hideMap | - | - |
| TR02_MS102_FREE | 0x34 | tr02 | 2 | W_FRIEND_FIX | boss,noPrize,hideMap | Counterx2 | FREE |
| TR02_MS210 | 0x86 | tr02 | 1 | DEFAULT | boss,noLeave,noPrizebox,hideMap | - | - |
| TR03_MS103 | 0x84 | tr03 | 1 | W_FRIEND | boss,noPrize,hideMap | Gauge,Timer | - |
| TR04_MS104 | 0x85 | tr04 | 1 | W_FRIEND | boss,noLeave,noPrize,hideMap | Gauge | - |
| TR04_MS202 | 0x87 | tr04 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| TR07_MS203 | 0x88 | tr07 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | Gauge | - |
| TR09_MS204 | 0x89 | tr09 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap | - | - |
| TR09_MS205 | 0x8A | tr09 | 2 | W_FRIEND W_FRIEND_FIX | boss,noLeave,noPrizebox,hideMap | - | - |

**eh World That Never Was** (16 missions, 2 flagged by name)

| Mission | Id | Rooms | Programs | Party | Flags | Meters | Name flag |
|---|---|---|---|---|---|---|---|
| EH03_KINOKO_XEM | 0x19E | eh03 | 1 | - | place,retry | Counterx2,Timer | KINOKO |
| EH10_MS102 | 0xC7 | eh10 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap,noSummon | - | - |
| EH14_MS103 | 0xC8 | eh14 | 2 | NO_FRIEND | boss,noLeave,noPrizebox,hideMap | Gaugex2 | - |
| EH15_MS104 | 0xC9 | eh15 | 2 | DEFAULT | boss,showWeapon,noLeave,noPrizebox,hideMap | Gauge | - |
| EH19_MS105 | 0xCA | eh19 | 2 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| EH20_MS113 | 0x111 | eh20 | 1 | W_FRIEND_ONLY | boss,showWeapon,noLeave,noPrize,hideMap,retry | - | - |
| EH20_MS113_RE | 0x1BA | eh20 | 1 | W_FRIEND_ONLY | boss,showWeapon,noLeave,noPrize,hideMap | - | RE |
| EH21_MS101 | 0xEF | eh21 | 2 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap | - | - |
| EH22_MS111 | 0x10F | eh22 | 1 | NO_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,retry | Gauge | - |
| EH23_MS112 | 0x110 | eh23 | 1 | W_FRIEND_ONLY | boss,noDrive,showWeapon,noLeave,noPrizebox,hideMap,retry | - | - |
| EH24_MS110 | 0x10E | eh24 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,mickey,retry | - | - |
| EH25_MS109 | 0x10D | eh25 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap,retry | - | - |
| EH26_MS108 | 0x10C | eh26 | 2 | W_FRIEND | boss,noLeave,noPrizebox,hideMap,retry | Gaugex3,Timer | - |
| EH27_MS106 | 0x112 | eh27 | 1 | W_FRIEND | boss,showWeapon,noLeave,noPrizebox,hideMap,noSummon | - | - |
| EH28_MS107 | 0x10B | eh28 | 1 | W_FRIEND | boss,noLeave,noPrizebox,hideMap,noSummon | - | - |
| TEST_EH22_MS111 |  | eh22 | 1 | NO_FRIEND | - | - | - |

## 5. Drive Forms, Limits and Summons

### 5a. Drive Forms

VERIFIED: `03system.bin`, table `cmd` (command list), entries with the Form icon; names looked up by message id in the English pack. `Argument` is the form number.

| Command id | Name | Argument | Cost | Flags | DisableForm mask |
|---|---|---|---|---|---|
| 4 | Drive | 4 | 0 | Cursor,Battle,Drive,DisableSkateboard | 65534 |
| 5 | Revert | 5 | 0 | Cursor,Battle,Secure,Drive,DisableSkateboard | 0 |
| 6 | Valor Form | 1 | 3 | Cursor,Battle,Drive,DisableSkateboard | 0 |
| 7 | Wisdom Form | 2 | 3 | Cursor,Battle,Drive,DisableSkateboard | 0 |
| 11 | Master Form | 4 | 4 | Cursor,Battle,Drive,DisableSkateboard | 0 |
| 12 | Final Form | 5 | 5 | Cursor,Battle,Drive,DisableSkateboard | 0 |
| 13 | Anti Form | 6 | 9 | Cursor,Battle,Drive,DisableSkateboard | 0 |
| 605 | Drive? | 605 | 0 | Cursor,Battle,Drive | 0 |
| 673 | Limit Form | 3 | 4 | Cursor,Battle,Drive,DisableSkateboard | 65534 |

- **Could not be read from the data:** which friends a form uses up. No field of the command table names Donald or Goofy, and `fmlv` (form levels) only lists experience and abilities per form (rows per form: AntiForm 3, Final 7, Limit 7, Master 7, Summon 7, Valor 7, Wisdom 7). HYPOTHESIS: the friend requirement is in the game program, not in these tables. Lanes that test Drive Forms must find it there.
- VERIFIED: the party table (3b) gives a separate object for every form in every world row, so a twin in a form needs that object too (memory: see the plan's risk about two forms at once).
- VERIFIED: 14 missions have the "Drive disabled" bit: EH23_MS112, HE_COLOSSEUM_3, HE_COLOSSEUM_7, HE_COLOSSEUM_8_TIT, HE_COL_8TI_BOSS, TT04_MS00, TT04_MS01, TT04_MS02, TT06_BAGGAGE_02, TT06_LETTER_02, TT06_PERFORM_02, TT07_CLEAN_02, TT07_POSTER_02, TT07_WORM_02.
- VERIFIED: 10 missions set a Drive refill ratio: HE_COLOSSEUM_2 (10.0), HE_COLOSSEUM_2_FOG (10.0), HE_COLOSSEUM_6 (10.0), HE_COLOSSEUM_6_FOG (10.0), HE_COLOSSEUM_8_CEL (10.0), HE_COL_2_10 (10.0), HE_COL_6_10 (10.0), HE_COL_8_31 (10.0), HE_COL_8_35 (10.0), HE_COL_8_40 (10.0). The OpenKH notes say this op-code also decides whether Sora can use the other forms when alone (not checked here).
- VERIFIED: command flags exist that switch a command off for one kind of player: DisableLimitForm on 347 commands, DisableLionSora on 332 commands, DisableRoxas on 318 commands, DisableSkateboard on 357 commands, DisableSora on 28 commands. So Roxas, lion Sora, Limit Form and the skateboard already have their own allowed command sets in data; a twin of those inherits the same limits.

### 5b. Limits

VERIFIED: `00battle.bin`, table `limt`. `Character` is who the limit belongs to and `Summon` the partner the table names (the field names are OpenKH's). World 13 rows are the Timeless River versions.

| Id | Character | Partner field | Group | File | Command | Command name | World |
|---|---|---|---|---|---|---|---|
| 0 | Auron | Sora | 0 | auron.bar | 82 | Bushido | 0 |
| 1 | Beast | Sora | 0 | beast.bar | 74 | Twin Howl | 0 |
| 2 | Mulan | Sora | 0 | mulan.bar | 139 | Red Rocket | 0 |
| 3 | Goofy | Sora | 0 | goofy_wi.bar | 255 | Whirli-Goof | 13 |
| 3 | Goofy | Sora | 0 | goofy.bar | 255 | Whirli-Goof | 0 |
| 4 | Goofy | Sora | 0 | goofy2_wi.bar | 338 | Knocksmash | 13 |
| 4 | Goofy | Sora | 0 | goofy2.bar | 338 | Knocksmash | 0 |
| 5 | Donald | Sora | 0 | donald_wi.bar | 282 | Comet | 13 |
| 5 | Donald | Sora | 0 | donald.bar | 282 | Comet | 0 |
| 6 | Donald | Sora | 0 | donald2_wi.bar | 344 | Duck Flare | 13 |
| 6 | Donald | Sora | 0 | donald2.bar | 344 | Duck Flare | 0 |
| 7 | Aladdin | Sora | 0 | aladdin.bar | 351 | Speedster | 0 |
| 8 | JackSparrow | Sora | 0 | sparrow.bar | 357 | Bluff | 0 |
| 9 | Simba | Sora | 0 | simba.bar | 376 | Wildcat | 0 |
| 10 | JackSkellington | Sora | 0 | jack.bar | 405 | Dance Call | 0 |
| 11 | Tron | Sora | 0 | tron.bar | 415 | Setup | 0 |
| 12 | Riku | Sora | 0 | riku.bar | 569 | Session | 0 |
| 13 | Sora | Donald | 3 | trinity_wi.bar | 484 | Trinity | 13 |
| 13 | Sora | Donald | 3 | trinity.bar | 484 | Trinity | 0 |
| 13 | Sora | None | 0 | trinity_zz.bar | 620 | Trinity | 0 |
| 14 | Sora | PeterPan | 0 | peterpan.bar | 468 | Never Land | 0 |
| 15 | Sora | Stitch | 0 | stitch.bar | 519 | Ohana! | 0 |
| 16 | Sora | ChickenLittle | 0 | chickenlittle.bar | 529 | FPS Mode | 0 |
| 17 | Sora | Genie | 0 | genie_brave.bar | 542 | Sonic | 0 |
| 18 | Sora | Genie | 0 | genie_wisdom.bar | 544 | Strike | 0 |
| 19 | Sora | Genie | 0 | genie_master.bar | 546 | Arcana | 0 |
| 20 | Sora | Genie | 0 | genie_final.bar | 548 | Ragnarok | 0 |
| 21 | Sora | None | 0 | sonic_rave.bar | 698 | Sonic Blade | 0 |
| 22 | Sora | None | 0 | last_alcanam.bar | 701 | Ars Arcanum | 0 |
| 23 | Sora | None | 0 | strike_raid.bar | 704 | Strike Raid | 0 |
| 24 | Sora | None | 0 | ragnarok.bar | 683 | Ragnarok | 0 |

HYPOTHESIS: every limit pairs exactly two named characters (Sora plus one partner; Trinity names Donald and has group 3). With two players, the data gives no rule for which player is the "Sora" of a limit; that is our design choice (the user decided: either player can start one).
VERIFIED: 10 missions set their own limit cost: HE_COLOSSEUM, HE_COLOSSEUM_8_PP, HE_COL_1_10, HE_COL_1_8, HE_COL_5, HE_COL_5_10, HE_COL_5_8, HE_COL_8PP_BOSS, HE_COL_8_25, HE_COL_8_30.

### 5c. Summons

VERIFIED: `00battle.bin`, table `sumn`, and the Summon-icon commands in `cmd`.

| Command | Name | Item | Entity 1 | Entity 2 | Limit command | Limit name |
|---|---|---|---|---|---|---|
| 447 | Chicken Little | 383 | P_EX350 | - | 529 | FPS Mode |
| 89 | Genie | 159 | P_AL010 | - | 609 | ? |
| 88 | Stitch | 25 | N_HB040_BTL | - | 519 | Ohana! |
| 306 | Peter Pan | 160 | P_EX330 | P_EX340 | 468 | Never Land |

VERIFIED: 3 missions have "Summon disabled"; 13 have "free summon (summon alone)": HE_COLOSSEUM_3, HE_COLOSSEUM_7, HE_COLOSSEUM_8_TIT, HE_COL_4_1, HE_COL_4_10, HE_COL_4_2, HE_COL_4_3, HE_COL_4_4, HE_COL_4_5, HE_COL_4_6, HE_COL_4_7, HE_COL_4_9, HE_COL_8TI_BOSS.
**Could not be read:** which friends a summon replaces. HYPOTHESIS: also in the game program.

### 5d. Friend commands

VERIFIED: commands with the Friend icon in `cmd` (the party-swap menu).

| Command id | Name | Argument | Flags |
|---|---|---|---|
| 73 | Party | 73 | Cursor,Land,Battle |
| 92 | Donald | 92 | Cursor,Land,Battle |
| 93 | Goofy | 93 | Cursor,Land,Battle |
| 94 | Auron | 94 | Cursor,Land,Battle |
| 95 | Ping | 95 | Cursor,Land,Battle |
| 96 | Mulan | 96 | Cursor,Land,Battle |
| 98 | Jack | 98 | Cursor,Land,Battle |
| 99 | Beast | 99 | Cursor,Land,Battle |
| 100 | Jack | 100 | Cursor,Land,Battle |
| 101 | Simba | 101 | Cursor,Land,Battle |
| 102 | Tron | 102 | Cursor,Land,Battle |
| 114 | Aladdin | 114 | Cursor,Land,Battle |
| 180 | Riku | 180 | Cursor,Land,Battle |

## 6. Other data that singles out "the player"

Counts only; each is something a second player has to share or trigger too.

| What | Count | Detail | Why it matters for two players |
|---|---|---|---|
| Entities with a non-zero `ReactionCommand` field | 1311 | 1225 different values; by object type: RTN 940, F_OBJ 347, G_OBJ 20, BTLNPC 3, NPC 1 | HYPOTHESIS: an individual id (which talk text, which chest), i.e. the things a player presses Triangle on; player 2 must be able to use them too |
| Event activators (trigger volumes) | 6572 | type 0: 6393, type 1: 70, 28 other types: 109 | room exits, event starts: the "both players at the exit" rule lives here |
| Spawn points with a teleport target | 1381 | of 5615 spawn points | where a room change sends the party |
| `SetJump` commands | 2320 | event scripts | scripted room changes after events |
| `SetEvent` commands | 1639 | event scripts | cutscene starts; the twin must be hidden or placed |
| `Mission` commands | 477 | battle scripts | mission rules apply to both players |
| `Capacity` commands | 465 |  | HYPOTHESIS: memory budget for a room; a twin adds load |
| `Camera` commands | 44 |  | fixed or special cameras |
| `BarrierFlag` commands | 203 |  | HYPOTHESIS: battle walls that lock the room |
| `MsgWall` commands | 80 |  | invisible walls with a message |
| `SetInventory` commands | 92 |  | items given or taken by script |
| `SetMenuFlag` commands | 34 |  | menu parts switched on or off |
| Walk paths / return parameters / signals | 872 / 8027 / 143 | spawn data | enemy and NPC behaviour hooks |

VERIFIED counts from `ard\*.ard`; the "why" column is my reading (HYPOTHESIS) unless marked otherwise.

## 7. What this list cannot tell

- 6 script or spawn entries could not be decoded by the OpenKH reader and are not counted: al08:m_00, al08:m_10, al08:m_11, al08:m_20, po10:m_00, po10:m_10.
- Which program runs when: the scripts are selected by story progress in memory. This list shows every program that exists, not the order the story uses them.
- Anything decided inside the game program instead of data: who a Drive Form or Summon uses up, how enemies choose a target, what the camera follows. Those belong to lanes A and B.
- Meanings marked HYPOTHESIS come from field and command names, not from tests.
- Text for room names and commands comes from the English pack; the ids come from the Japanese disc.

