# The mission sweep: every mission program of the game once, with two heroes

Made by `python -I tools\own\sweep_doc.py` from the logs in `local\sweep`. Method and limits: `docs\STATE.md`,
seventh round, part 7b. Story order and row names are those of `docs\PARITY-CHECKLIST.md`.

How to read a line: `f5200: 17/20 / 15/20, two views` = at session frame 5200 player 1's hero has 17 of 20 HP,
player 2's hero 15 of 20, and each PC shows its own view. `none` = that player has no hero at that moment.
Every run: two linked emulators, 9,000 frames, level 1 heroes with 20 HP, player 1 presses Circle now and then,
player 2 presses Circle all the time. A run proves that the mission STARTS and RUNS with two heroes in sync;
it does not play a mission to its end.

## Totals (346 mission programs and cup blocks with a result or in the first list)

| Class | Programs | Meaning |
|---|---|---|
| OK | 269 | works: both heroes there, in sync, 0 fault lines |
| SHARED | 27 | one hero, both controllers drive him (twenty-eighth glue) |
| OK-V5 | 18 | works with disc v5: player 2 has his own special object |
| CUP-LOBBY | 13 | a cup round that was over before the first probe point (level 1 heroes); both heroes then stand in the cup lobby with two views, in sync |
| TEST-LIMIT | 10 | cannot be started by a jump test (see the note) |
| OK-GAME | 9 | works with two heroes; its fault lines are there with no patch too (the game's own in this test start) |

## 1. Twilight Town: Roxas's prologue

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| TTR-01 | `TT07_MS101` | tt07 95 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-01 | `TT07_MS103` | tt07 97 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-01 | `TT07_MS105` | tt07 99 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-01 | `TT02_MS201` | tt02 2 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-01 | `TT32_MS303` | tt32 155 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-01 | `TT04_MS106` | tt04 76 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-02 | `TT03_MS400` | tt03 180 | OK | 0 | f5200: 18/20 / 18/20, two views; f7000: 6/20 / 18/20, two views; f8900: 0/20 / 15/20, two views |  |
| TTR-02 | `TT04_MS107` | tt04 77 | OK | 0 | f5200: none / none; f7000: 20/20 / 19/20, two views; f8900: none / none |  |
| TTR-02 | `TT04_MS108` | tt04 78 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: room 0D02 |  |
| TTR-02 | `TT04_MS500` | tt04 181 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 14/20 / 16/20, two views; f8900: 2/20 / 16/20, two views |  |
| TTR-03 | `TT06_LETTER_01` | tt06 192 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-03 | `TT06_LETTER_02` | tt06 195 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-03 | `TT06_WORK_LETTER` | tt06 91 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-04 | `TT06_BAGGAGE_01` | tt06 190 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-04 | `TT06_BAGGAGE_02` | tt06 193 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-04 | `TT06_WORK_BAGGAGE` | tt06 89 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-05 | `TT06_PERFORM_01` | tt06 191 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-05 | `TT06_PERFORM_02` | tt06 194 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-05 | `TT06_WORK_PERFORM` | tt06 90 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-06 | `TT07_POSTER_01` | tt07 198 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-06 | `TT07_POSTER_02` | tt07 201 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-06 | `TT07_WORK_POSTER` | tt07 102 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-07 | `TT07_WORM_01` | tt07 197 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-07 | `TT07_WORM_02` | tt07 200 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-07 | `TT07_WORK_WORM` | tt07 101 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-08 | `TT07_CLEAN_01` | tt07 196 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-08 | `TT07_CLEAN_02` | tt07 199 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-08 | `TT07_WORK_CLEAN` | tt07 100 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-09 | `TT05_MS401` | tt05 189 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 0/20 / 17/20, two views; f8900: 0/20 / 14/20, two views |  |
| TTR-09 | `TT05_MS401` | tt05 84 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 20/20 / 17/20, two views; f8900: none / none |  |
| TTR-09 | `TT05_MS402` | tt05 85 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 17/20, two views; f8900: none / none |  |
| TTR-09 | `TT05_MS405` | tt05 88 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 20/20 / 0/20, two views; f8900: none / none |  |
| TTR-10 | `TT03_MS601` | tt03 73 | OK | 0 | f5200: 17/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 20/20, two views |  |
| TTR-10 | `TT05_MS403` | tt05 86 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: none / none; f8900: none / none |  |
| TTR-10 | `TT04_MS301` | tt04 79 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: none / none; f8900: room 2002 |  |
| TTR-10 | `TT14_MS109` | tt14 127 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: none / none; f8900: none / none |  |
| TTR-10 | `TT14_MS110` | tt14 128 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: room 0202; f8900: room 0202 |  |
| TTR-10 | `TT19_MS602` | tt19 134 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 2/20 / 20/20, two views; f8900: 0/20 / 15/20, two views |  |
| TTR-11 | `TT05_MS404` | tt05 87 | OK | 0 | f5200: 15/20 / 20/20, two views; f7000: 12/20 / 0/20, two views; f8900: 20/20 / 20/20 |  |
| TTR-11 | `TT20_MS603` | tt20 137 | OK | 0 | f5200: 16/20 / 9/20, two views; f7000: 4/20 / 7/20, two views; f8900: 0/20 / 2/20, two views |  |
| TTR-12 | `TT10_WORK_TIMBER` | tt10 120 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-12 | `TT36_WORK_FIGURE` | tt36 159 | OK | 0 | f5200: 18/20 / 20/20, two views; f7000: 16/20 / 20/20, two views; f8900: 11/20 / 20/20, two views |  |
| TTR-12 | `TT10_WORK_MIRROR` | tt10 121 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 20/20, two views |  |
| TTR-13 | `TT12_WORK_BOX` | tt12 125 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTR-14 | `TT32_MS302` | tt32 154 | OK | 0 | f5200: 17/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 20/20, two views |  |
| TTR-15 | `TT34_MS304` | tt34 157 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 15/20 / 15/20, two views; f8900: 12/20 / 9/20, two views |  |

## 2. Twilight Town: Sora's visits

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| TTS-01 | `TT08_MS701` | tt08 108 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 16/20 / 20/20, two views; f8900: none / none |  |
| TTS-02 | `TT25_MS801` | tt25 149 | OK | 0 | f5200: 18/20 / 20/20, two views; f7000: none / none; f8900: room 1A02 |  |
| TTS-02 | `TT29_MS802` | tt29 152 | OK | 0 | f5200: 18/20 / 18/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTS-02 | `TT30_MS803` | tt30 153 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 10/20, two views |  |
| TTS-03 | `TT04_MS901` | tt04 80 | OK | 0 | f5200: 14/20 / 20/20, two views; f7000: 11/20 / 17/20, two views; f8900: 16/20 / 20/20, two views |  |
| TTS-04 | `TT14_MS001` | tt14 166 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTS-04 | `TT14_MS001` | tt41 186 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 16/20 / 16/20, two views; f8900: 16/20 / 6/20, two views |  |
| TTS-05 | `TT40_MS002` | tt40 160 | OK | 0 | f5200: 17/20 / 20/20, two views; f7000: none / none; f8900: none / none |  |
| TTS-05 | `TT40_MS003` | tt40 161 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 12/20 / 11/20, two views; f8900: 3/20 / 8/20, two views |  |
| TTS-06 | `TT04_MS00` | tt04 182 | OK | 0 | f5200: 20/20 / 19/20, two views; f7000: 20/20 / 10/20, two views; f8900: 20/20 / 6/20, two views |  |
| TTS-06 | `TT04_MS01` | tt04 183 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 8/20, two views; f8900: 20/20 / 1/20, two views |  |
| TTS-06 | `TT04_MS02` | tt04 184 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TTS-07 | `TT07_SKATE_01` | tt07 187 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |

## 3. Hollow Bastion / Radiant Garden

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| HB-01 | `HB08_MS102` | hb08 91 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-01 | `HB08_MS102` | hb08 52 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 10/20 / 20/20, two views; f8900: 0/20 / 20/20, two views |  |
| HB-02 | `HB09_MS101` | hb09 51 | OK | 0 | f5200: 16/20 / 17/20, two views; f7000: none / none; f8900: none / none |  |
| HB-02 | `HB09_MS501` | hb09 72 | OK | 0 | f5200: 17/20 / 13/20, two views; f7000: none / none; f8900: room 0D04 |  |
| HB-02 | `HB09_MS901` | hb09 58 | OK | 0 | f5200: 16/20 / 19/20, two views; f7000: none / none; f8900: room 0009 |  |
| HB-03 | `HB13_MS902` | hb13 101 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-04 | `HB20_MS401` | hb20 86 | OK | 0 | f5200: 20/20 / 12/20, two views; f7000: 6/20 / 13/20, two views; f8900: 17/20 / 11/20, two views |  |
| HB-04 | `HB07_MS402` | hb18 73 | OK | 0 | f5200: 17/20 / 14/20, two views; f7000: 19/20 / 10/20, two views; f8900: 0/20 / 11/20, two views |  |
| HB-05 | `HB04_MS403` | hb04 55 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 0/20 / 6/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-05 | `HB04_MS403` | hb04 114 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: the New Game room (after a Continue); f8900: 18/20 / 20/20, two views |  |
| HB-06 | `HB16_MS404A` | hb16 62 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 0/20 / 18/20, two views; f8900: 6/20 / 13/20, two views |  |
| HB-06 | `HB16_MS404B` | hb16 63 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-06 | `HB16_MS404C` | hb16 64 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-06 | `HB16_MS404D` | hb16 65 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-07 | `HB17_MS405` | hb17 85 | OK | 0 | f5200: 4/20 / 15/20, two views; f7000: 0/20 / 15/20, two views; f8900: 0/20 / 15/20, two views |  |
| HB-07 | `HB17_MS405` | hb17 66 | OK | 0 | f5200: 3/20 / 13/20, two views; f7000: 0/20 / 13/20, two views; f8900: 0/20 / 13/20, two views |  |
| HB-08 | `HB01_MS601` | hb01 75 | TEST-LIMIT | 0 | f5200: none / none; f7000: the New Game room (after a Continue); f8900: the New Game room (after a Continue) | as hb33 148 (swc-HB01_MS601-75: with no patch the game stops at Continue) |
| HB-09 | `HB09_SKATE_01` | hb09 99 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HB-09 | `HB09_SKATE_01` | hb09 100 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |

## 4. The Land of Dragons

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| MU-01 | `MU01_MS101` | mu01 67 | OK | 0 | f5200: 18/20 / 18/20, two views; f7000: 19/20 / 20/20, two views; f8900: 19/20 / 20/20, two views |  |
| MU-02 | `MU01_MS102` | mu01 68 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 16/20 / 20/20, two views; f8900: 16/20 / 20/20, two views |  |
| MU-02 | `MU01_MS103C` | mu01 70 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 14/20 / 20/20, two views; f8900: none / none |  |
| MU-02 | `MU01_MS103C` | mu01 102 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: none / none |  |
| MU-02 | `MU01_MS103C` | mu01 100 | OK-GAME | 50 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: other] | both heroes, two views, the mission runs. Its 50 fault lines are there WITH NO PATCH, the same places and counts (swc-MU01_MS103C-100): the game's own in this test start |
| MU-02 | `MU02_MS103A` | mu02 69 | OK | 0 | f5200: 14/20 / 20/20, two views; f7000: 17/20 / 20/20, two views; f8900: the New Game room (after a Continue) |  |
| MU-02 | `MU02_MS103B` | mu02 80 | OK | 0 | f5200: 18/20 / 20/20, two views; f7000: 8/20 / 20/20, two views; f8900: 16/20 / 20/20, two views |  |
| MU-03 | `MU03_MS104` | mu03 71 | OK | 0 | f5200: 15/20 / 13/20, two views; f7000: 10/20 / 8/20, two views; f8900: 10/20 / 8/20, two views |  |
| MU-04 | `MU05_MS105` | mu05 72 | OK | 0 | f5200: 15/20 / 16/20, two views; f7000: 9/20 / 11/20, two views; f8900: 2/20 / 4/20, two views |  |
| MU-05 | `MU07_MS106` | mu07 73 | OK | 0 | f5200: 17/20 / 14/20, two views; f7000: 11/20 / 0/20, two views; f8900: 20/20 / 17/20, two views |  |
| MU-06 | `MU08_MS107` | mu08 104 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| MU-06 | `MU08_MS107` | mu08 74 | OK | 0 | f5200: 13/20 / 13/20, two views; f7000: 10/20 / 19/20, two views; f8900: 10/20 / 19/20, two views |  |
| MU-06 | `MU08_MS202` | mu08 81 | OK | 0 | f5200: 14/20 / 11/20, two views; f7000: 8/20 / 17/20, two views; f8900: 3/20 / 5/20, two views |  |
| MU-06 | `MU10_MS203` | mu10 78 | OK | 0 | f5200: 12/20 / 20/20, two views; f7000: 16/20 / 9/20, two views; f8900: 10/20 / 9/20, two views |  |
| MU-07 | `MU09_MS108` | mu09 75 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 16/20, two views |  |
| MU-08 | `MU07_MS201` | mu07 76 | OK | 0 | f5200: 19/20 / 20/20, two views; f7000: 2/20 / 12/20, two views; f8900: 0/20 / 5/20, two views |  |
| MU-08 | `MU07_MS201` | mu07 106 | OK | 0 | f5200: 19/20 / 20/20, two views; f7000: 1/20 / 10/20, two views; f8900: 0/20 / 8/20, two views |  |
| MU-09 | `MU08_MS204` | mu08 79 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 17/20 / 17/20, two views; f8900: 11/20 / 13/20, two views |  |

