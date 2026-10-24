# Astro Game: project notes

Hand-over notes so a fresh Claude session (or a person) can continue the work. Written 2026-10-19.

## What it is

A chess-like, turn-based strategy game for two players (Blue at the bottom, Red at the top), prototyped as one
self-contained `index.html` (plain JavaScript, canvas, no build step, no libraries). The long-term target is the
Board platform, so everything is designed around "pieces on a display" (lift a piece, see legal squares, etc.).
Art style: "Der Kleine Astronaut" crayon look. The sprites live in `art/` (source art: `Standuhr/ASTRO/Art`).

Page layout: the playfield column (`#main`: canvas + the "How to play" rules box underneath) is on the left, the control
panel (`#panel`: status, players, buttons, AI info box) on the right; the column shrinks to fit next to the panel.
The panel no longer shows a title or status text: `#turn` and `#msg` still exist but are `hidden` (the code writes to them, e.g. `say()`),
so messages such as 'Illegal landing' or online errors are not visible. At its top is the blue/red position gauge (`#gauge`, `updateGauge()`
called from `updateUI()`): the static `evaluate()` of the current position squashed with 1/(1+exp(-v/250)), the blue/red boundary itself moves with the score (no extra marker); label text 'Blue +1.2' =
about 1.2 astronauts ahead (v/150).
Open `index.html` in Chrome or Edge from the folder that contains `art/`. The art is loaded relatively,
so without `art/` the game runs but the pieces and backgrounds are missing.

## Controls

- **Left mouse:** press on a piece, drag a transparent copy to a highlighted square, release to make the real move
  (the real piece stays put while you drag, then animates).
- **Drag onto the sun:** refuel (only for a piece standing next to the sun; the piece stays where it is, the move's target square is the sun hex).
- **(Removed 2026-10-23) Right mouse on a smasher:** click = fire the laser in its current facing direction. Drag toward one of the six directions = TURN AND FIRE in
  that direction in one move (60 degree steps); a smasher without fuel can only turn.
- Buttons: New game, Undo move, Suggest move. A small text box below them (`#aiinfo`) shows depth, number of legal moves,
  positions searched and time of the last AI/suggested move. Dropdown "Players": Human Red (AI plays Blue, default), Human Blue
  (AI plays Red), No human (AI vs AI), Two humans. A "look-ahead" box sets the AI depth in double moves (1 to 7, default 7).

## Rules (current state)

Board: 9 rows of pointy-top hexes, 77 cells: the 5 even rows have 9 hexes and the 4 odd rows (shifted right by half a hex) have 8, because the
rightmost hex of each odd row was removed (2026-10-22) so that the right edge is almost straight; only the left edge is zig-zag. `inB` tests `col < COLS - (y & 1)`,
the canvas width is `HW * COLS`. The board is now left-right symmetric (about the middle of the Home Planet column); the start setup is not: the drone stands at x = 1.5 and the smasher at x = 7.5 on the odd row. History: two 7x7 fields with wormholes -> square 9x9 -> hex rhombus -> this rectangle (2026-10-19).
Engine coordinates are AXIAL with a constant shift so the six directions are the same steps everywhere: `x = column -
floor(row/2) + AXS` (`AXS` = 4, keeps x >= 0), `y` = row. Helpers `toX(col,row)`, `colOf(x,y)`, `inB(x,y)` (rectangle test),
`hexDist`; lookup tables are sized `XN` x `ROWS`. Owner 0 = Blue (home row 8, moves up), owner 1 = Red (home row 0, moves
down). The sun (fuel station) is the centre hex (column 4, row 4), nobody may enter or jump onto it. A turn is one move.
The six directions `HEX6` are E, NE, NW, W, SW, SE (screen angle = -60 degrees x index).

Pieces:
- **Astronaut:** fuel is range. It can reach every hex within `fuel + 1` steps (hex distance): 0 fuel = the 6 neighbours,
  3 fuel = up to 4 steps. A 1-step move ('walk', or 'capture' on an enemy) is free; a longer move ('jump', carries `cost`)
  flies over everything except the sun (the sun cannot be crossed even in the air, see `flyDist`: two hexes on a straight line with the sun strictly between them are one step further apart, so the far side is 3 away, not 2), costs distance - 1 fuel, may capture where it lands, and can never land on a Home Planet, so only a
  single step onto the enemy Home Planet wins. Cannot land on own pieces or the sun. Fuel max 3 (`MAXFUEL`), start 1
  (`START_FUEL`). Refuels by 1 when next to the sun (drag it onto the sun; 6 neighbours) and spending the move.
  **Overcharge:** an astronaut may hold the full fuel (3) for one move only. The move that fills it up marks it `hot`; on its
  side's next move it must spend a charge by jumping (`kind` jump, cost >= 1) or it explodes (it is simply removed, no blast
  on neighbours; a stunned or shield-covered hot astronaut explodes too). A jump that steals fuel and ends at 3 again makes it hot
  again. `step` does this after every move (the `hot` field; the evaluation subtracts `EV.hot` = 40 for a hot astronaut, and the
  search sees the explosion, so the AI plans around it: no explosions in 12 AI-vs-AI games). The UI shows a pulsing red ring and a !. Capturing an astronaut steals
  1 fuel (capped at 3). (Earlier rules, removed: forward/sideways steps only, hex-knight jumps for 1 fuel.)
