# AI findings (2026-10-20)

Tested on the hex-board engine from `features/hexgrid` (commit 6ebd1f2), run headless in Node (the engine block of
`index.html`, no UI, no worker, no pondering). Method: AI-vs-AI duels, 20 to 40 games per row, colours swapped
every game, equal time per move (1.5 s unless noted), 150-ply cap. Wins are counted for the variant (A) against the
reference (B). Small samples: a difference of less than about 6 games out of 20 is noise.

## Result 1: fuel is undervalued (big win)

The AI's astronauts were nearly always at fuel 0. They walked and jumped forward but almost never refuelled, because one
advanced row was worth 16 points and one fuel point only 14. Fuel is range (fuel + 1 hexes), so a fuel-0 astronaut can
only hit its six neighbours.

| A (variant) vs B (reference) | A wins | B wins | draws / capped |
|---|---|---|---|
| fuel 40 vs original (fuel 14) | 16 | 3 | 1 |
| fuel 70 vs original | 17 | 3 | 0 |
| fuel 100 vs original | 13 | 4 | 3 |
| fuel 55 vs original | 15 | 3 | 2 |

Chosen: `EV.fuel = 55`.

## Result 2: quiescence search helps

The search stopped at a fixed depth and evaluated statically, so a hanging piece or a pending laser kill at the leaves was
missed. `qsearch` keeps playing out captures and laser shots (stand pat allowed) for up to `EV.qs` extra plies.
All rows have fuel 55 on both sides.

| A vs B | A wins | B wins | draws / capped |
|---|---|---|---|
| qs 4 vs no qs (first run) | 9 | 5 | 6 |
| qs 4 vs no qs (second run, 40 games) | 25 | 11 | 4 |
| qs 2 vs no qs | 8 | 8 | 4 |
| qs 6 vs qs 4 (40 games) | 16 | 19 | 5 |

Chosen: `EV.qs = 4`. Deeper (6) gave nothing; 2 was not enough.

Both changes together, new (fuel 55, qs 4) vs original (fuel 14, qs 0) at 3 s per move: 19 wins, 1 loss, 4 draws (24 games).

## Result 3: other weights, no change needed (A = fuel 40 + change, B = fuel 40)

| change | A wins | B wins | draws / capped |
|---|---|---|---|
| adv 8 (was 16) | 8 | 9 | 3 |
| adv 24 | 5 | 11 | 4 |
| near 2 (was 5) | 9 | 7 | 4 |
| near 9 | 9 | 8 | 3 |
| draw 0 (was -600) | 11 | 8 | 1 |
| vfuel 20 (was 6) | 6 | 9 | 5 |

A higher advancement weight is clearly worse. The others are within noise. `draw 0` was slightly ahead (11 to 8); not
changed, worth a bigger test.

## Observations from hand play (game 1, unfinished, Red against the original AI at 5 s)

- The original AI spent every astronaut's fuel on advancing and left several at fuel 0 next to the sun without refuelling.
  The new weights fix this: its first move is now a refuel from its rover.
- `legal()` only generates `aim` (and `laser`) moves when a target is already in line. The AI therefore never pre-aims a
  rover laser to deny a lane, which a human can do with "aim at nothing". Not changed; probably not worth the branching.
- Defence idea for a human: two guards next to the Core with fuel 1 or more, plus the default west aim of the rover, which
  covers the Core's entry hexes on its row, makes a direct rush hard. Not tested against the AI.

## Ideas not done

- Late-move pruning: jumps of 3 or 4 hexes are a large part of the branching factor (about 57 to 95 moves). Skipping far
  non-captures deep in the tree should buy about one ply.
- Make/unmake instead of cloning the piece list in `child` (the search runs about 0.5 million positions per second).
- Retest the evaluation weights at the real 10 s budget and with the worker and pondering (these tests used the plain search).
- Evaluation terms still missing: shield safety, a rover standing in an enemy rover's line, who gets the first shot.
- A bigger test of draw contempt (`draw` 0 against -600).

## What changed in `index.html`

Only the engine script: `EV` now `{ fuel: 55, qs: 4, ... }` and the new function `qsearch`, called from `minimax` at depth 0.
Nothing was pushed or deployed.