## 5. Beast's Castle

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| BB-01 | `BB01_MS101` | bb01 68 | OK | 0 | f5200: 16/20 / 20/20, two views; f7000: none / none; f8900: none / none |  |
| BB-03 | `BB12_GIMMICK` | bb12 94 | TEST-LIMIT | 50 | f5200: none / none; f7000: none / none; f8900: none / none [fault lines: other] | the Beast's Castle puzzle: no hero and 50 fault lines; the NO-PATCH control has the same (sp-c-bb94: no hero, 50 lines at the same six places, pc 0x00172574 ...). The game's own in this test start |
| BB-03 | `BB12_GIMMICK` | bb12 22 | TEST-LIMIT | 50 | f5200: none / none; f7000: none / none; f8900: none / none [fault lines: other] | as bb12 94 |
| BB-04 | `BB11_MS102` | bb11 72 | OK | 0 | f5200: 15/20 / 8/20, two views; f7000: 10/20 / 15/20, two views; f8900: 10/20 / 15/20, two views |  |
| BB-04 | `BB11_MS102` | bb11 80 | OK | 0 | f5200: 15/20 / 10/20, two views; f7000: 20/20 / 13/20, two views; f8900: 11/20 / 20/20, two views |  |
| BB-05 | `BB03_MS103` | bb03 69 | OK | 0 | f5200: 14/20 / 11/20, two views; f7000: 20/20 / 17/20, two views; f8900: 6/20 / 17/20, two views |  |
| BB-06 | `BB05_MS104A` | bb05 78 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 12/20 / 12/20, two views; f8900: 19/20 / 20/20, two views |  |
| BB-07 | `BB05_MS104B` | bb05 81 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 14/20 / 17/20, two views; f8900: 11/20 / 11/20, two views | Dark Thorn, second program, with map program 79: both heroes, two views, 0 fault lines (zq1). The 6 lines of the earlier pass came from the test start (all three programs 81) |
| BB-07 | `BB05_MS104B` | bb05 79 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 8/20 / 14/20, two views; f8900: 3/20 / 14/20, two views |  |
| BB-08 | `BB04_MS201` | bb04 74 | OK | 0 | f5200: 15/20 / 17/20, two views; f7000: none / none; f8900: none / none |  |
| BB-08 | `BB00_MS202` | bb00 75 | OK | 0 | f5200: 15/20 / 15/20, two views; f7000: 17/20 / 17/20, two views; f8900: 13/20 / 14/20, two views |  |
| BB-08 | `BB00_MS202` | bb00 96 | OK | 0 | f5200: 15/20 / 15/20, two views; f7000: 16/20 / 20/20, two views; f8900: 18/20 / 20/20, two views |  |
| BB-09 | `BB15_MS203` | bb15 82 | OK | 0 | f5200: 18/20 / 6/20, two views; f7000: 9/20 / 18/20, two views; f8900: 35/60 / 0/20, two views |  |

