# AstronautGame

A chess-like strategy game for two on a hex board, featuring the little astronaut. Open `index.html` in Chrome or Edge
(keep the `art/` folder next to it). Blue plays from the bottom, Red from the top; by default you play Red against the AI.

**Goal:** walk an astronaut onto the enemy Core. Smashers, drones and shields can never win.

**Pieces** (each side starts with 4 astronauts, a smasher, a drone, a shield and its Core):

- **Astronaut:** fuel is range. It reaches every hex within fuel + 1 steps. One step is free, a longer move flies over
  everything and costs steps - 1 fuel, and may capture where it lands (but never lands on a Core). It refuels next to the
  sun, and by taking the fuel pack of a neighbouring smasher or drone.
- **Smasher** (the gorilla; an ogre in the fantasy theme): it has to move, 1 hex (a step) or 2 hexes (a jump over everything
  except the central fire). Wherever it lands, every enemy astronaut, smasher and drone on the six hexes around it is destroyed
  (pieces under a shield are safe). It cannot land on own pieces, shields or Core, so it can never win.
- **Drone:** up to 3 hexes along a line. It pushes enemies one hex away; pushed off the board or into a piece = captured.
- **Shield** (glass dome): moves one hex, also onto occupied hexes (not onto a Core). Whatever is under it is fully
  protected but cannot move, until the shield moves away. Your own pieces may move under your own shield. It cannot be
  captured, pushed or landed on. Covering an enemy piece holds it, but that side breaks the shield
  after two of its turns (a cracked, more transparent dome after the first); a shield that has moved away heals on the
  next turn.

Full rules, code map and design history: see `NOTES.md`.