- **Fuel packs (smasher and drone; the smasher part is SUPERSEDED, it has no fuel any more):** a drone carries 1 fuel unit (`VEH_FUEL`), a smasher up to 2 (`SMASHER_FUEL`, helper `fuelCap(p)`); a drone starts full and refuels at the sun like an
  astronaut (drag it onto the sun, it stays put). An astronaut (fuel < 3) in the 6 neighbouring hexes of an own smasher/drone with
  fuel can play move kind `feed` (target = the vehicle's square): astronaut +1 fuel, vehicle -1, nobody moves. A vehicle's
  fuel is only used for feeding, never for moving. Drawn as one flame beside the vehicle.
- **Smasher (SUPERSEDED 2026-10-23, see 'Smasher rework' at the end of this file):** moves one hex in one of the six directions, but a smasher that has never moved may take TWO hexes along a line on its
  first move (like a chess pawn: `fresh` flag, switch `SMASHER_DOUBLE` in the engine block; the first hex of the double step
  must be free, the second hex may hold an enemy that is CAPTURED (never a shield or Home Planet), but it cannot move under a shield, and the sun blocks it; the flag is lost with the first change of position). No jumping, captures by moving onto an enemy (not a Home Planet). Has a
  **laser that needs fuel**: the smasher starts EMPTY (fuel 0), so at the start both lasers are off (grey emitter point, no beam).
  It refuels at the sun like any piece (drag it onto the sun while next to it). It holds up to 2 units (`SMASHER_FUEL`; a fire fills it, the sun gives +1 per move) and each shot costs ONE unit, so a full
  smasher has two shots. With fuel the faint wobbling glow shows its aim; a shot destroys the first astronaut, drone or smasher (either
  side, including own) in line, stops at the sun and Home Planets, and the shooter stays intact, so in a smasher duel the first to shoot wins.
  **Turning and shooting is one move** (the old separate `aim` move is gone from `legal()`; the smasher turns to the target and fires,
  `step` sets `dir` from the move). Only a smasher without fuel can still just turn (right-drag, kind `aim`, human only). A shot at an
  ENEMY SHIELD is a legal move too (kind `laser`, target = the shield's hex): the beam stops at a shield and damages it (`beamTrace`
  returns `shield`): 1st hit cracks it, 2nd hit shatters it (see Shield damage below). The fuel can instead feed a neighbouring
  astronaut (`feed`). The evaluation gives an armed smasher `EV.smasher + EV.armed` (50 + 35) and an empty one `EV.smasher`.
  (Earlier rules, removed: a beam hitting a smasher burnt out both lasers; the smasher started with fuel and always had its laser.)
- **Drone:** moves up to 3 hexes along any of the six lines, no jumping, cannot capture by moving. Dropping it on an enemy
  in range pushes that piece one square further along the line and the drone takes its square. The pushed piece is
  stunned for its next turn. Pushed off the board, into the central fire (rule added 2026-10-22), or into one of the drone owner's own pieces = captured. Blocked if
  behind the target is a piece of the target's own side or a Home Planet. Home Planets cannot be pushed.
- **Shield** (type `shield`, one per side, glass half-sphere): moves one hex to any of the 6 neighbours (never the sun), also
  onto occupied hexes of either side, except Home Planets and other shields (move kind `cover`; it never captures). `at(x,y)` returns the shield instead of
  whatever stands under it, so a covered piece is invisible to captures, pushes, drone landings and laser hits (fully
  protected), and `covered(p)` pieces have no legal moves at all (no walking, laser or feeding) until the shield moves
  away. A shield cannot be captured, pushed, landed on or entered by any piece (`fixed(t)` includes it); a laser beam
  stops at it harmlessly. The owner's other pieces (astronaut, smasher, drone) can move under their own shield when nothing is under it yet
  (`freeShield`; plain 'walk'/'jump' move onto the shield's hex, `step` then does not capture; smasher/drone stop there and
  cannot pass through). One piece per shield; enemies never enter. Shield vs shield: no stacking.
  Damage (`dmg`, `hl` on the shield, handled at the end of `step`): a shield on an ENEMY piece gains 1 damage each time the
  covered piece's side finishes a move (cracked: drawn more transparent with cracks), at 2 it is cracked twice (more cracks drawn), at 3 it shatters (changed 2026-10-22 from 2: the prisoner is held one turn longer; a smasher's laser still breaks it at 2 damage) and the piece is free
  (log text 'The shield shatters!'). A shield that is not on an enemy piece heals on the next move after it left (`hl` marks
  the pending heal). Hopping from one enemy piece straight to another keeps the damage. LASER damage: a smasher's beam adds 1 damage
  and sets `hl = -1`, so the shield only heals after one more move than usual; the owner gets exactly one reply to move the shield away
  (or to stop the smasher) before a second shot would break it. Evaluation: a cracked shield is worth 15 less per damage point. It does not need fuel. Evaluation value 40. Drawn last, on top
  of the pieces (`drawShield`): seen from above (deliberately not consistent with the side-view astronauts), a circle of
  hex size at 70% opacity, rim in the team colour. Starts two rows straight in front of the Home Planet: Blue (4,6), Red (4,2).