## 6. Olympus Coliseum: story

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| HE-01 | `HE07_MS103` | he07 114 | OK | 0 | f5200: 10/20 / 15/20, two views; f7000: 9/20 / 15/20, two views; f8900: 6/20 / 15/20, two views |  |
| HE-02 | `HE05_MS102` | he05 111 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 17/20 / 11/20, two views; f8900: 14/20 / 17/20, two views |  |
| HE-03 | `HE06_MS101` | he06 112 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: none / none |  |
| HE-03 | `HE06_MS101` | he06 136 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HE-04 | `HE17_MS105` | he17 123 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 3/20 / 3/20, two views; f8900: 20/20 / 20/20 |  |
| HE-05 | `HE08_MS106` | he08 115 | OK | 0 | f5200: 15/20 / 18/20, two views; f7000: 18/20 / 18/20, two views; f8900: none / none |  |
| HE-05 | `HE08_MS107` | he08 116 | OK | 0 | f5200: 20/20 / 15/20, two views; f7000: 15/20 / 20/20, two views; f8900: 18/20 / 18/20, two views |  |
| HE-06 | `HE18_MS108` | he18 171 | OK | 0 | f5200: 15/20 / 15/20, two views; f7000: 10/20 / 16/20, two views; f8900: 11/20 / 15/20, two views |  |
| HE-07 | `HE09_MS201` | he09 124 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HE-07 | `HE09_MS202` | he09 125 | OK | 0 | f5200: 20/20 / 16/20, two views; f7000: none / none; f8900: room 0306 |  |
| HE-07 | `HE06_MS203` | he06 126 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 17/20; f8900: room 0306 |  |
| HE-08 | `HE19_MS204` | he19 201 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: room 0D06; f8900: room 0D06 |  |
| HE-08 | `HE19_MS205` | he19 202 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 15/20 / 14/20, two views; f8900: 4/20 / 11/20, two views |  |

