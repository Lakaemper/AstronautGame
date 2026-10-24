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
  The new weights fix this: its first move is now a refuel from its smasher.
- `legal()` only generates `aim` (and `laser`) moves when a target is already in line. The AI therefore never pre-aims a
  smasher laser to deny a lane, which a human can do with "aim at nothing". Not changed; probably not worth the branching.
- Defence idea for a human: two guards next to the Core with fuel 1 or more, plus the default west aim of the smasher, which
  covers the Core's entry hexes on its row, makes a direct rush hard. Not tested against the AI.

## Ideas not done

- Late-move pruning: jumps of 3 or 4 hexes are a large part of the branching factor (about 57 to 95 moves). Skipping far
  non-captures deep in the tree should buy about one ply.
- Make/unmake instead of cloning the piece list in `child` (the search runs about 0.5 million positions per second).
- Retest the evaluation weights at the real 10 s budget and with the worker and pondering (these tests used the plain search).
- Evaluation terms still missing: shield safety, a smasher standing in an enemy smasher's line, who gets the first shot.
- A bigger test of draw contempt (`draw` 0 against -600).

## What changed in `index.html`

Only the engine script: `EV` now `{ fuel: 55, qs: 4, ... }` and the new function `qsearch`, called from `minimax` at depth 0.
Not deployed to the server (the later rule changes of the same day touched the rules code too, see NOTES.md).

## Later tests (same day, after the smasher, overcharge and refuel changes)

Same method (AI-vs-AI duels, colours swapped, 24 games each, 1.5 s per move) against the current weights.

| variant (A) | A wins | B wins | draws / capped |
|---|---|---|---|
| smasher armed value 0 | 13 | 9 | 2 |
| smasher armed value 70 | 12 | 12 | 0 |
| smasher armed value 120 | 9 | 10 | 5 |
| smasher base value 85 | 9 | 12 | 3 |
| bonus 30 for an empty smasher at the sun | 9 | 13 | 2 |
| bonus 60 for an empty smasher at the sun + armed 70 (before overcharge existed) | 16 | 5 | 3 |
| the same two, after overcharge | 12 | 10 | 2 |
| overcharge penalty `hot` 0 (default 40) | 9 | 13 | 2 |
| overcharge penalty `hot` 120 | 7 | 15 | 2 |
| fuel weight 40 (default 55) | 8 | 14 | 2 |

Conclusion: the defaults (`fuel` 55, `hot` 40, smasher 50 + armed 35) stay. The 16 to 5 result did not repeat.
In 12 games the AI never let an astronaut explode from overcharge; its smashers refuelled 8 times and fired one laser shot.

First-move advantage: 50 AI-vs-AI games with identical settings (3 s per move, current rules): Blue (moves first) won 26, Red won 24,
no draws (p = 0.89). No sign of a first-move advantage; a small one cannot be excluded with 50 games.

## Smasher double step on its first move (2026-10-21, AI-vs-AI, rule test)

Question: the smasher was hardly ever moved. Would an optional 2-hex first move (like a pawn) help? Implemented as `SMASHER_DOUBLE` (see NOTES.md) and
tested with the real engine inside 14 Web Workers in the browser (7 per rule), 0.7 s and 8 plies per move, current weights, 150-ply cap,
both sides played by the same AI. 96 of 98 planned games finished (the last two were stopped). This compares the two RULE sets, it is not a strength test.

| | old rule (49 games) | double step (47 games) |
|---|---|---|
| Blue wins / Red wins / draws | 14 / 35 / 0 | 22 / 22 / 3 |
| average game length (plies) | 51 | 65 |
| smasher moves per game (both sides) | 1.29 | 4.19 |
| games in which any smasher moved | 23 of 49 | 42 of 47 |
| double steps per game | 0 | 1.26 |
| first smasher move at ply (average, sides that moved it) | 41 | 30 |
| a smasher refuelled at a fire, per game | 0.06 | 0.34 |
| laser shots per game | 0 | 0.02 |