- **Setup** (given as column,row): four astronauts per side (the front astronaut was removed). Blue: Home Planet (4,8);
  astronauts (1,8), (3,8), (5,8), (7,8) (the outer two were at columns 0 and 8 until 2026-10-22); drone (2,8), smasher (6,8), shield (4,6) (back row 1..7 = A drone A Home Planet A smasher A; the four corner hexes (0,0),(8,0),(0,8),(8,8) do not exist, 73 hexes). Red is Blue mirrored top to bottom (row -> 8-row), same
  columns: Home Planet (4,0), astronauts (1,0), (3,0), (5,0), (7,0), drone (2,0), smasher (6,0), shield (4,2). Both smashers start empty (laser off)
Start setup box (UI, right of the board): Blue/Red x Human/AI tick table (replaces the old Players select; `roleSel` is a shim with the old values red/blue/none/two), astronauts 2 or 4 (2 = only the inner ones), smasher/drone/shield checkboxes; applied by "New game". For online games the choice travels in the link as `&s=4111` (astronauts, smasher, drone, shield) and locks the box.
  with the aim pointing away from the board: Red NW (up), Blue SW (down). A pointy-top hex board has no exact north or south, so
  these two (the vertical mirror of each other) stand for it; nothing is in line at the start. Rotation by 180 degrees is NOT a symmetry (odd rows
  are shifted), the vertical mirror is.
- **Winning:** walk an astronaut onto the enemy Home Planet. Smashers and drones can never win.
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
   mirrored for left), `crayon()` helper for hand-drawn shapes (smasher), `drawField`, `drawPiece`.
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

