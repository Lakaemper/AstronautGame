# AstronautGame

A chess-like strategy game for two on a hex board, featuring the little astronaut. Open `index.html` in Chrome or Edge
(keep the `art/` folder next to it). Blue plays from the bottom, Red from the top; by default you play Red against the AI.

**Goal:** walk an astronaut onto the enemy Core. Rovers, drones and shields can never win.

**Pieces** (each side starts with 4 astronauts, a rover, a drone, a shield and its Core):

- **Astronaut:** fuel is range. It reaches every hex within fuel + 1 steps. One step is free, a longer move flies over
  everything and costs steps - 1 fuel, and may capture where it lands (but never lands on a Core). It refuels next to the
  sun, and by taking the fuel pack of a neighbouring rover or drone.
- **Rover:** 1-2 hexes along a line. Its laser destroys the first astronaut, drone or rover in line (even your own);
  aiming and firing are separate moves.
- **Drone:** up to 3 hexes along a line. It pushes enemies one hex away; pushed off the board or into a piece = captured.
- **Shield** (glass dome): moves one hex, also onto occupied hexes (not onto a Core). Whatever is under it is fully
  protected but cannot move, until the shield moves away. Your own pieces may move under your own shield. It cannot be
  captured, pushed or landed on, and lasers stop at it. Covering an enemy piece holds it, but that side breaks the shield
  after two of its turns (a cracked, more transparent dome after the first); a shield that has moved away heals on the
  next turn.

Full rules, code map and design history: see `NOTES.md`.
