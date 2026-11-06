# Deep AI test: findings (branch deeptest, 2026-11-06)

Material for a strategy tutorial. Everything below was measured with the engine of `JS/index.html` **as it is on this branch** (73 hexes, drone range **unlimited** = the test rule
from 2026-10-25, 4 astronauts + smasher + drone + shield per side). Total compute: about 52 minutes on the 16 cores of the user's PC (browser Web Workers, nothing in the cloud).
Tools: `JS/tools/deep_harness.js` (root search, handicap and weight duels), `JS/tools/openings_phase.js` (opening catalog); raw numbers in `JS/rawdata.json`; the 100 openings in `Openings.md`.
Notation in this file: files a-i, ranks 1-9 (Blue's Home Planet is e1, Red's e9, the central fire e5); `A` astronaut, `S` smasher, `D` drone;
`-` step, `~` jetpack jump, `=` take fuel from the drone, `+` refuel at the fire, `>` push, `*` smash.

## 1. Is the perfect game computable? Does Blue always win?

**No, not with this engine and not in any reasonable time, and nothing suggests a forced Blue win.**

* The game tree is far too large: 48 legal first moves, 40-60 per ply later, games of 80+ plies. Exact search of the 12 best first moves needed 61 s at depth 7 and 295 s at
  depth 8 (all 16 cores); depth 9 on the 8 best moves did not finish in 8.5 minutes. Growth is about 2.5-5x per ply, so a win/loss proof (80+ plies) is out of reach by many orders of magnitude.
* No search ever found a forced win (a forced win would show as a score above 90 000). At depth 8 the **best first moves are all worth -6** for Blue (about 1/16 of an astronaut, i.e. equal),
  the worst of the 12 candidates (smasher leap `Sg1~g3`, i.e. 6,8>7,6) -41. Depth 7 gave +35 to +41 for the same moves: odd depths see Blue's last move but not Red's answer, so
  the sign flips with parity. That is the horizon effect, not a real advantage.
* Red's best answers to the best three openings (depth 7, 48 replies each): `Ab9-b8` / `Ad9-d8`-type steps keep the score at -6; taking the drone fuel (`Ab9=c9`, `Ad9=c9`) gives Red a score of -2..0.
* In 182 games with a forced Blue first move (both sides AI, 0.3 s per move): Blue won **84 (46%)**, Red won 62 (34%), 36 were drawn or hit the 150-ply cap (20%).
  So **Blue (first mover) has a real but modest advantage, about 12 percentage points**, not a win. (The games reached only about 4 plies of search depth on average because 16 searches ran in parallel;
  they are decent but not deep play, so treat the percentages as tendencies.)

## 2. Openings