Per astronaut: 100 + 14 per fuel + 16 per row advanced + closeness to the enemy Home Planet (5 per step within 8) + 150 when one
step from the Home Planet; a smasher is 45 (+40 if its laser still works); a drone is 40. A draw scores -600 for the side
searching. These weights were retuned only superficially after the 9x9 change (3 quick depth-2 self-play games: two
repetition draws, one Blue win), so treat them as a starting point; the old tuning was for the two-field game.

## How the logic was tested

No test files in the repo. The approach used: extract the `<script>` body, stub `document`, `Image`, `performance` etc.,
`eval` it in Node, and drive `newGame`, `legal`, `apply`, `aiSearch(side)` directly (self-play, unit checks of
`beamTrace`, Home Planet-capture rules). Visual checks were done by serving the folder with `python -m http.server`
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
- A fuel-station art piece (the sun is the stand-in), a smasher sprite in the original art (drawn in code now).
- A deeper AI (it only searches a limited number of half-moves in its 10 s budget), a better defence against the opponent's laser aim.
- A win/lose screen with the unused sprites from the art folder (banner, balloon, etc.).

## Fuel fires (added 2026-10-21)

Two one-time fuel fires lie in the middle row, at the second and second to last column (`add('fire', 2, ...)` in `newGame`; type `fire`,
owner 2, a floor token: `at()` never returns it, so pieces walk, jump and shoot over it). A piece that LANDS on one (walk, capture, jump,
or a drone's push glide) uses it up and is refuelled, only that piece: an astronaut +1 but never above `MAXFUEL - 1` (a fire cannot overcharge),
a smasher or drone is filled (`VEH_FUEL`). A first version refuelled every fuelable piece of the landing side; with it the AI always sent its
drone (3 hexes per move) to a fire on its second move, and Blue won 39 of 47 decided AI-vs-AI games, so it was replaced. The permanent fuel
station in the middle is drawn as a big fire of three flames (`drawStation`), the one-time fires as one small flame (`drawFire`). Flame shapes
are picked at random every ~120 ms (`flick`), sizes and glow are constant (`FLAME_K` equalises the four shapes).

## Smasher artwork (2026-10-21)

The smasher is drawn in code in a paper-cut pencil style (`drawSmasher`, helpers `paper`, `wobblyPath`, `circlePts`): wobbly cut edges, a soft
shadow under every paper layer, two directions of pencil hatching, heavy outline. Parts: six-spoke wheels with tread, team-coloured chassis
with cream stripe, rivets, headlight and bumper, solar panel with cells, glossy cockpit dome, dish with a red tip. The laser is a separate
barrel drawn in `drawPiece`, rotated to the aim: dark steel with a red band and a yellow lens when armed (fuel), grey when empty.

## Tutorial page (2026-10-21)

`TUTORIAL.html` (next to `index.html`, needs the `art` folder) shows every move with the game's own pieces: the drawing code (`drawPiece`, `drawSmasher`,
`drawShield`, fires, sprite table `R`) is copied into it, so it must be regenerated when the game's art or rules change. The generator
(`build_tutorial.py` + `tutorial_template.html`) was kept outside the repo. The main page has a "Tutorial" button that opens it; the old
"How to play" box on the main page was removed (its text moved into the tutorial cards).

## 3D models for printing (2026-10-21)

`models/make_models.py` (pure Python, no libraries) builds printable STL files of three pieces from simple solids (spheres, lathe solids, prisms):
`astronaut` (about 41 mm tall), `smasher` (shrunk to 70% so it fits the base; laser barrel points forward) and `drone_red_ship` (a rocket ship with
swept wings and two engine pods, 34.5 mm tall). Every piece stands on a flat round base of 1 inch (25.4 mm) across and 4 mm thick (the usual tabletop
miniature base: 25 mm for Medium and Small creatures, and 3D-printed bases are most often about 4 mm thick). Curves use 64 segments (`SEG`).
Run `python make_models.py [scale]` to regenerate the STL files and `preview.html` (an offline viewer: drag to rotate, wheel to zoom).
Each STL is a union of closed overlapping solids (slicers merge them). Earlier versions also had the Blue rocket drone, the shield dome, the two
Home Planets and the two fires (24 mm bases); they were dropped on request and can be rebuilt from the git history.