## 7. Olympus Coliseum: Phil's training and the cups

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| HEC-00 | `HE00_MS104A` | he00 140 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-00 | `HE00_MS104A` | he00 174 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-00 | `HE00_MS104B` | he00 141 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-00 | `HE02_MS104C` | he02 142 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-00 | `HE02_MS104D` | he02 143 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-00 | `HE00_MS104` | he00 137 | OK-GAME | 19 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] |  |
| HEC-01 | `HE_COLOSSEUM` | he09 189e5 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 18/20 / 6/20, two views; f8900: room 0306 |  |
| HEC-01 | `HE_COL_1_8` | he09 189e8 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-01 | `HE_COL_1_10` | he09 189e10 | OK | 0 | f5200: 13/20 / 15/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-02 | `HE_COLOSSEUM_2` | he09 190e5 | OK | 0 | f5200: 3/20 / 0/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-02 | `HE_COLOSSEUM_2_FOG` | he09 190e8 | OK | 0 | f5200: 20/20 / 0/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-02 | `HE_COL_2_10` | he09 190e10 | OK | 0 | f5200: 20/20 / 9/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-03 | `HE_COLOSSEUM_3` | he09 191e5 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_1` | he09 192e1 | CUP-LOBBY | 2 | f5200: room 0306; f7000: room 0306; f8900: room 0306 [fault lines: other] | round over; both heroes in the lobby 0306 with two views. 2 fault lines at pc 0x001D69EC when the round goes back to the lobby (a control object's field +0xAF4 is already 0; the same place once in the no-patch control sp-c-eh58: HYPOTHESIS the game's own) |
| HEC-04 | `HE_COL_4_2` | he09 192e2 | CUP-LOBBY | 2 | f5200: room 0306; f7000: room 0306; f8900: room 0306 [fault lines: other] | as 192e1 (2 fault lines at pc 0x001D69EC) |
| HEC-04 | `HE_COL_4_3` | he09 192e3 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_4` | he09 192e4 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_5` | he09 192e5 | OK | 0 | f5200: 15/20 / 0/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_6` | he09 192e6 | CUP-LOBBY | 0 | f5200: room 0306; f7000: room 0306; f8900: room 0306 | round over; both heroes in the lobby 0306 with two views, 0 fault lines |
| HEC-04 | `HE_COL_4_7` | he09 192e7 | CUP-LOBBY | 0 | f5200: room 0306; f7000: room 0306; f8900: room 0306 | round over; both heroes in the lobby 0306 with two views at 7000 and 8900, 0 fault lines |
| HEC-04 | `HE_COL_4_8` | he09 192e8 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_9` | he09 192e9 | OK | 0 | f5200: 14/20 / 18/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-04 | `HE_COL_4_10` | he09 192e10 | OK | 0 | f5200: 10/20 / 8/20, two views; f7000: room 0306; f8900: room 0306 |  |
| HEC-05 | `HE_COL_5` | he09 193e5 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-05 | `HE_COL_5_8` | he09 193e8 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-05 | `HE_COL_5_10` | he09 193e10 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0606; f8900: room 0606 |  |
| HEC-06 | `HE_COLOSSEUM_6` | he09 194e5 | OK | 0 | f5200: 2/20 / 0/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-06 | `HE_COLOSSEUM_6_FOG` | he09 194e8 | OK | 0 | f5200: 8/20 / 0/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-06 | `HE_COL_6_10` | he09 194e10 | OK | 0 | f5200: 0/20 / 20/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-07 | `HE_COLOSSEUM_7` | he09 195e5 | CUP-LOBBY | 0 | f5200: none / none; f7000: room 0606; f8900: room 0606 | round over; both heroes in the lobby 0606 with two views, 0 fault lines |
| HEC-08 | `HE_COLOSSEUM_8` | he09 196e1 | CUP-LOBBY | 2 | f5200: 0/20 / 0/20; f7000: room 0606; f8900: room 0606 [fault lines: other] | both heroes 0/20 at 5200, then in the lobby 0606 with two views. 2 fault lines at pc 0x001D69EC (as 192e1) |
| HEC-08 | `HE_COLOSSEUM_8_CEL` | he09 196e38 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COLOSSEUM_8_ONLY` | he09 196e44 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | round over; both heroes in the lobby 0606 with two views, 0 fault lines |
| HEC-08 | `HE_COLOSSEUM_8_PP` | he09 196e27 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COLOSSEUM_8_TIT` | he09 196e16 | CUP-LOBBY | 0 | f5200: none / none, two views; f7000: room 0606; f8900: room 0606 | round over; both heroes in the lobby 0606 with two views, 0 fault lines |
| HEC-08 | `HE_COL_8_5` | he09 196e5 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COL_8_6` | he09 196e6 | OK | 0 | f5200: 15/20 / 4/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COL_8_10` | he09 196e10 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | round over at once; both heroes in the lobby 0606 with two views at all three points, 0 fault lines |
| HEC-08 | `HE_COL_8_25` | he09 196e25 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | as 196e10 |
| HEC-08 | `HE_COL_8_30` | he09 196e30 | OK | 0 | f5200: 20/20 / 18/20, two views; f7000: 3/20 / 0/20, two views; f8900: room 0606 |  |
| HEC-08 | `HE_COL_8_31` | he09 196e31 | OK | 0 | f5200: 0/20 / 0/20; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COL_8_35` | he09 196e35 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| HEC-08 | `HE_COL_8_40` | he09 196e40 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | as 196e10 |
| HEC-08 | `HE_COL_8_45` | he09 196e45 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | round over; both heroes in the lobby 0606 with two views, 0 fault lines |
| HEC-08 | `HE_COL_8_49` | he09 196e49 | CUP-LOBBY | 0 | f5200: room 0606; f7000: room 0606; f8900: room 0606 | as 196e10 |
| HEC-08 | `HE_COL_8_50` | he09 196e50 | OK | 0 | f5200: 20/20 / 0/20, two views; f7000: room 0606; f8900: room 0606 |  |
| HEC-08 | `HE_COL_8TI_BOSS` | he09 196e20 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 0/20 / 0/20; f8900: room 0606 |  |

## 8. Disney Castle and Timeless River

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| DC-01 | `DC02_MS100` | dc02 2 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 17/20, two views; f8900: 20/20 / 17/20, two views |  |
| DC-01 | `DC02_MS101` | dc02 4 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| DC-01 | `DC00_MS101` | dc00 51 | OK | 0 | f5200: 20/20 / 14/20, two views; f7000: 5/20 / 5/20, two views; f8900: 1/20 / 5/20, two views |  |
| DC-01 | `DC00_MS101` | dc00 64 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| DC-01 | `DC00_MS101` | dc00 66 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 1/20 / 8/20, two views; f8900: 1/20 / 8/20, two views |  |
| WI-01 | `WI01_MS101` | wi01 58 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 15/20 / 16/20, two views; f8900: 12/20 / 16/20, two views |  |
| WI-02 | `WI07_MS102A` | wi07 57 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: room 080D |  |
| WI-02 | `WI06_MS102B` | wi06 56 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 13/20 / 0/20, two views; f8900: 7/20 / 3/20, two views |  |
| WI-02 | `WI04_MS102C` | wi04 54 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 10/20 / 20/20, two views; f8900: 20/20 / 20/20 |  |
| WI-02 | `WI05_MS102D` | wi05 55 | OK | 0 | f5200: 10/20 / 15/20, two views; f7000: 14/20 / 15/20, two views; f8900: none / none |  |
| WI-03 | `WI02_MS103` | wi02 52 | OK | 0 | f5200: 20/20 / 10/20, two views; f7000: 10/20 / 5/20, two views; f8900: 10/20 / 8/20, two views |  |
| WI-04 | `WI03_MS104` | wi03 53 | OK | 0 | f5200: 12/20 / 12/20, two views; f7000: 9/20 / 8/20, two views; f8900: 19/20 / 15/20, two views |  |

## 9. Port Royal

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| CA-01 | `CA01_MS101` | ca01 51 | OK | 0 | f5200: 17/20 / 6/20, two views; f7000: none / none; f8900: none / none |  |
| CA-01 | `CA01_MS102` | ca01 52 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 11/20 / 17/20, two views; f8900: none / none |  |
| CA-01 | `CA02_MS103` | ca02 55 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: none / none; f8900: 20/20 / 16/20, two views |  |
| CA-02 | `CA07_MS105` | ca07 58 | OK | 0 | f5200: 17/20 / 20/20, two views; f7000: 17/20 / 9/20, two views; f8900: 13/20 / 13/20, two views |  |
| CA-02 | `CA03_MS106` | ca03 56 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| CA-03 | `CA09_MS104` | ca09 59 | OK | 0 | f5200: 15/20 / 11/20, two views; f7000: 6/20 / 19/20, two views; f8900: none / none |  |
| CA-04 | `CA10_MS107` | ca10 60 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| CA-05 | `CA01_MS201` | ca01 53 | OK | 0 | f5200: 10/20 / 20/20, two views; f7000: 19/20 / 20/20, two views; f8900: none / none |  |
| CA-05 | `CA14_MS203` | ca14 62 | OK | 0 | f5200: 20/20 / 16/20, two views; f7000: none / none; f8900: room 0510 |  |
| CA-07 | `CA18_MS202` | ca18 85 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 19/20 / 14/20, two views; f8900: 17/20 / 18/20, two views |  |
| CA-08 | `SHIP_BATTLE` | ca18 11 | OK | 0 | f5200: 15/20 / 14/20, two views; f7000: 20/20 / 14/20, two views; f8900: 20/20 / 14/20, two views |  |
| CA-08 | `SHIP_BATTLE` | ca18 1 | OK | 0 | f5200: 20/20 / 15/20, two views; f7000: room 0110; f8900: room 0110 |  |
| CA-08 | `SHIP_BATTLE` | ca19 12 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| CA-08 | `SHIP_BATTLE` | ca21 2 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 6/20 / 10/20, two views; f8900: room 0410 |  |
| CA-08 | `SHIP_BATTLE` | ca21 3 | OK | 0 | f5200: 11/20 / 17/20, two views; f7000: 16/20 / 14/20, two views; f8900: 20/20 / 10/20, two views |  |
| CA-09 | `CA01_MS204` | ca01 54 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 20/20 / 14/20, two views; f8900: 20/20 / 6/20, two views |  |
| CA-10 | `CA02_SKATE_01` | ca02 88 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |

## 10. Agrabah

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| AL-01 | `AL00_MS101` | al00 57 | OK | 0 | f5200: 19/20 / 20/20, two views; f7000: none / none; f8900: room 0207 |  |
| AL-02 | `AL09_GIMMICK` | al09 2 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 17/20 / 14/20, two views; f8900: 11/20 / 10/20, two views |  |
| AL-03 | `AL13_TRAP` | al13 79 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 10/20 / 20/20, two views; f8900: 14/20 / 13/20, two views |  |
| AL-03 | `AL13_TRAP_FREE` | al13 80 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 0/20 / 20/20, two views; f8900: 16/20 / 18/20, two views |  |
| AL-03 | `AL13_TRAP_FREE2` | al13 81 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 6/20 / 8/20, two views; f8900: 9/20 / 13/20, two views |  |
| AL-04 | `AL10_MS102` | al10 58 | OK | 0 | f5200: 15/20 / 11/20, two views; f7000: 14/20 / 13/20, two views; f8900: 5/20 / 2/20, two views |  |
| AL-05 | `AL03_MS103` | al03 59 | OK | 0 | f5200: 17/20 / 17/20, two views; f7000: 13/20 / 14/20, two views; f8900: 13/20 / 15/20, two views |  |
| AL-06 | `AL14_MS_K` | al14 10 | OK-V5 | 0 | f5200: none / none; f7000: 20/20 / none; f8900: 20/20 / none | carpet phase "Head towards Jafar's shadow!": two riders after the scene (sp-5-al10; jump by room) |
| AL-06 | `AL14_MS_L` | al14 11 | OK-V5 | 0 | f5200: none / none; f7000: none / none; f8900: none / none | carpet phase (sp-5-al11; jump by room) |
| AL-06 | `AL14_MS_M` | al14 12 | OK-V5 | 0 | f5200: 20/20 / none; f7000: none / none; f8900: 3/20 / none | carpet phase (sp-5-al12; jump by room) |
| AL-06 | `AL14_MS_O` | al14 14 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 14/20 / none; f8900: 2/20 / none | carpet phase "Examine the monument!" (sp-5-al14; jump by room) |
| AL-06 | `AL14_MS_O` | al14 18 | OK-V5 | 0 | f5200: none / none; f7000: none / none; f8900: none / none | carpet phase (sp-5-al18; jump by room) |
| AL-06 | `AL14_MS_P` | al14 102 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | race to the tower (sp-5-al102: 0 fault lines) |
| AL-06 | `AL14_MS_P` | al14 101 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | race to the tower (sp-5-al101: 0 fault lines) |
| AL-06 | `AL14_MS_P` | al14 100 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | race to the tower: two riders, each flies by his own stick (sp-5-al100: 0 fault lines) |
| AL-06 | `AL14_MS201A` | al14 86 | OK-V5 | 0 | f5200: 20/20 / none; f7000: none / none; f8900: 2/20 / none | carpet fight A: two riders (sp-5-al86: 0 fault lines) |
| AL-06 | `AL14_MS201B` | al14 87 | OK-V5 | 0 | f5200: 10/20 / none; f7000: 20/20 / none; f8900: 2/20 / none | carpet fight B: two riders (sp-5-al87: 0 fault lines) |
| AL-07 | `AL14_MS202` | al14 106 | SHARED | 50 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | as 105 (no-patch control sp-c-al106: 50 lines) |
| AL-07 | `AL14_MS202` | al14 61 | SHARED | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 10/20 / none | the escape: one hero, player 2 alone starts the game and plays it (nt-al61, sp-5-al61: 0 fault lines) |
| AL-07 | `AL14_MS202` | al14 105 | SHARED | 50 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | the escape, another program: 50 fault lines WITH NO PATCH TOO (sp-c-al106 is its sister): the game's own in this test start |
| AL-07 | `AL14_MS202_FREE` | al14 111 | SHARED | 0 | f5200: 20/20 / none; f7000: 17/20 / none; f8900: 9/20 / none | the escape as a replay mission (see the note on replay missions in STATE part 7e) |
| AL-08 | `AL05_MS203` | al05 62 | OK-V5 | 0 | f5200: 14/20 / none; f7000: 4/20 / none; f8900: none / none | Jafar: two riders, two views, own HP, lane N's down-and-rescue (sp-5-al62: 0 fault lines) |
| AL-09 | `AL00_SKATE_01` | al00 109 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0207; f8900: room 0207 |  |
| AL-09 | `AL00_SKATE_01` | al00 110 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 0F07; f8900: room 0F07 |  |

## 11. Halloween Town

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| NM-01 | `NM00_MS101` | nm00 51 | OK | 0 | f5200: 16/20 / 20/20, two views; f7000: 9/20 / 20/20, two views; f8900: 10/20 / 20/20, two views |  |
| NM-01 | `NM06_MS102` | nm06 53 | OK | 0 | f5200: 15/20 / 20/20, two views; f7000: 15/20 / 20/20, two views; f8900: 15/20 / 20/20, two views |  |
| NM-02 | `NM03_MS103` | nm03 52 | OK | 0 | f5200: 15/20 / 20/20, two views; f7000: 13/20 / 15/20, two views; f8900: 8/20 / 1/20, two views |  |
| NM-03 | `NM09_MS104` | nm09 68 | OK-GAME | 50 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: a script attaches something to an object that is not there after a jump start] | Oogie Boogie: both heroes fight on the belt, two views. 50 fault lines, the same places WITH NO PATCH (sp-c-nm68: the script attaches Oogie to an object that is not there after a jump start) |
| NM-03 | `NM09_MS104` | nm09 69 | OK-GAME | 50 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: a script attaches something to an object that is not there after a jump start] | Oogie Boogie, second program: as program 68 (50 fault lines that the no-patch run has too) |
| NM-03 | `NM09_MS104` | nm09 55 | OK | 0 | f5200: 17/20 / 15/20, two views; f7000: 17/20 / 6/20, two views; f8900: 0/20 / 0/20 |  |
| NM-04 | `NM10_MS201` | nm10 62 | OK | 0 | f5200: 17/20 / 14/20, two views; f7000: 19/20 / 8/20, two views; f8900: 15/20 / 4/20, two views |  |
| NM-05 | `NM00_MS202` | nm00 60 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 3/20 / 11/20, two views; f8900: 15/20 / 11/20, two views |  |
| NM-06 | `NM07_MS204` | nm07 71 | OK | 0 | f5200: 12/20 / 13/20, two views; f7000: 1/20 / 12/20, two views; f8900: 1/20 / 0/20, two views |  |
| NM-06 | `NM07_MS204` | nm07 64 | OK | 0 | f5200: 9/20 / 13/20, two views; f7000: 17/20 / 9/20, two views; f8900: 0/20 / 3/20, two views |  |
| NM-07 | `NM10_MS203` | nm10 63 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none | the toy cannon: turns with player 2's stick, shoots with his Circle (nt-nm63: score 1 -> 3, 0 fault lines) |
| NM-07 | `NM10_MS203_FREE` | nm10 72 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: none / none | the toy cannon as a replay mission (sp-5-nm72: 0 fault lines) |
| NM-08 | `NM09_SKATE_01` | nm09 75 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: room 050E; f8900: room 050E |  |