Search values (depth 8, exact, full window) and game results (13 games per forced first move, Blue's wins : draws : losses):

| Blue's first move | search value d8 | games W:D:L | remark |
|---|---|---|---|
| `Ah1-g2` (7,8>7,7) | -6 (top) | 9:2:2 | best in both tests |
| `Ah1-h2` (7,8>8,7) | -6 (top) | 9:1:3 | |
| `Ab1=c1` (1,8>2,8, take the drone's fuel) | -6 (top) | 7:3:3 | |
| `Ad1=c1` (3,8>2,8, same from d1) | -6 (top) | 6:1:6 | |
| `Ab1-a2` / `Ab1-b2` | top 4 at d7 (+41) | 7:4:2 / 7:1:5 | |
| `Af1-e2`, `Af1-f2`, `Ad1-c2` | middle | 6:2:5, 6:3:4, 6:0:7 | |
| `Af1~d2`, `Ad1~b2` (early jetpack jump) | lower | 6:3:4, 5:3:5 | spends fuel for nothing yet |
| `Af1~g2` (jump) | lower | 4:1:8 | worst of the astronaut moves in games |
| `Ad1-d2` | -6 (top at d8) | **1:7:5** | the games and the deep search disagree; mostly drawn games |
| free choice (no forced move) | | 5:5:3 | |
| smasher leap `Sg1~f3` / `Sg1~g3` | -41 (worst) | (not played) | clearly weakest first move in the search |

Pattern of the good openings (see `Openings.md`): **both sides begin by taking the drone's fuel** (`Ab1=c1`, `Ad1=c1`; Red `Ab9=c9`, `Ad9=c9`), then an astronaut steps towards the centre,
a second one takes fuel, and a jetpack jump (`~e4`) brings an astronaut next to the central fire where it refuels (`Ae4+`). Red sends the drone out around move 3-4 (`Dc9-d6`).
**The smasher does not move in the first four moves of any good line.**

## 3. How much is each piece worth (handicap games)

Blue plays without one piece, Red complete, first mover alternating, 49 games each (Blue's wins : draws : losses):

| Blue without | W:D:L | Blue's score* | what the loss means |
|---|---|---|---|
| nothing (baseline) | 24:6:19 | 0.53 | |
| shield (dome) | 18:10:21 | 0.46 | -0.07: moderate |
| drone (ship) | 16:15:18 | 0.48 | -0.05: converts fewer wins into draws, loses no more games |
| smasher | **10:2:37** | 0.22 | -0.31: the most valuable single piece |
| one astronaut | **5:9:35** | 0.20 | -0.33: an astronaut is worth about as much as the smasher |

(*score = (wins + draws/2) / games.) Ranking by value: **astronaut >= smasher >> shield > drone**.

## 4. Suggested weights (evaluation in `evaluate()`)

Weight duels: a changed value against the default, 44 games each, colours and first mover balanced (variant : default wins, rest draws). Differences of fewer than ~7 games are noise.

| Weight (now) | variant | variant : default | verdict |
|---|---|---|---|
| astronaut (100) | 70 | 14 : 26 | worse, keep 100 |
| astronaut (100) | 140 | 14 : 18 | slightly worse, keep 100 |
| **fuel per unit (55)** | **90** | **23 : 13** | **clearly better** -> use about 90 |
| fuel per unit (55) | 30 | 16 : 20 | slightly worse |
| smasher (220) | 120 | 22 : 16 | equal or better |
| smasher (220) | 350 | 16 : 17 | equal; the earlier 110-vs-220 result (22 : 7) and this one disagree, so the value is flat between 120 and 350: keep 220 |
| drone (40) | 0 / 100 | 17 : 18 / 15 : 19 | no effect, keep 40 |
| shield (40) | 0 / 100 | 16 : 19 / 20 : 16 | slightly better with more: use 70 |

**Recommendation:** `EV.fuel` 55 -> **90**, shield 40 -> **70**, everything else unchanged (astronaut 100, smasher 220, drone 40). Not applied to `index.html` (only suggested); to apply: change
`fuel: 55` in `const EV` and the shield line `x = 40 - 15 * (p.dmg || 0)` to `70 - ...`, then duel-test the combination against the old weights before committing.

## 5. The four questions

**Is it good to bring out the smasher early? No.** In the games, a side's first smasher move on its 3rd-4th move scored only 0.38 (17 sides), on the 5th-7th move 0.62 (60 sides), later 0.48-0.51.
Sides that moved the smasher 1-3 times in the game scored 0.69, 4-6 times 0.50, 7-10 times 0.43, 11+ times 0.39 (every smasher move is a tempo: it **must** move). The search rates a smasher leap as the weakest first move.
But never owning it is worse (section 3). Use it as a standing threat, release it from about your 5th-7th move when two or more enemy pieces stand on neighbouring hexes, or to kill a runner.

**When should the ship (drone) be used?** First as a **fuel pack in the opening** (nearly every good line starts with an astronaut taking its fuel, `Ab1=c1`); later sparingly. Sides that never moved the drone
scored 0.72 (47 sides, mostly a sign of a fast game that did not need it), 1-3 moves 0.49, 4-8 moves 0.47, 15+ moves 0.37: **drone moves are tempo spent**. Without the drone Blue wins fewer games (16 against 24) but
loses no more. Its value in the evaluation does not matter (0 to 100 all the same). Use it for one or two decisive pushes (off the board, into the fire, against an own piece); with the new unlimited range a drone
on an open line threatens from far away, but the AI did not use the long range more than the 3-hex range (earlier test in `AI_FINDINGS.md`: 8.6 drone moves per game both).

**How important is the dome (shield)?** Moderate: Blue without it loses about 0.07 of score (18:10:21 against 24:6:19), less than the smasher or an astronaut, more than the drone. Raising its value from 40 to 100
gave 20 : 16. It protects a runner or the Home Planet row and holds a prisoner for three enemy turns; the cheapest way to lose a game is to leave the Home Planet column undefended, not to lose the dome.

**Is it advantageous to focus on the central fire? Yes, the clearest result.** Sides that refuelled 0 times in a game scored 0.18 (57 sides), 1-2 times 0.42 (165), 3-5 times 0.61 (204), 6-9 times 0.79 (36).
The weight duel agrees (fuel 90 beats 55 by 23 : 13, fuel 30 is worse). Fuel is range: an astronaut reaches fuel + 1 steps, so the fire (and the two one-time side fires) decide who can jump to the enemy Home Planet.
Kills correlate in the same way (0 kills 0.23, 2-3 kills 0.54, 4-6 kills 0.70).

## 6. Tutorial hints that follow from the numbers

1. **Fuel first**: take the drone's fuel on move 1-2, bring a second astronaut up, refuel at the fire (`Ae4+`) whenever you are next to it; an astronaut with 0 fuel is a walker.
2. **Do not hurry the smasher.** Keep it home as a threat; release it around move 5-7 on a cluster; avoid moving it just to pass the turn.
3. **Do not waste fuel on early jetpack jumps** (`Af1~g2` was the worst astronaut opening); step to the centre, jump when the jump lands next to the fire or captures.
4. **Keep your pieces apart** (a smash kills everything on six hexes); keep the dome for a runner or the Home Planet row.
5. **Count tempo**: the player who needs fewer moves to bring two fuelled astronauts to the enemy half wins, since every drone or smasher move is a move not spent on that.
6. **Blue's first move is worth about 12 percentage points**, not a win: a good Red is fine if it copies the fuel opening.

## 7. Caveats

* The game statistics (sections 2-5) come from fast, shallow AI play (0.3 s per move, about 4 plies deep on average, noise 6); they describe **typical AI games**, not perfect play. Correlations (refuels, drone moves) can run both ways
  (a side that is winning has time to refuel). The weight duels and the handicap tests are controlled comparisons and are the stronger evidence.
* Samples are small (13 games per opening, 44-49 per weight/handicap variant); differences under ~7 games are noise. One disagreement (`Ad1-d2`, search top but 1:7:5 in games) shows how noisy the opening games are.
* The deep search values are of the static evaluation at the horizon: they say how the engine judges the position, not who wins. A real proof would need a tablebase-style solution of the whole game.
* Drone range is currently unlimited (test rule); the narrow-board experiment was rolled back.
