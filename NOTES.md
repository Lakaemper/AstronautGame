# Astro Game: project notes

Hand-over notes so a fresh Claude session (or a person) can continue the work. Written 2026-10-19.

## What it is

A chess-like, turn-based strategy game for two players (Blue at the bottom, Red at the top), prototyped as one
self-contained `index.html` (plain JavaScript, canvas, no build step, no libraries). The long-term target is the
Board platform, so everything is designed around "pieces on a display" (lift a piece, see legal squares, etc.).
Art style: "Der Kleine Astronaut" crayon look. The sprites live in `art/` (source art: `Standuhr/ASTRO/Art`).

Page layout: the playfield column (`#main`: canvas + the "How to play" rules box underneath) is on the left, the control
panel (`#panel`: status, players, buttons, AI info box) on the right; the column shrinks to fit next to the panel.
Open `index.html` in Chrome or Edge from the folder that contains `art/`. The art is loaded relatively,
so without `art/` the game runs but the pieces and backgrounds are missing.

## Controls

- **Left mouse:** press on a piece, drag a transparent copy to a highlighted square, release to make the real move
  (the real piece stays put while you drag, then animates).
- **Drag onto the sun:** refuel (only for a piece standing next to the sun; the piece stays where it is, the move's target square is the sun hex).
- **Right mouse on a rover:** click = fire the laser in its current facing direction. Drag toward one of the six directions = turn the laser
  (60 degree steps). Turning and firing are separate moves.
- Buttons: New game, Undo move, Suggest move. A small text box below them (`#aiinfo`) shows depth, number of legal moves,
  positions searched and time of the last AI/suggested move. Dropdown "Players": Human Red (AI plays Blue, default), Human Blue
  (AI plays Red), No human (AI vs AI), Two humans. A "look-ahead" box sets the AI depth in double moves (1 to 7, default 7).

## Rules (current state)

Board: a RECTANGLE of 9 x 9 pointy-top hexes (81 cells); every odd row is shifted right by half a hex, so the left and
right edges are zig-zag. History: two 7x7 fields with wormholes -> square 9x9 -> hex rhombus -> this rectangle (2026-10-19).
Engine coordinates are AXIAL with a constant shift so the six directions are the same steps everywhere: `x = column -
floor(row/2) + AXS` (`AXS` = 4, keeps x >= 0), `y` = row. Helpers `toX(col,row)`, `colOf(x,y)`, `inB(x,y)` (rectangle test),
`hexDist`; lookup tables are sized `XN` x `ROWS`. Owner 0 = Blue (home row 8, moves up), owner 1 = Red (home row 0, moves
down). The sun (fuel station) is the centre hex (column 4, row 4), nobody may enter or jump onto it. A turn is one move.
The six directions `HEX6` are E, NE, NW, W, SW, SE (screen angle = -60 degrees x index).

Pieces:
- **Astronaut:** fuel is range. It can reach every hex within `fuel + 1` steps (hex distance): 0 fuel = the 6 neighbours,
  3 fuel = up to 4 steps. A 1-step move ('walk', or 'capture' on an enemy) is free; a longer move ('jump', carries `cost`)
  flies over everything except the sun (the sun cannot be crossed even in the air, see `flyDist`: two hexes on a straight line with the sun strictly between them are one step further apart, so the far side is 3 away, not 2), costs distance - 1 fuel, may capture where it lands, and can never land on a Core, so only a
  single step onto the enemy Core wins. Cannot land on own pieces or the sun. Fuel max 3 (`MAXFUEL`), start 1
  (`START_FUEL`). Refuels by 1 when next to the sun (drag it onto the sun; 6 neighbours) and spending the move.
  **Overcharge:** an astronaut may hold the full fuel (3) for one move only. The move that fills it up marks it `hot`; on its
  side's next move it must spend a charge by jumping (`kind` jump, cost >= 1) or it explodes (it is simply removed, no blast
  on neighbours; a stunned or shield-covered hot astronaut explodes too). A jump that steals fuel and ends at 3 again makes it hot
  again. `step` does this after every move (the `hot` field; the evaluation subtracts `EV.hot` = 40 for a hot astronaut, and the
  search sees the explosion, so the AI plans around it: no explosions in 12 AI-vs-AI games). The UI shows a pulsing red ring and a !. Capturing an astronaut steals
  1 fuel (capped at 3). (Earlier rules, removed: forward/sideways steps only, hex-knight jumps for 1 fuel.)