## Online play for two humans (2026-10-21)

Two friends can play over the net. `serve.py` (standard library only; it replaces the plain static server on Lightsail) relays moves:
`POST /api/new` creates a room (the creator gets a random colour), `POST /api/join` gives the friend the other colour (later visitors only
watch), `POST /api/move {room, token, i, sig}` appends a move (checked: it must be that colour's turn and index `i` must be the next one; Blue
moves first and the turns alternate), and `GET /api/events` is a Server-Sent-Events stream that replays the old moves ('ready' marks the end of
the backlog) and then delivers new ones live, with 'presence' events for the two players. Rooms live in `rooms.json` (ignored by git), so a server
restart keeps games running; rooms older than 14 days are dropped. The server listens on IPv4 and IPv6.

In the page everything funnels through `apply()`: it computes the move signature (`msig`, independent of piece numbers) before the step, sends our own
moves with `postMove`, and skips animations while the backlog replays (`replaying`). A friend's move comes back through `resolveSig`, which finds the
piece and the move (a laser aimed at nothing is parsed from the signature because `legal()` does not generate it), and is applied with the normal
animation. The seat key lives in the address hash (`?room=ID#k=TOKEN`), so reloading or reopening that address returns to the same seat; the link to
send is `?room=ID` without the key. Online games have no undo, no suggestions and no AI (the players menu is locked). The "New game" button
leaves the online game after a confirmation. Tests used: a Python script that drives the server (turn order, seats, SSE, reconnect with Last-Event-ID,
restart persistence) and two browser tabs on this PC. Note: with plain `http.server` a browser may try `::1` first; `serve.py` now listens on both.

Display ranges (UI, checkbox in the second box, on by default): `rangeBoundary()` takes, per colour, the hexes every piece of that colour can move to (`legal()` kinds walk/capture/jump/push/cover) plus the pieces' own hexes, and returns the edges where the region ends; `drawRanges()` draws them in the colour (dark underlay), an edge that bounds both colours' regions is dashed in both colours alternately. Cached by `posKey()`.

Home Planet moves (2026-10-22): a Home Planet may sidestep one hex E/W onto an EMPTY hex (`walk`), and `resign` = drag it onto the central fire: `step` sets `winner = 1 - owner` (log text kept, not the 'reached the Home Planet' text), the UI asks `confirm()` first. The AI never generates `resign` (skipped in `genMoves`). Because the Home Planet can move, `evaluate()` finds it with `coreOf(owner)` instead of the constant `CORE` (which is only the start fallback).

Start colour selector (setup box, `startSel`, Blue default): `newGame()` sets `turn` from it. Online games always start with Blue (the selector is set to Blue and locked), because serve.py checks move order by parity (Blue = even moves).

Online options (2026-10-22): the HOST's choices travel through the server, not the link. `POST /api/new {setup:'4111', start:0|1, color:0|1|null}` (setup = astronauts, smasher, drone, shield; color = the colour the host plays, null = random) is stored in the room; `/api/new` and `/api/join` answer with `setup`, `start`, `host`, and `/api/move` checks turn order as `(moves + start) % 2`. In the UI the first Human column of the table means Host when pressing 'Online game' (tick Human on the colour you want; 'two'/'none' = random colour); online the headers read Host/Guest and the table shows the host's colour. Online `aiOff = true` keeps the AI out. serve.py must be restarted when deployed; a new client with an old server would play the default game.

A Home Planet cannot sidestep while an enemy astronaut (not covered by a shield) stands on one of its 6 neighbour hexes ('pinned' in `legal()`); resigning stays possible.

ART_SHEET.html: one page with every picture and animation frame of the game (the 7 PNG files with their frame rectangles, astronaut facing/held/flight frames, piece states, shield stages, Home Planet pulse, fires, flame and explosion frames, laser beam, board tiles, sticker sheet, move-highlight colours). It is generated from the drawing code copied from TUTORIAL.html plus `makeTiles()` copied from index.html (builder script was `build_sheet.py` in the session scratchpad; regenerate it when the art code changes).