Reading: the double step triples the smasher moves, the AI uses it, and the smasher gets to a fire much more often. It still almost never shoots
(0.02 per game), so it is used as a fuel carrier, not as a gun. The old rule gave Red 35 of 49 wins here, which does not agree with the 26:24 measured
earlier at 3 s per move: the short 0.7 s search may favour one colour, so treat the colour split as a weak signal. A repeat at a longer time per
move would be needed to confirm it.

## Smasher with 2 fuel, laser breaks shields, turn + shoot in one move (2026-10-21, rule test)

Changes: a smasher carries up to 2 fuel (`SMASHER_FUEL`, each shot costs 1), a laser hit damages a shield (2 hits shatter it; a hit shield
heals only one move later than usual), and turning and shooting is ONE move (`legal()` no longer generates `aim`). Same method as the
double-step test above (14 workers x 7 games planned, 0.7 s and 8 plies per move, current weights, both sides the same AI; 93 games finished,
the rest were stopped). Compared with the double-step-only version (47 games):

| | double step only | + 2 fuel, shield damage, turn+shoot |
|---|---|---|
| Blue wins / Red wins / draws | 22 / 22 / 3 | 45 / 36 / 12 |
| average game length (plies) | 65 | 63 |
| smasher moves per game (both sides) | 4.19 | 6.89 |
| laser shots per game | 0.02 | 1.01 |
| games with at least one shot | 1 of 47 (approx.) | 63 of 93 |
| smasher refuelled at a fire, per game | 0.34 | 0.97 |
| shield hits / shatters per game | not possible | 0 / 0 |
| average ply of the first shot | - | 17 |

Reading: the smasher now takes part: it moves more, refuels at the fires about once per game and shoots about once per game, which was almost
never the case before. The shield damage is NOT used at all by the AI (0 hits in 93 games): the evaluation values a shield at 40 (minus 15 per
damage point), so two shots (two tempi) never pay off, and nothing in the evaluation values what a shield protects. Draws went up (12 of 93,
13%, against 6%), probably repetition draws; not investigated. First-shot and colour effects are within the noise of this sample size.

Ideas: give the evaluation a term for pieces under an enemy or own shield (protected = worth more), then shield shots may start to appear; look
at the draws (which rule produces repetition?).

## Smasher value in the evaluation (2026-10-25, branch feature/fantasyOption)

Question: is `EV.smasher` = 110 too low? (An astronaut counts 100 + 55 per fuel + 16 per row + closeness, so about 160 to 200 at the start.)
Method: AI-vs-AI duels with the real engine in 14 Web Workers, 0.3 s and at most 8 plies per move, 150-ply cap, default setup (4 astronauts,
smasher, drone, shield), the variant (`EV.smasher` = V) against the current weights (110), the colour of the variant swapped every game.
Small samples: a difference of less than about 6 games per 30 is noise.

| V (variant) | games | variant wins | 110 wins | draws / capped | variant smasher moves per game (110: moves) | variant smashes per game (110: smashes) |
|---|---|---|---|---|---|---|
| 160 | 30 | 15 | 9 | 4 / 2 | 6.5 (3.7) | 1.6 (0.7) |
| 220 | 30 | 22 | 7 | 1 / 0 | 6.0 (2.5) | 2.1 (0.7) |
| 300 | 24 | 17 | 6 | 1 / 0 | 7.0 (1.8) | 2.3 (0.7) |

Reading: every higher value beats 110, and the AI with 110 hardly uses its smasher (2 to 4 moves per game, 0.7 smashes). 220 and 300 both win about
three games in four, 160 is only slightly ahead (15 : 9). 220 is the first value that is clearly better, and 300 shows no further gain, so about
220 to 250 looks right (an astronaut with 1 fuel and a little advancement is worth 165 to 200). Not tested: a value that depends on the number of
astronauts left (the fewer astronauts, the more each one is worth because only astronauts can win), and the combination with the optional `threat`
and `spread` terms. The test itself changed nothing; afterwards `EV.smasher` was set to 220 on request.