- **Fuel packs (rover and drone):** each carries 1 fuel unit (`VEH_FUEL`), starts full and refuels at the sun like an
  astronaut (drag it onto the sun, it stays put). An astronaut (fuel < 3) in the 6 neighbouring hexes of an own rover/drone with
  fuel can play move kind `feed` (target = the vehicle's square): astronaut +1 fuel, vehicle -1, nobody moves. A vehicle's
  fuel is only used for feeding, never for moving. Drawn as one flame beside the vehicle.
- **Rover:** moves exactly one hex in one of the six directions (it used to move 1 or 2), no jumping, captures by moving onto an enemy (not a Core). Has a
  **laser that needs fuel**: the rover starts EMPTY (fuel 0), so at the start both lasers are off (grey emitter point, no beam).
  It refuels at the sun like any piece (drag it onto the sun while next to it). With fuel (1 unit, `VEH_FUEL`) the faint
  wobbling glow shows its aim; a shot (right-click) destroys the first astronaut, drone or rover (either side, including own) in
  line, stops at the sun and Cores, and uses the fuel up (enough for a single shot). The shooter stays intact, so in a rover duel the
  first to shoot wins. Turning the aim (right-drag, one move, six directions) works without fuel. The fuel can instead feed a
  neighbouring astronaut (`feed`). The AI only generates laser/aim moves while the rover has fuel; the evaluation gives an armed
  rover `EV.rover + EV.armed` (50 + 35) and an empty one `EV.rover`.
  (Earlier rules, removed: a beam hitting a rover burnt out both lasers; the rover started with fuel and always had its laser.)
- **Drone:** moves up to 3 hexes along any of the six lines, no jumping, cannot capture by moving. Dropping it on an enemy
  in range pushes that piece one square further along the line and the drone takes its square. The pushed piece is
  stunned for its next turn. Pushed off the board, or into one of the drone owner's own pieces = captured. Blocked if
  behind the target is the sun, a piece of the target's own side or a Core. Cores cannot be pushed.
- **Shield** (type `shield`, one per side, glass half-sphere): moves one hex to any of the 6 neighbours (never the sun), also
  onto occupied hexes of either side, except Cores and other shields (move kind `cover`; it never captures). `at(x,y)` returns the shield instead of
  whatever stands under it, so a covered piece is invisible to captures, pushes, drone landings and laser hits (fully
  protected), and `covered(p)` pieces have no legal moves at all (no walking, laser or feeding) until the shield moves
  away. A shield cannot be captured, pushed, landed on or entered by any piece (`fixed(t)` includes it); a laser beam
  stops at it harmlessly. The owner's other pieces (astronaut, rover, drone) can move under their own shield when nothing is under it yet
  (`freeShield`; plain 'walk'/'jump' move onto the shield's hex, `step` then does not capture; rover/drone stop there and
  cannot pass through). One piece per shield; enemies never enter. Shield vs shield: no stacking.
  Damage (`dmg`, `hl` on the shield, handled at the end of `step`): a shield on an ENEMY piece gains 1 damage each time the
  covered piece's side finishes a move (cracked: drawn more transparent with cracks), at 2 it shatters and the piece is free
  (log text 'The shield shatters!'). A shield that is not on an enemy piece heals on the next move after it left (`hl` marks
  the pending heal). Hopping from one enemy piece straight to another keeps the damage. It does not need fuel. Evaluation value 40. Drawn last, on top
  of the pieces (`drawShield`): seen from above (deliberately not consistent with the side-view astronauts), a circle of
  hex size at 70% opacity, rim in the team colour. Starts two rows straight in front of the Core: Blue (4,6), Red (4,2).
- **Setup** (given as column,row): four astronauts per side (the front astronaut was removed). Blue: Core (4,8);
  astronauts (0,8), (3,8), (5,8), (8,8); drone (1,7), rover (7,7), shield (4,6). Red is Blue mirrored top to bottom (row -> 8-row), same
  columns: Core (4,0), astronauts (0,0), (3,0), (5,0), (8,0), drone (1,1), rover (7,1), shield (4,2). Both rovers start empty (laser off)
  with the aim pointing away from the board: Red NW (up), Blue SW (down). A pointy-top hex board has no exact north or south, so
  these two (the vertical mirror of each other) stand for it; nothing is in line at the start. Rotation by 180 degrees is NOT a symmetry (odd rows
  are shifted), the vertical mirror is.
- **Winning:** walk an astronaut onto the enemy Core. Rovers and drones can never win.
- **Draws:** neither side has an astronaut left, the player to move has no legal move, or threefold repetition.
- "Undo move" takes back the last single move, for either colour, up to 4 moves deep (`UNDO_DEPTH`). It also switches the
  players dropdown to "Two humans" so the AI does not immediately replay.

## Code map (all in index.html, two scripts)

1. State, constants (`COLS`, `ROWS`, `AXS`, `XN`, `HOME`, `CORE`, `STATION`, `HEX6`, `hexDist`, `KCOL`), `newGame`. Pixel geometry (UI script only):
   `HS`, `HW`, `ctrX/ctrY` (hex centre; linear, so fractional coordinates work for animations and beams), `hexPath`, `cellOf`
   (pixel -> hex with cube rounding, shift added back), `PS` (piece scale; sprites are drawn for 100 px cells).
2. Rules: `at`, `beamTrace` (end points in axial coordinates), `legal(p)` returns moves `{x,y,kind,...}` with kinds
   `walk capture jump refuel push laser aim`; `step(p, m)` mutates `pieces/turn/winner` and returns log text.
   `step` and `legal` are also used by the AI search on cloned states, so they must stay free of UI code.
3. `drawCheck`, `posKey`, `apply` (history for undo, move animation start), input handlers.
4. Animations: `buildAnim`, `visual`, `animate` (the game state is updated at once; the display lags via `anims`,
   `ghosts`, `animUntil`; input and the AI wait while `busy()`). Constants `TURN`, `SHIFT`, `FLY0` set the speed.
5. Art and drawing (the square surfaces are 5 procedural paper-cut pencil tiles from `makeTiles()`, handed out by `makeBoardLayer()` with a seeded RNG, never the same as the left/upper neighbour): sprite rectangles in `R`, `FRAMES` (astronaut turn frames: front, 45, profile, 135, back,
   mirrored for left), `crayon()` helper for hand-drawn shapes (rover), `drawField`, `drawPiece`.
6. AI: iterative-deepening minimax with alpha-beta and a 10 s time budget (`AI_MS`), random leaf jitter (`AI_NOISE`),
   evaluation in the `EV` weight table, draw contempt (`EV.draw = -600`).
   Move ordering in `genMoves`: captures by victim value (own victims last), forward moves, history table, two killer moves
   per ply, and a small transposition table (`hashState`, `ttMove`) that holds only the best move per position, so each
   deeper iteration starts with the previous best line. This gained about one ply in 5 s (opening: 5 -> 6 plies at a 5 s budget).
   Speed-up ideas not done: make/unmake instead of cloning the piece list in `child`, TT value cutoffs.

### Engine / worker split and pondering (added 2026-10-19)

`index.html` has two script blocks. `<script id="engine">` holds the constants, the rules (`at`, `legal`, `step`...) and the
whole AI (`genMoves`, `minimax`, `aiSearch`, `packResult`, `ponderSearch`). It must stay free of DOM code, because the
page also copies its text into a Web Worker (Blob URL; `WORKER_GLUE` adds the message handler). The second script is
the UI. All AI searches (the AI's move, "Suggest move") run in the worker, so the board never freezes. If the worker
cannot be created, `search()` falls back to a blocking search on the main thread.

Pondering: while it is the human's turn against the AI (roles "Human: Red/Blue"), `startPonder()` sends the position to
the worker. `ponderSearch` looks at EVERY legal human reply, skips only the suicidal ones (after a 2-ply look a reply
is skipped if it is more than `SUICIDE` = 110 worse than the best reply), and for each remaining reply searches the AI's
best answer deeper and deeper with NO time limit (ends at the look-ahead maximum). Likely replies (the ones worst for
the AI) get the deeper passes first (reply rank limit halves every 2 plies). Each result is posted at once and kept in
`pond.table` keyed by `msig` (a piece-index-free move signature). When the human moves, `apply` picks the matching entry
(`ponderHit`) and stops the worker; `maybeAI` plays it immediately if its depth is at least that of the last normal
search (`lastAiDepth`, min 4), otherwise it runs a normal 10 s search. "Suggest move" and undo stop pondering; it restarts
after the AI's next move. The info box shows the pondering status (replies, skipped, depth).
Moves a human can make that `legal()` never generates (firing or aiming a laser at nothing) are always a miss.

## AI evaluation (positive = good for Blue)

Per astronaut: 100 + 14 per fuel + 16 per row advanced + closeness to the enemy Core (5 per step within 8) + 150 when one
step from the Core; a rover is 45 (+40 if its laser still works); a drone is 40. A draw scores -600 for the side
searching. These weights were retuned only superficially after the 9x9 change (3 quick depth-2 self-play games: two
repetition draws, one Blue win), so treat them as a starting point; the old tuning was for the two-field game.

## How the logic was tested

No test files in the repo. The approach used: extract the `<script>` body, stub `document`, `Image`, `performance` etc.,
`eval` it in Node, and drive `newGame`, `legal`, `apply`, `aiSearch(side)` directly (self-play, unit checks of
`beamTrace`, Core-capture rules). Visual checks were done by serving the folder with `python -m http.server`
and loading it in a browser. A freezing trick for animations: override `performance.now` to a fixed value, then `draw()`.

## Working preferences (from the user)

- Ask before changing code when the user only says "let's ..."; explicit requests ("add", "make", "fix") are go-aheads.
- Keep designs simple; propose the simplest mechanism first.
- After changing `index.html`, the author likes to receive the updated file directly (it was sent through the Claude
  desktop session's file-send tool, since the author also works from a second PC).
- The author often asks "why can't X do Y?" with a screenshot: answer from the rules above, and check the position in
  Node before blaming the rules (twice this found a real bug, for example a missing highlight colour for a move kind).

## Ideas not done

- Physical-piece features for Board (fuel token on the backpack, lift-to-preview on real pieces).
- A fuel-station art piece (the sun is the stand-in), a rover sprite in the original art (drawn in code now).
- A deeper AI (it only searches a limited number of half-moves in its 10 s budget), a better defence against the opponent's laser aim.
- A win/lose screen with the unused sprites from the art folder (banner, balloon, etc.).
