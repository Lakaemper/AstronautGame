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
Not deployed to the server (the later rule changes of the same day touched the rules code too, see NOTES.md).

## Later tests (same day, after the rover, overcharge and refuel changes)

Same method (AI-vs-AI duels, colours swapped, 24 games each, 1.5 s per move) against the current weights.

| variant (A) | A wins | B wins | draws / capped |
|---|---|---|---|
| rover armed value 0 | 13 | 9 | 2 |
| rover armed value 70 | 12 | 12 | 0 |
| rover armed value 120 | 9 | 10 | 5 |
| rover base value 85 | 9 | 12 | 3 |
| bonus 30 for an empty rover at the sun | 9 | 13 | 2 |
| bonus 60 for an empty rover at the sun + armed 70 (before overcharge existed) | 16 | 5 | 3 |
| the same two, after overcharge | 12 | 10 | 2 |
| overcharge penalty `hot` 0 (default 40) | 9 | 13 | 2 |
| overcharge penalty `hot` 120 | 7 | 15 | 2 |
| fuel weight 40 (default 55) | 8 | 14 | 2 |

Conclusion: the defaults (`fuel` 55, `hot` 40, rover 50 + armed 35) stay. The 16 to 5 result did not repeat.
In 12 games the AI never let an astronaut explode from overcharge; its rovers refuelled 8 times and fired one laser shot.

First-move advantage: 50 AI-vs-AI games with identical settings (3 s per move, current rules): Blue (moves first) won 26, Red won 24,
no draws (p = 0.89). No sign of a first-move advantage; a small one cannot be excluded with 50 games.

## Rover double step on its first move (2026-10-21, AI-vs-AI, rule test)

Question: the rover was hardly ever moved. Would an optional 2-hex first move (like a pawn) help? Implemented as `ROVER_DOUBLE` (see NOTES.md) and
tested with the real engine inside 14 Web Workers in the browser (7 per rule), 0.7 s and 8 plies per move, current weights, 150-ply cap,
both sides played by the same AI. 96 of 98 planned games finished (the last two were stopped). This compares the two RULE sets, it is not a strength test.

| | old rule (49 games) | double step (47 games) |
|---|---|---|
| Blue wins / Red wins / draws | 14 / 35 / 0 | 22 / 22 / 3 |
| average game length (plies) | 51 | 65 |
| rover moves per game (both sides) | 1.29 | 4.19 |
| games in which any rover moved | 23 of 49 | 42 of 47 |
| double steps per game | 0 | 1.26 |
| first rover move at ply (average, sides that moved it) | 41 | 30 |
| a rover refuelled at a fire, per game | 0.06 | 0.34 |
| laser shots per game | 0 | 0.02 |

Reading: the double step triples the rover moves, the AI uses it, and the rover gets to a fire much more often. It still almost never shoots
(0.02 per game), so it is used as a fuel carrier, not as a gun. The old rule gave Red 35 of 49 wins here, which does not agree with the 26:24 measured
earlier at 3 s per move: the short 0.7 s search may favour one colour, so treat the colour split as a weak signal. A repeat at a longer time per
move would be needed to confirm it.
