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
- Buttons: New game, Undo Blue move, Suggest move. Dropdown "Players": Human Red (AI plays Blue, default), Human Blue
  (AI plays Red), No human (AI vs AI), Two humans. A "look-ahead" box sets the AI depth in double moves (default 5).

## Rules (current state)

Board: two 7x7 fields side by side. Field 1 (left) is the main field, field 2 (right) holds the Cores.
Owner 0 = Blue (home row 6, moves up), owner 1 = Red (home row 0, moves down). The sun (fuel station) is the centre
square (3,3) on both fields: nobody may enter or jump onto it. A turn is one move of one piece on either field.

Pieces:
- **Astronaut:** walks one square forward or sideways (captures by walking onto an enemy). Jumps like a knight over
  pieces, costs 1 fuel (max 2), not on the turn right after a jump (landing cooldown), cannot land on a wormhole or a
  Core. Refuels by 1 when next to the sun and spending the move. Capturing an astronaut steals 1 fuel (capped at 2).
- **Rover:** moves 1 or 2 squares straight, no jumping, captures by moving onto an enemy (not a Core, wormhole,
  shielded piece). Has a **laser**: faint wobbling glow shows its aim; a shot destroys the first astronaut (either side,
  including own, unless shielded) or drone (either side) in line, whole field. The beam stops at the sun, wormholes,
  Cores and rovers. If a beam hits a rover (either side), both lasers burn out for good (no glow, grey emitter).
- **Drone:** moves up to 3 squares in any of 8 directions, no jumping, cannot capture by moving. Dropping it on an enemy
  in range pushes that piece one square further along the line and the drone takes its square. The pushed piece is
  stunned for its next turn (cannot act). Pushed off the board, or pushed into one of the drone owner's own pieces =
  captured. Blocked if behind the target is the sun, a piece of the target's own side, a Core or a wormhole.
  Cores and wormholes cannot be pushed.
- **Field 1 setup (per side):** a wormhole (where the Core would be) at the back-row centre, a rover at column 1, a drone
  at column 5 on the back row, 3 astronauts (columns 2 to 4) in front.
- **Field 2 setup (per side):** only a Core at the back-row centre and one drone directly in front of it.
- **Wormhole:** an astronaut that WALKS (not jumps) onto the enemy wormhole leaves field 1 and appears on field 2
  next to its own Core. Landing squares in order east, middle, west: Blue (4,6),(3,5),(2,6); Red (4,0),(3,1),(2,0).
  If all three are occupied, entering is blocked. It arrives WITHOUT fuel and is shielded (cannot be captured, pushed or
  lasered) through the enemy's next turn.
- **Winning:** walk an astronaut onto the enemy Core on field 2. Rovers and drones can never win.
- **Draws:** neither side has an astronaut left (dead draw), the player to move has no legal move (stalemate), or the same
  position occurs three times (repetition).
- Undo goes back to just before Blue's last move (drops Red's reply too) and switches the players dropdown to
  "Two humans" so the AI does not immediately replay.

## Code map (all in index.html, one script)

1. State, constants (`N`, `CELL`, `HOME`, `DIR`, `ARRIVE`, `DIRS4`, `KCOL`), `newGame`.
2. Rules: `at`, `arrival`, `beamTrace`, `legal(p)` returns moves `{x,y,kind,...}` with kinds
   `walk capture jump refuel push warp laser aim`; `step(p, m)` mutates `pieces/turn/winner` and returns log text.
   `step` and `legal` are also used by the AI search on cloned states, so they must stay free of UI code.
3. `drawCheck`, `posKey`, `apply` (history for undo, move animation start), input handlers.
4. Animations: `buildAnim`, `visual`, `animate` (the game state is updated at once; the display lags via `anims`,
   `ghosts`, `animUntil`; input and the AI wait while `busy()`). Constants `TURN`, `SHIFT`, `FLY0` set the speed.
5. Art and drawing: sprite rectangles in `R`, `FRAMES` (astronaut turn frames: front, 45, profile, 135, back,
   mirrored for left), `crayon()` helper for hand-drawn shapes (rover, rings), `drawField`, `drawPiece`, `drawWorm`.
6. AI: iterative-deepening minimax with alpha-beta and a 2.5 s time budget (`AI_MS`), random leaf jitter (`AI_NOISE`),
   evaluation in the `EV` weight table, `warpBonus` (stepping into the wormhole is worth more the sooner it happens,
   which fixed the AI postponing it forever), draw contempt (`EV.draw = -600`).

## AI evaluation (positive = good for Blue)

Per astronaut: 100 + 14 per fuel + advancement (16 per row on field 1, 14 on field 2) + 450 for being past the wormhole
+ 150 when one step from the enemy wormhole (and a landing square is free) + a small closeness-to-goal term; a rover is
45 (+40 if its laser still works); a drone is 40. A draw scores -600 for the side searching, so the AI avoids draws
unless it is clearly worse. Weights were tuned by AI-vs-AI self-play (short 80 ms games); results were noisy, so treat
them as a starting point. Known: when the AI declines the wormhole it is often for a sound defensive reason.

## How the logic was tested

No test files in the repo. The approach used: extract the `<script>` body, stub `document`, `Image`, `performance` etc.,
`eval` it in Node, and drive `newGame`, `legal`, `apply`, `aiSearch(side)` directly (self-play, unit checks of
`beamTrace`, wormhole and shield rules). Visual checks were done by serving the folder with `python -m http.server`
and loading it in a browser. A freezing trick for animations: override `performance.now` to a fixed value, then `draw()`.

## Working preferences (from the user)

- Ask before changing code when the user only says "let's ..."; explicit requests ("add", "make", "fix") are go-aheads.
- Keep designs simple; propose the simplest mechanism first.
- After changing `index.html`, the author likes to receive the updated file directly (it was sent through the Claude
  desktop session's file-send tool, since the author also works from a second PC).
- The author often asks "why can't X do Y?" with a screenshot: answer from the rules above, and check the position in
  Node before blaming the rules (twice this found a real bug, for example a missing highlight colour for wormhole moves).

## Ideas not done

- Physical-piece features for Board (fuel token on the backpack, lift-to-preview on real pieces).
- A fuel-station art piece (the sun is the stand-in), a rover sprite in the original art (drawn in code now).
- A deeper AI (it only searches roughly 4 to 6 half-moves in 2.5 s), a better defence against the opponent's laser aim.
- A win/lose screen with the unused sprites from the art folder (banner, balloon, etc.).
