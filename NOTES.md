# Astro Game: project notes

Hand-over notes so a fresh Claude session (or a person) can continue the work. Written 2026-10-19.

## What it is

A chess-like, turn-based strategy game for two players (Blue at the bottom, Red at the top), prototyped as one
self-contained `index.html` (plain JavaScript, canvas, no build step, no libraries). The long-term target is the
Board platform, so everything is designed around "pieces on a display" (lift a piece, see legal squares, etc.).
Art style: "Der Kleine Astronaut" crayon look. The sprites live in `art/` (source art: `Standuhr/ASTRO/Art`).

Open `index.html` in Chrome or Edge from the folder that contains `art/`. The art is loaded relatively,
so without `art/` the game runs but the pieces and backgrounds are missing.

## Controls

- **Left mouse:** press on a piece, drag a transparent copy to a highlighted square, release to make the real move
  (the real piece stays put while you drag, then animates).
- **Release on the piece's own square:** refuel (only next to the sun).
- **Right mouse on a rover:** click = fire the laser in its current facing direction. Drag toward a side = turn the laser
  (90 degree steps). Turning and firing are separate moves.
- Buttons: New game, Undo move, Suggest move. A small text box below them (`#aiinfo`) shows depth, number of legal moves,
  positions searched and time of the last AI/suggested move. Dropdown "Players": Human Red (AI plays Blue, default), Human Blue
  (AI plays Red), No human (AI vs AI), Two humans. A "look-ahead" box sets the AI depth in double moves (1 to 7, default 7).

## Rules (current state)

Board: ONE 9x9 field (the earlier two-field/wormhole design was dropped on 2026-10-19). Owner 0 = Blue (home row 8, moves
up), owner 1 = Red (home row 0, moves down). The sun (fuel station) is the centre square (4,4): nobody may enter or jump
onto it. A turn is one move of one piece.

Pieces:
- **Astronaut:** walks one square forward or sideways (captures by walking onto an enemy). Jumps like a knight over
  pieces, costs 1 fuel (max 3, start with 2: `MAXFUEL`, `START_FUEL`), can jump on consecutive turns (no landing pause), cannot land on a Core. Refuels by 1
  when next to the sun and spending the move. Capturing an astronaut steals 1 fuel (capped at 3).
- **Fuel packs (rover and drone):** each carries 1 fuel unit (`VEH_FUEL`), starts full and refuels at the sun like an
  astronaut (spend the move on its own square). An astronaut (fuel < 3) in the 8-neighbourhood of an own rover/drone with
  fuel can play move kind `feed` (target = the vehicle's square): astronaut +1 fuel, vehicle -1, nobody moves. A vehicle's
  fuel is only used for feeding, never for moving. Drawn as one flame beside the vehicle.
- **Rover:** moves 1 or 2 squares straight, no jumping, captures by moving onto an enemy (not a Core). Has a **laser**:
  faint wobbling glow shows its aim; a shot destroys the first astronaut, drone or rover (either side, including own) in
  line; the shooter stays intact, so in a rover duel the first to shoot wins. The beam stops at the sun and Cores.
  (Earlier rule, removed: a beam hitting a rover burnt out both lasers; the `nolaser` flag is gone.)
- **Drone:** moves up to 3 squares in any of 8 directions, no jumping, cannot capture by moving. Dropping it on an enemy
  in range pushes that piece one square further along the line and the drone takes its square. The pushed piece is
  stunned for its next turn. Pushed off the board, or into one of the drone owner's own pieces = captured. Blocked if
  behind the target is the sun, a piece of the target's own side or a Core. Cores cannot be pushed.
- **Setup (per side):** Core at back-row centre (4, home). Four astronauts on the back row at columns 0, 3, 5, 8, the
  fifth in front of the Core at (4, home+-1). Rover and drone on the row in front of the home row: Blue rover at column 1 and
  drone at column 7, Red the other way round (drone column 1, rover column 7). Blue's rover starts with the laser aimed east, Red's west.
- **Winning:** walk an astronaut onto the enemy Core. Rovers and drones can never win.
- **Draws:** neither side has an astronaut left, the player to move has no legal move, or threefold repetition.
- "Undo move" takes back the last single move, for either colour, up to 4 moves deep (`UNDO_DEPTH`). It also switches the
  players dropdown to "Two humans" so the AI does not immediately replay.

## Code map (all in index.html, two scripts)

1. State, constants (`N`, `CELL`, `HOME`, `DIR`, `ARRIVE`, `DIRS4`, `KCOL`), `newGame`.
2. Rules: `at`, `arrival`, `beamTrace`, `legal(p)` returns moves `{x,y,kind,...}` with kinds
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