## 12. Pride Lands

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| LK-01 | `LK05_MS101` | lk05 56 | OK | 0 | f5200: 8/20 / 6/20, two views; f7000: none / none; f8900: none / none |  |
| LK-02 | `LK02_MS102` | lk02 51 | OK | 0 | f5200: 17/20 / 20/20, two views; f7000: 14/20 / 14/20, two views; f8900: 14/20 / 17/20, two views |  |
| LK-03 | `LK14_MS103` | lk14 55 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 14/20 / 10/20, two views |  |
| LK-04 | `LK05_MS201` | lk05 57 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| LK-05 | `LK15_MS202` | lk15 59 | OK | 0 | f5200: 20/20 / 2/20, two views; f7000: 4/20 / 4/20, two views; f8900: 2/20 / 20/20, two views |  |

## 13. Space Paranoids

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| TR-01 | `A_SCT_GIMMICK` | tr00 1 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| TR-02 | `TR01_MS101` | tr01 51 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: none / none |  |
| TR-03 | `TR02_MS102A` | tr02 72 | TEST-LIMIT | 22 | f5200: none / none; f7000: none / none; f8900: none / none [fault lines: other] | a later phase of the ride: this program places no rider (its spawn groups are b_9b, b_96, b_9c, b_9f), so a jump test shows no hero; 22 fault lines, 25 with no patch at all (sp-c-tr72) |
| TR-03 | `TR02_MS102A` | tr02 73 | TEST-LIMIT | 22 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none [fault lines: other] | as 72 |
| TR-03 | `TR02_MS102A` | tr02 61 | OK-V5 | 0 | f5200: 14/20 / none; f7000: the New Game room (after a Continue); f8900: 2/20 / none | two cycles; player 2's Circle and Square work on his own cycle (lc33-p2), 0 fault lines (sp-5-tr61) |
| TR-03 | `TR02_MS102B` | tr02 62 | OK-V5 | 0 | f5200: 18/20 / none; f7000: 0/20 / none; f8900: 8/20 / none | the escape part: each stick steers its own cycle (sp-5-tr62: 0 fault lines) |
| TR-03 | `TR02_MS102_FREE` | tr02 63 | OK-V5 | 47 | f5200: 18/20 / none; f7000: 0/20 / none [fault lines: Continue on a jump disc (the game's own test limit, fifth round)] | the Light Cycle as a replay mission: two cycles (sp-5-tr63 in v5free.log: 0 fault lines). With "Continue" pressed a jump test stops (STATE part 7e) |
| TR-03 | `TR02_MS102_FREE` | tr02 74 | TEST-LIMIT | 22 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none [fault lines: other] | a later phase of the replay ride, no rider placement of its own (22 fault lines, as programs 72 and 73) |
| TR-04 | `TR03_MS103` | tr03 54 | OK | 0 | f5200: 16/20 / 20/20, two views; f7000: 14/20 / 20/20, two views; f8900: 5/20 / 20/20, two views |  |
| TR-05 | `TR04_MS104` | tr04 55 | OK | 0 | f5200: 20/20 / 17/20, two views; f7000: 19/20 / 11/20, two views; f8900: 16/20 / 11/20, two views |  |
| TR-06 | `TR02_MS210` | tr02 53 | OK | 0 | f5200: 16/20 / 20/20, two views; f7000: 8/20 / 17/20, two views; f8900: 9/20 / 13/20, two views |  |
| TR-06 | `TR04_MS202` | tr04 56 | OK | 0 | f5200: 18/20 / 20/20, two views; f7000: 7/20 / 20/20, two views; f8900: 0/20 / 0/20 |  |
| TR-07 | `TR07_MS203` | tr07 57 | OK | 0 | f5200: 7/20 / 10/20, two views; f7000: 15/20 / 13/20, two views; f8900: 17/20 / 13/20, two views |  |
| TR-08 | `TR09_MS204` | tr09 58 | OK | 0 | f5200: 15/20 / 15/20, two views; f7000: 7/20 / 15/20, two views; f8900: 18/20 / 10/20, two views |  |
| TR-08 | `TR09_MS205` | tr09 59 | OK | 0 | f5200: 14/20 / 14/20, two views; f7000: 14/20 / 9/20, two views; f8900: 9/20 / 9/20, two views |  |
| TR-08 | `TR09_MS205` | tr09 64 | OK | 0 | f5200: 14/20 / 14/20, two views; f7000: 16/20 / 9/20, two views; f8900: 1/20 / 9/20, two views |  |

## 14. The World That Never Was

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| EH-01 | `EH21_MS101` | eh21 99 | OK | 0 | f5200: none / none; f7000: the New Game room (after a Continue); f8900: 0/20 / 0/20 |  |
| EH-01 | `EH21_MS101` | eh21 65 | OK | 0 | f5200: 5/20 / 0/20, two views; f7000: 11/20 / 0/20, two views; f8900: 11/20 / 0/20, two views |  |
| EH-02 | `EH10_MS102` | eh10 57 | OK | 0 | f5200: 11/20 / 17/20, two views; f7000: the New Game room (after a Continue); f8900: 8/20 / 1/20, two views |  |
| EH-02 | `EH10_MS102` | eh10 100 | OK | 0 | f5200: 0/20 / 20/20, two views; f7000: 0/20 / 1/20, two views; f8900: 20/20 / 20/20, two views |  |
| EH-03 | `EH14_MS103` | eh14 101 | OK | 0 | f5200: 0/20 / 20/20, two views; f7000: 0/20 / 20/20, two views; f8900: 0/20 / 0/20 |  |
| EH-03 | `EH14_MS103` | eh14 58 | OK | 5 | f5200: 8/20 / 19/20, two views; f7000: 0/20 / 17/20, two views; f8900: 0/20 / 17/20, two views [fault lines: player 2's gauge without a unit slot for one frame (fixed by the gauge guard, STATE part 6d)] | Luxord: both heroes, two views. The 5 fault lines of the sweep's patch (v28) were player 2's gauge without a unit slot for one frame; FIXED by the gauge guard: the same run on the final patch has 0 (sp-q-eh58) |
| EH-04 | `EH15_MS104` | eh15 56 | OK | 0 | f5200: 6/20 / 11/20, two views; f7000: 15/20 / 3/20, two views; f8900: 20/20 / 20/20 |  |
| EH-04 | `EH15_MS104` | eh15 102 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| EH-05 | `EH19_MS105` | eh19 97 | OK | 0 | f5200: 0/20 / 4/20, two views; f7000: 12/20 / 0/20, two views; f8900: 4/20 / 0/20, two views |  |
| EH-05 | `EH19_MS105` | eh19 59 | OK | 0 | f5200: 16/20 / 20/20, two views; f7000: 1/20 / 20/20, two views; f8900: 1/20 / 20/20, two views |  |
| EH-06 | `EH25_MS109` | eh25 70 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 8/20 / 20/20, two views; f8900: 11/20 / 15/20, two views |  |
| EH-06 | `EH26_MS108` | eh26 69 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 18/20 / 14/20, two views |  |
| EH-06 | `EH26_MS108` | eh26 86 | OK | 0 | f5200: 20/20 / 18/20, two views; f7000: 14/20 / 20/20, two views; f8900: none / none |  |
| EH-07 | `EH27_MS106` | eh27 75 | OK | 0 | f5200: 20/20 / 15/20, two views; f7000: 13/20 / 10/20, two views; f8900: 8/20 / 15/20, two views |  |
| EH-07 | `EH28_MS107` | eh28 68 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 15/20, two views; f8900: 20/20 / 15/20, two views |  |
| EH-08 | `EH24_MS110` | eh24 71 | OK | 0 | f5200: 20/20 / 14/20, two views; f7000: 19/20 / 18/20, two views; f8900: 52/60 / 0/20, two views |  |
| EH-09 | `EH22_MS111` | eh22 72 | SHARED | 0 | f5200: 14/20 / none; f7000: 6/20 / none; f8900: 18/20 / none | the sidecar: it moves with player 2's stick while player 1 presses nothing (nt-eh72: 0 fault lines) |
| EH-09 | `TEST_EH22_MS111` | eh22 90 | SHARED | 35 | f5200: 12/20 / none; f7000: 2/20 / none; f8900: 18/20 / none [fault lines: other] | a TEST_ mission of the same ride (35 fault lines of the "mission data not loaded" kind) |
| EH-10 | `EH23_MS112` | eh23 73 | OK | 0 | f5200: 20/20 / 15/20, two views; f7000: 8/20 / 15/20, two views; f8900: 13/20 / 16/20, two views |  |
| EH-11 | `EH20_MS113` | eh20 74 | OK | 0 | f5200: 20/20 / 0/20, two views; f7000: 10/20 / 3/20, two views; f8900: 10/20 / 0/20, two views |  |

## 15. 100 Acre Wood

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| PO-01 | `PO06_MS101` | po06 55 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | two flyers (sp-5-po55: 0 fault lines) |
| PO-01 | `PO06_MS101` | po06 66 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | two flyers (sp-5-po66: 0 fault lines) |
| PO-01 | `PO06_MS101_FREE` | po06 69 | OK-V5 | 0 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none | the balloon flight as a replay mission: two flyers (sp-5-po69: 0 fault lines) |
| PO-01 | `PO06_MS100` | po06 54 | OK-V5 | 15 | f5200: 20/20 / none; f7000: 20/20 / none; f8900: 20/20 / none [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | two flyers, each by his own stick (sp-5-po54). 17 fault lines: the no-patch run has 15 of the same places (sp-c-po54: the mission's data file is not loaded after a jump start) |
| PO-02 | `PO07_MS201` | po07 67 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none | Hunny Slider (another program of the same game) |
| PO-02 | `PO07_MS201` | po07 57 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: room 0309 | Hunny Slider: the slider goes left when player 2 pushes left, player 1 pressing nothing (nt-po57: 0 fault lines) |
| PO-02 | `PO07_MS201_FREE` | po07 70 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none | Hunny Slider as a replay mission (the same game as program 57) |
| PO-03 | `PO08_MS301` | po08 59 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: room 0509 | Hunny Pot: no hero object; both controllers (nt-po59: in sync, 0 fault lines) |
| PO-03 | `PO08_MS301_FREE` | po08 71 | SHARED | 0 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none | Hunny Pot as a replay mission |
| PO-04 | `PO09_MS401` | po09 61 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| PO-04 | `PO09_MS401` | po09 74 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| PO-04 | `PO09_MS401_FREE` | po09 72 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| PO-05 | `PO01_MS501` | po01 52 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| PO-05 | `PO01_MS501_FREE` | po01 73 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |

## 16. Atlantica

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| LM-00 | `LM02_MS101` | lm02 52 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |

## 18. Final Mix extras

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| FM-02 | `HB32_FM_VEX` | hb32 115 | OK | 0 | f5200: 20/20 / 10/20, two views; f7000: 20/20 / 16/20, two views; f8900: 20/20 / 20/20 |  |
| FM-02 | `HB32_FM_VEX` | hb32 146 | OK | 0 | f5200: the New Game room (after a Continue); f7000: 0/20 / 0/20; f8900: 20/20 / 20/20 |  |
| FM-02 | `HB33_FM_VEX` | hb33 156 | OK | 0 | f5200: 0/20 / 0/20; f7000: 10/20 / 16/20, two views; f8900: 20/20 / 10/20, two views |  |
| FM-02 | `HB33_FM_VEX` | hb33 157 | OK | 0 | f5200: the New Game room (after a Continue); f7000: 0/20 / 0/20; f8900: 20/20 / 20/20, two views |  |
| FM-03 | `HB33_FM_LEX` | hb33 142 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20; f8900: 20/20 / 0/20, two views |  |
| FM-03 | `HB33_FM_LEX` | hb33 147 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20; f8900: 16/20 / 0/20, two views |  |
| FM-04 | `HB34_FM_ZEX` | hb34 151 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| FM-04 | `HB34_FM_ZEX` | hb34 152 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: the New Game room (after a Continue); f8900: 20/20 / 20/20, two views |  |
| FM-05 | `HB33_FM_LAR` | hb33 148 | TEST-LIMIT | 0 | f5200: none / none; f7000: the New Game room (after a Continue); f8900: the New Game room (after a Continue) | no hero after the jump. With NO PATCH the game stops at Continue (swc-HB33_FM_LAR-148: TIMED OUT, the "Continue on a jump disc" lines); the build does not stop (it goes to the New Game room by test line B) |
| FM-05 | `HB33_FM_LAR` | hb33 155 | OK | 0 | f5200: 3/20 / 13/20, two views; f7000: 3/20 / 4/20, two views; f8900: 9/20 / 3/20, two views |  |
| FM-05 | `HB33_FM_LAR` | hb33 143 | OK | 0 | f5200: 9/20 / 13/20, two views; f7000: 3/20 / 4/20, two views; f8900: 9/20 / 3/20, two views |  |
| FM-06 | `HB38_FM_MAR` | hb38 150 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| FM-06 | `HB38_FM_MAR` | hb38 145 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| FM-07 | `TT20_MS603_RE` | tt20 213 | OK | 0 | f5200: 20/20 / 20/20; f7000: none / none; f8900: 20/20 / 20/20 |  |
| FM-07 | `BB15_MS203_RE` | bb15 97 | OK | 0 | f5200: 15/20 / 20/20, two views; f7000: 0/20 / 20/20, two views; f8900: none / none |  |
| FM-07 | `EH20_MS113_RE` | eh20 98 | OK | 0 | f5200: the New Game room (after a Continue); f7000: 20/20 / 20/20; f8900: none / none |  |
| FM-08 | `DC07_FM_NAZO` | dc07 73 | OK | 0 | f5200: the New Game room (after a Continue); f7000: 0/20 / 5/20, two views; f8900: the New Game room (after a Continue) |  |
| FM-08 | `DC07_FM_NAZO` | dc07 67 | OK | 0 | f5200: the New Game room (after a Continue); f7000: 0/20 / 5/20, two views; f8900: the New Game room (after a Continue) |  |

## Missions that are not in the checklist's lists

| Row | Mission | Room, program | Result | Fault lines | Three probe points (player 1 / player 2) | Note |
|---|---|---|---|---|---|---|
| - | `BB08_GIMMICK` | bb08 95 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `BB13_KINOKO_XAL` | bb13 10 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `CA13_KINOKO_LUX` | ca13 10 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `DC02_MS102` | dc02 3 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `EH03_KINOKO_XEM` | eh03 3 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `HB02_KINOKO_ROX` | hb02 2 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `HB04_KINOKO_DEM` | hb04 1 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `HB24_CONFINE_3` | hb24 3 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `HB25_CONFINE_4` | hb25 5 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `HE17_KINOKO_ZEX` | he17 2 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `LM01_MS201` | lm01 51 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | the musical "Part of Your World": player 2's taps give byte for byte the pictures of player 1's taps (mus-p1 / mus-p2), 0 fault lines |
| - | `LM01_MS201_FREE` | lm01 67 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | the musical as a replay mission: no hero object; both controllers |
| - | `LM02_MS102` | lm02 63 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical scene with the ring prompts: no hero object; both controllers (not run with player 2 alone) |
| - | `LM03_MS301` | lm03 53 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical: no hero object; both controllers (nt-lm53: in sync, 0 fault lines) |
| - | `LM03_MS301_FREE` | lm03 68 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical as a replay mission |
| - | `LM04_MS103` | lm04 64 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical: no hero object; both controllers (not run with player 2 alone) |
| - | `LM04_MS103_FREE` | lm04 66 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical as a replay mission |
| - | `LM04_MS501` | lm04 55 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical: no hero object; both controllers (the same glue as lm01 51; not run with player 2 alone) |
| - | `LM04_MS501_FREE` | lm04 70 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical as a replay mission |
| - | `LM09_MS401` | lm09 65 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical: no hero object; both controllers (not run with player 2 alone) |
| - | `LM09_MS401_FREE` | lm09 69 | SHARED | 0 | f5200: none / none; f7000: none / none; f8900: none / none | a musical as a replay mission |
| - | `MU09_KINOKO_VEX` | mu09 1 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `NM07_KINOKO_XIG` | nm07 1 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `PO01_MS500` | po01 51 | OK-GAME | 17 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | 17 fault lines of the "mission data file not loaded" kind, as PO06_MS100 with no patch (sp-c-po54) |
| - | `PO07_MS200` | po07 56 | SHARED | 14 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | Hunny Slider, story version: a rider object without a unit slot, no hero for player 2; both controllers. 14 fault lines of the "mission data file not loaded" kind |
| - | `PO08_MS300` | po08 58 | SHARED | 14 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | Hunny Pot, story version: as po07 56 (14 fault lines of the "mission data" kind) |
| - | `PO09_MS400` | po09 60 | OK-GAME | 17 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | both heroes, two views (zq0). 17 fault lines, all of the "mission data file not loaded after a jump start" kind (the no-patch control sp-c-po54 has them) |
| - | `TEST_HE_COLOSSEUM` | he09 178e5 | TEST-LIMIT | 48 | f5200: 20/20 / 9/20, two views; f7000: 12/20 / 12/20, two views; f8900: 0/20 / 0/20 [fault lines: other] | a TEST_ entry: with NO PATCH the game stops (swc-TEST_HE_COLOSSEUM-178e5: TIMED OUT); the build runs it in sync with 48 fault lines |
| - | `TEST_HE_COLOSSEUM2` | he09 178e2 | TEST-LIMIT | 50 | f5200: 9/20 / 9/20, two views; f7000: 13/20 / 12/20; f8900: 13/20 / 17/20, two views [fault lines: other] | a TEST_ entry (no player reaches it); in sync with 50 fault lines; HYPOTHESIS: as its sister 178e5, which stops with no patch |
| - | `TEST_HE_COLOSSEUM3` | he09 178e3 | TEST-LIMIT | 46 | f5200: 10/20 / 13/20, two views; f7000: 11/20 / 13/20, two views; f8900: 15/20 / 20/20, two views [fault lines: other] | as 178e2 |
| - | `TEST_MU07_MS999` | mu07 99 | OK-GAME | 17 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] |  |
| - | `TEST_PO08_MS300` | po08 68 | SHARED | 14 | f5200: noslot / none; f7000: noslot / none; f8900: noslot / none [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] | a TEST_ entry of the Hunny Pot (14 fault lines of the "mission data" kind) |
| - | `TT25_KINOKO_AXE` | tt25 7 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `TT36_KINOKO_SAI` | tt36 1 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `WI02_KINOKO_MAR` | wi02 10 | OK | 0 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views |  |
| - | `ZZ_HE09_MS201` | he09 175 | OK-GAME | 19 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] |  |
| - | `ZZ_HE09_MS201` | he09 176 | OK-GAME | 19 | f5200: 20/20 / 20/20, two views; f7000: 20/20 / 20/20, two views; f8900: 20/20 / 20/20, two views [fault lines: the mission's data file is not loaded after a jump start (the game's own: the no-patch control sp-c-po54 has them)] |  |

## The Olympus cups: blocks that were not run

A cup round is an "If Entrance N" block inside a battle program of the arena room he09 (130 blocks, 44 mission
names). One block of each name was run (the lines of rows HEC-01 to HEC-08 above). Not run, same name and rules:

`HE_COLOSSEUM` 7 more, `HE_COLOSSEUM_2` 6 more, `HE_COLOSSEUM_2_FOG` 1 more, `HE_COLOSSEUM_3` 9 more, `HE_COLOSSEUM_6` 6 more, `HE_COLOSSEUM_6_FOG` 1 more, `HE_COLOSSEUM_7` 9 more, `HE_COLOSSEUM_8` 6 more, `HE_COLOSSEUM_8_CEL` 6 more, `HE_COLOSSEUM_8_ONLY` 6 more, `HE_COLOSSEUM_8_PP` 7 more, `HE_COLOSSEUM_8_TIT` 7 more, `HE_COL_5` 7 more, `HE_COL_8TI_BOSS` 1 more, `TEST_HE_COLOSSEUM` 7 more

## Mission names of the checklist that no room program starts

These names are in the game's mission files, but no program of any room names them (not in the un-indented
Mission lines and not in the cup blocks). A jump test cannot start them; they were NOT run.

CA-06 `CA09_MEDAL`, CA-06 `CA10_MEDAL`, CA-06 `CA12_MEDAL`, CA-06 `CA13_MEDAL`, CA-06 `CA14_MEDAL`, CA-06 `CA15_MEDAL`