ALL ART IS PNG (branch feature/fantasyOption, 2026-10-22). Nothing that is artwork is painted by code any more; the old procedural drawing (crayon(), paper(), wobblyPath(), drawSmasher(), makeTiles(), gradients for shield, glow, sky, beam) was exported once to PNG and then removed from index.html and TUTORIAL.html. To re-skin the game, replace the files in art/ and keep the frame layout (all sizes in px, `blit(img, sx, sy, sw, sh, dx, dy, dw, dh)` cuts a frame):
- (REMOVED 2026-10-25, see the end of this file) AstroRoverBlue/Red.png 220x184: local frame x -52..58, y -82..10 (2x); drawn at k = s*.95*.92. AstroBarrelArmed/Empty.png 80x40: local x -2..38, y -10..10 (2x), pivot at the origin, points east; the game rotates it to the aim.
- AstroShield.png 1248x208: six 208x208 frames (Blue 0/1/2 cracks, Red 0/1/2); opacity is baked in, the game only fades it. AstroBase.png 480x60: three 160x60 frames (Blue, Red, neutral). AstroShadow.png 160x60. AstroHotRing.png 200x80 (pulsed by scale and alpha). AstroBang.png 80x100 ('!'). AstroZzz.png 148x144. AstroGlow.png 256x256 (radial glow, tinted by alpha).
- AstroTiles.png 500x100: five 100x100 ground tiles (translucent, laid over the green hex tint). AstroSky.png 858x772: the board background. AstroBeam.png 1024x80: two flicker frames of 512 px; each is a left cap (px 2-28), a stretchable middle (28-484) and a right cap (484-510).
- AstroHexes.png 960x880: 19 hex frames of 192x220 px (96x110 game px), 5 per row: frames 0-14 = green tint 0-2 x ground tile 0-4 (index tint*5+tile), 15 blue baseline wash, 16 red baseline wash, 17 yellow refuel wash, 18 outline. The board layer stacks tint+tile, wash, outline per hex. AstroBanner.png 1176x1188: three 588x396 frames (Blue wins, Red wins, Draw), drawn centred over the board when the game ends. (AstroTiles.png, the five bare ground tiles, is the source of the hex frames and is only shown on the art sheet.)
Still code, on purpose (the only drawing code left): move-hint fills and outlines (incl. the jump arc and the hover ring), the 'Display ranges' lines, the hint arrow, the last-move outline, and the smasher aim guide line with its wobble. Text in the page itself is HTML. The Home Planets and the sticker stars/planets come from AstroBG.png as before.

THEMES (2026-10-22): two complete art sets with the same file names and layout, `art/` (space, the original) and `art/fantasy/` (fantasy). The 'Theme' button beside 'Tutorial' switches them in place (the game in progress stays); the choice is stored in localStorage (`astroTheme`) and `?theme=fantasy|space` forces one. TUTORIAL.html and ART_SHEET.html follow the same stored choice. Code: `THEME`, `loadAllArt()`, `THEME_RECTS` + `applyThemeRects()` in index.html (the fantasy sheets are laid out differently, so frame rectangles for the astronaut frames, the wave pose, the drone, the two Home Planets and the stickers are per theme; everything else is identical), `AstroCrystal.png` (fantasy only) replaces the flame on the one-time fuel fires.
The fantasy art was cut out of one ChatGPT contact sheet (`tools/fantasy_extract/src.webp`, 1536x1024, fake checkerboard background) by `tools/fantasy_extract/` (lib.py: background removal; ex1.py/ex2.py: cut each sprite; build_fantasy.py: scale, anchor and assemble the files, write `art/fantasy/theme.json`). Mapping: wizard poses -> astronaut frames (front, 3/4 mirrored, profile, back 3/4, back, orb-raised wave), dragon = drone, golem = smasher, cannon = laser barrel, glass sphere with a castle = shield (cracks and the red version are generated), blue flames = fuel flames, gold star = '!' mark, 'Zzz' swirl, gold ring = overcharge ring, crystal = fuel fire, flag banners with generated lettering, panorama (blurred and darkened) = board background. The ground tiles are darkened and desaturated so that the pieces stand out. The sheet is low resolution (a wizard is about 150 px tall); replacing single files with better ones keeps the game working as long as the layout in ART_BRIEF.md and theme.json is kept.

