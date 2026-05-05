# Unknown Opta qualifier IDs in `qualifiers.parquet`

This repository parses Opta F24 event data from Opta Analyst (`theanalyst.com`) into three main tables: `events`, `qualifiers`, and `metadata`.[cite:4][cite:7][cite:9]

The `qualifiers.parquet` file contained a number of `qualifier_id` values that were not covered by the existing `OptaQualifierReference.QUALIFIERS` mapping, so they appeared as `"Unknown (ID: X)"` in the exported data.[cite:4][cite:5]

## IDs that appear as unknown

Inspecting `data/match-events/qualifiers.parquet` shows the following distinct `qualifier_id` values where `qualifier_name` starts with `"Unknown (ID:"`:

```text
[10, 12, 13, 14, 16, 17, 18, 19, 22, 23, 24, 25, 26,
 46, 47, 49, 55, 60, 61, 62, 63, 64, 65, 66, 68, 70,
 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85,
 86, 87, 94, 100, 101, 102, 103, 127, 145, 146, 147,
 167, 169, 170, 185, 190, 211, 216, 229, 232, 233,
 239, 249, 250, 252, 276, 277, 285, 286, 292, 293,
 294, 295, 296, 297, 298, 300, 302, 314, 319, 328,
 329, 330, 331, 332, 335, 336, 343, 345, 346, 347,
 348, 353, 354, 361, 362, 363, 364, 365, 374, 375,
 376, 377, 378, 380, 381, 383, 384, 385, 386, 387,
 388, 389, 390, 391, 392, 393, 395, 396, 397, 398,
 399, 436, 458, 459, 464, 465, 467, 468, 472, 474,
 484, 485, 488, 490]
```

These values were computed by reading the parquet file and filtering rows where `qualifier_name` equals `"Unknown (ID: <qualifier_id>)"`.[cite:7]

## Mapping many of the unknown IDs

To understand what these IDs mean, an open Opta qualifier reference file (`opta-qualifiers.csv`) from the `tomh05/football-scores` repository was used as a lookup table.[web:10]  This CSV encodes the official Opta qualifier names, value types, and descriptions for a large subset of F24 qualifiers.

For the IDs listed above, that reference provides definitions for the following subset (the rest are not present in that public CSV and remain undocumented here):[web:10]

| qualifier_id | name                     | notes (shortened from Opta docs)                                    |
|-------------:|--------------------------|---------------------------------------------------------------------|
| 10           | Hand                     | Handball (used with relevant foul and handball events).            |
| 12           | Dangerous play           | Foul due to dangerous play.                                        |
| 13           | Foul                     | All fouls (generic foul qualifier).                                |
| 14           | Last line                | Defensive action as last player between opponent and goal.         |
| 16           | Small box-centre        | Shot zone in the 6-yard box centre (Appendix 13 in F24 docs).      |
| 17           | Box-centre              | Shot zone in central part of penalty area.                         |
| 18           | Out of box-centre       | Shot from central area outside box.                                |
| 19           | 35+ centre              | Shot from central area beyond 35 yards.                            |
| 22           | Regular play            | Shot during open play, not from a set piece.                       |
| 23           | Fast break              | Shot following a fast break.                                       |
| 24           | Set piece               | Shot from a crossed free kick.                                     |
| 25           | From corner             | Shot occurring directly from a corner.                             |
| 26           | Free kick               | Shot occurring directly from a free kick.                          |
| 49           | Attendance figure       | Crowd size (dynamic integer).                                      |
| 55           | Related event ID        | Event ID of the related assist/preceding event.                    |
| 60–66, 68,70 | Pitch zones             | Various shot-location zones (small box left/right, box-deep, etc). |
| 73–87        | Goal mouth zones        | Detailed goalmouth zones (e.g. low left, high centre, close high). |
| 94           | Def block               | Defender block of an opposition shot.                              |
| 100          | Six yard blocked        | Shot blocked on the six-yard line.                                 |
| 101          | Saved off line          | Shot saved on the goal line.                                       |
| 102          | Goal mouth y coordinate | Y coordinate where shot crossed the goal line (0–100).             |
| 103          | Goal mouth z coordinate | Height (Z) where shot crossed goal line (0–100).                   |
| 127          | Direction of play       | Actual direction of play relative to TV camera.                    |
| 145          | Formation slot          | 1–11 slot in team formation for a player coming on.                |
| 146–147      | Blocked shot location   | X/Y pitch coordinates where a shot was blocked.                    |
| 167          | Out of play             | Tackle/clearance sends ball out of play.                           |
| 169          | Leading to attempt      | Player error that leads to an opposition shot.                     |
| 170          | Leading to goal         | Player error that leads directly to an opposition goal.            |
| 185          | Blocked cross           | Clearance where cross is blocked.                                  |
| 190          | Saved shot off target   | Shot saved by goalkeeper but was going wide.                       |
| 211          | Overrun                 | Take-on where ball runs out of play or to an opponent.             |
| 216          | 2nd related event ID    | Event ID of a second assist/pre-assist in some competitions.       |
| 229          | Post-match complete     | Opta post-match QC completed for this match.                       |

These are good candidates to be added to `OptaQualifierReference.QUALIFIERS` so that future parses label them correctly instead of `Unknown (ID: X)`.

## Remaining IDs

The remaining IDs in the list above are not present in the publicly-available `opta-qualifiers.csv` reference and do not appear with clear definitions in the accessible F24 documentation.[web:10][web:15]  They likely correspond to newer or competition-specific qualifiers added after that reference was published.  Until an up-to-date Opta appendix is available, those IDs will continue to show up as `Unknown (ID: X)` in the current code.