Smasher rework (2026-10-23, branch feature/fantasyOption; the smasher is the 'ogre' of the fantasy set): the laser, aiming, fuel, the double first step and the barrel/beam art are gone. Rules now: a smasher MUST move (no other way to use its power) 1 hex (a step) or 2 hexes (a jump over everything except the sun; `flyDist` like the astronaut), any direction; it cannot land on own pieces, shields or Home Planets (so it cannot win); an own free shield may be entered. When it lands, every ENEMY astronaut, smasher and drone on the six neighbouring hexes is destroyed (`smashList(p, x, y)`; a piece under a shield is safe, shields and Home Planets are never destroyed), and an enemy on the landing hex is captured as before. `legal()` gives such a move the kind `smash` (with `kv` = summed `VICTIM` value of everything it kills, used for move ordering and the quiescence search); a move that kills nothing is `walk` (1 hex) or `jump` (2 hexes). Landing on a fuel fire leaves the fire alone. The smasher needs no fuel (`fuelCap` = 0, no flames next to it, no refuel at the sun, no feeding; only the drone can feed an astronaut). Evaluation: `EV.smasher` = 220 (it was 110 until 2026-10-25; AI_FINDINGS.md has the duel test: 220 beat 110 by 22 : 7). UI: legal landings that destroy something are red (`KCOL.smash`), and while a smasher is dragged over a landing hex the pieces that would die are marked. Balance check (24 AI-vs-AI games, 0.3 s per move, colours swapped): Blue 15 wins, Red 6, 3 draws (repetition), 72 plies on average; the smasher made 12 % of all moves (the old laser smasher: 6 %, one shot in 6 games), 50 of its 206 moves were smashes (about 2 per game), most of the rest were positioning jumps. Blue's lead may be the first-move advantage or the smasher (not separated yet).
Smasher smoke (2026-10-23): when a smasher lands, `animate()` adds a `smoke` fx (`{type:'smoke', x, y, t0, ms: SMOKE_MS}`) on each of the six neighbouring hexes at the moment it arrives; they are drawn from the grey frames 3 and 4 of the explosion sheet, growing and fading. While a smasher is dragged over a landing hex, the same frames are drawn as small drifting puffs over the six neighbours (end of `drawField`), plus the red marks on the pieces that would die.
Ranges and the smasher (2026-10-23): `rangeBoundary()` adds, for a smasher, all hexes around each of its landing hexes (its destruction fields, so up to 3 hexes from the smasher) to its colour's region; `smash` is one of the `RANGE_KINDS`.
AI and the smasher (2026-10-23): `evaluate()` has two optional terms, both OFF (`EV.threat = 0`, `EV.spread = 0`): `threat` adds a fraction of the best smash value (`kv`) that each smasher could reach from where it stands, `spread` penalises pairs of adjacent own pieces while the enemy has a smasher. Self-play (0.3 s per move, colours swapped, A = new weights, B = current weights): threat .25: 9 : 14 (23 games); spread 8: 14 : 9 (24 games) and 19 : 27 (48 games, 2 draws); both: 9 : 15 (24 games). With identical weights and no smashers the same harness gave 5 : 13, so differences of about 5 games per 24 are noise. Result: no evidence that either term helps, so they stay off. Colours are balanced with the smasher (Blue 71 wins, Red 66 over 118 decided games), the AI makes 13 to 15 % of its moves with the smasher (about 3 smashes per game), and the smasher reduces draws by repetition (4 of 22 games without it, 2 of 164 with it). Harness: `NOSMASHER=1` env var removes the smashers in `game.js`.


Gorilla smasher (2026-10-25, branch feature/fantasyOption; SPACE theme only, the fantasy theme keeps its ogre): the smasher is drawn from `art/GorillaSprites.png` (590 x 370, transparent; row 0 Blue,
row 1 Red; each row = front, three-quarter view (faces RIGHT, mirrored for left moves), back view). It replaced the old single sprite `art/AstroRoverBlue/Red.png` of the space set (deleted, see the end of this file).
`ART.gorilla` exists only in the space theme (`loadAllArt()` loads it there and deletes it in the fantasy theme); the fantasy theme draws its ogre from
`art/fantasy/AstroSmasherBlue/Red.png` with the old single-picture branch of `drawPiece` and, being one picture, has no turning animation (`buildAnim` turns only when `ART.gorilla` exists). Frame rectangles are in
`GORILLA` (each cut to its own bounding box, so the bottom of a frame is the feet line); the front frame is drawn 76 px tall (scale `gk = 76 * s / 162`, all frames the
same scale). Animation (`buildAnim`, the smasher/drone branch): the gorilla TURNS first (180 degrees = back view when it moves up the screen, 45 = three-quarter when it moves
down, 90 = three-quarter when it moves sideways; `TURN` = 75 ms per 45 degrees like the astronaut), then moves (1 hex: slide; 2 hexes: lifted jump), and TURNS BACK to face
the viewer after landing. `tArrive` is the moment of landing, so the smash and the smoke still happen on arrival, before the turn back. The animation angle is mapped to a
frame by `[0, 1, 1, 2, 2][round(ang / 45)]` (front, three-quarter, back); only three views exist, so 45 and 90 degrees share the three-quarter frame. TUTORIAL.html and
ART_SHEET.html got the same gorilla (front view at rest).

Smasher, art cleanup and calmer fantasy tiles (2026-10-25, branch feature/fantasyOption):
- The piece formerly called the ROVER is now the SMASHER everywhere: engine type `'smasher'`, `EV.smasher`, `setupEls.smasher` (checkbox `#cSmasher`), messages, tutorial,
  art sheet, README, ART_BRIEF.md, this file and AI_FINDINGS.md (older sections that say "smasher" for the time before the rename describe the old rover with its laser and fuel).
  Not renamed on purpose: `models/` (the printable STL is still `rover.stl`, a rover with a laser barrel, now out of date) and `tools/fantasy_extract/ex2.py` (the source cut names).
- The Smasher picture depends on the theme: the gorilla (`art/GorillaSprites.png`, drawn by `drawPiece`, animated by `buildAnim`) in the SPACE theme, the ogre
  (`art/fantasy/AstroSmasherBlue/Red.png`, 220 x 184, the old single sprite: renamed from `AstroRoverBlue/Red.png` on 2026-10-25) in the FANTASY theme. TUTORIAL.html and
  ART_SHEET.html do the same.
- Removed picture files (all were tracked in git, get them back from the history if needed): in `art/` the old rover `AstroRoverBlue/Red.png`, and in `art/` and `art/fantasy/` the
  laser pictures `AstroBarrelArmed/Empty.png` and `AstroBeam.png` (8 files). The code that drew them, their lines in ART_SHEET.html and the steps in
  `tools/fantasy_extract/build_fantasy.py` that built the barrels and the beam are removed too. (First all 10 were deleted, including the fantasy ogre; the ogre pictures
  were restored the same day and renamed.)
- Fantasy ground hexes: `art/fantasy/AstroHexes.png` (ground frames 0..14 only; the washes and the outline are untouched) and `art/fantasy/AstroTiles.png` were processed once with
  PIL (Gaussian blur 2.2 px, contrast x 0.35 towards each tile's mean colour, saturation x 0.5, alpha unchanged) so that the playing pieces stand out. The processing script was
  `calm.py` in the session scratchpad (arguments: blur contrast saturation, always starting again from the original); the originals are in git (`git show HEAD:art/fantasy/AstroHexes.png`).
  If the tiles are regenerated by `build_fantasy.py`, the calming step has to be applied again.
