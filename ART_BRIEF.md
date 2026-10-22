# Astro Game: artwork brief for ChatGPT

Paste PART 1 first (it sets the style for the whole chat), then work through PART 3 one asset at a time. PART 2 is the technical data to keep next to you. Attach the matching old image from the `art/` folder (or a screenshot of `ART_SHEET.html`) as a reference when you ask for an asset.

---

## PART 1: master prompt (paste this first)

> You are the artist for a small turn-based hex-board strategy game. I will ask you for individual game sprites, one at a time. Rules for every image:
>
> 1. **Transparent background** (PNG with alpha). If you cannot make transparency, use a flat pure magenta (#FF00FF) background and nothing else in that colour, so I can remove it.
> 2. **One subject per image**, centred, nothing cropped, no text, no frame, no drop shadow on the ground (the game draws its own shadow), no border.
> 3. **Square or tall canvas, at least 1024 px** on the long side. I will scale it down to roughly 90 px on screen, so the design must **read clearly at 90 px**: a strong silhouette, bold shapes, few details, thick clean outlines.
> 4. **Viewpoint:** slightly from above (3/4 top-down), like a board-game miniature seen from the player's seat. Light comes from the **top left**. Keep this the same in every image.
> 5. **Two teams:** Blue (#2f8fe8) and Red (#e9475a). A team is shown only by its accent colour (clothes, trim, glow). Keep the shape identical for both teams, only the accent colour changes. Everything else uses the neutral palette below.
> 6. **Consistency matters more than detail.** Every piece must look like it belongs to the same set: the same line weight, the same level of detail, the same palette.
>
> STYLE (choose one and keep it): **[A] current space look**: "Der Kleine Astronaut" children's-book crayon and paper-cut style, thick black outline, flat colour with light pencil hatching, friendly but not babyish. **[B] fantasy ink-wash look**: serious East-Asian-inspired fantasy, soft watercolour washes with confident ink outlines, jade green, mist grey, blossom pink and gold as neutrals, moody but readable, not cartoonish.
>
> Reply to each request with the image only, plus one line saying what you changed if I ask for a revision.

Then say which style (A or B) you want. If you want fantasy, also paste the piece mapping in PART 3 (column "B").

---

## PART 2: technical data

### The board and the sizes you must respect
- The board is 9 hexes wide and 9 high, pointy-top hexes, **one hex is about 94 x 108 px** on screen. Pieces stand on a hex and are about 80 to 90 px tall. The whole image library is drawn at that size (some files at twice that size, see the table).
- Pieces are drawn **with their feet or base at the bottom of the frame**, horizontally centred, because the game places them from that point.
- Colours used by the game: Blue #2f8fe8, Red #e9475a, neutral grey #6b6b6b, ground greens #1f5c3e #2c7451 #256848, ink outline #111111, paper #f6efdc, fire gold #ffd24d.

### The pieces and what they do (so the art can say it)
| Piece | Rules in one line | Fantasy version [B] |
|---|---|---|
| Astronaut (4 per team) | Walks one hex or jumps up to 3 hexes using fuel; steps onto the enemy Home Planet to win. Fuel is shown as little flames beside the feet. | Wizard or sage, mana instead of fuel |
| Rover (1) | Slow vehicle with a laser barrel on top that turns and fires along a line. | Stone guardian or golem with a gaze beam |
| Drone (1) | Flies up to 3 hexes and pushes an enemy piece one hex away. | Dragon |
| Shield (1) | A glass dome that covers one piece, cracks in 2 stages, then shatters. | Ward bubble or ice-crystal prison |
| Home Planet (1) | The target. Can be moved sideways one hex. | Floating pagoda or sky-keep |
| Fuel station | The big fire in the middle of the board. | Well of embers / brazier |
| One-time fuel fires | Small flames on the middle row. | Mana crystals or wisps |

### File list: exact sizes, frames and anchors
All sizes are in pixels. "Frame" means a rectangle cut out of a bigger sheet by position, so **the sheet layout must be kept exactly**. If you give me single frames instead, I will assemble the sheets for you.

| File | Whole image | Frames inside | What it is and where the anchor is |
|---|---|---|---|
| AstroAnimsheet.png (Blue), AstroAnimsheetRed.png | 748 x 160 | Front [205,0,108,160], 1 [105,0,98,160], 2 [1,0,103,160], 3 [314,0,88,160], 4 [406,0,105,160], wave [514,0,116,160] (x, y, width, height) | Astronaut in 5 turning poses: frame 0 faces the viewer, 1 to 3 turn towards the side, 4 shows the back. The east-facing poses are the same frames mirrored by the game. "Wave" is the pose while the piece is held in the air. Feet at the bottom. Drawn about 84 px tall. A jetpack is on the back. |
| AstroShipBlue.png, AstroShipRed.png | 143 x 160 each | 1 frame | The drone (a rocket in the space version). Base at the bottom, about 76 px tall on screen. |
| AstroFire.png | 179 x 50 | 4 flames: [12,0,25,50] [51,0,26,50] [94,0,29,50] [144,0,22,50] | Four flicker shapes of one flame, **hanging downwards** from a jetpack (the game flips them upright for the fires). All four must have similar size and area. |
| AstroExplosion.png | 998 x 200 | [14,0,299,200] [324,0,184,200] [520,0,179,200] [709,0,146,200] [875,0,87,200] [967,0,18,200] | Six frames of a burst: starburst, smoke puff, drifting smoke, fading smoke, tiny, almost gone. Left to right in time. |
| AstroBG.png | 384 x 256 | sun [2,3,115,112], Neptune [217,96,73,74], Mars [13,114,62,62], plus 15 decorations (planets, stars, rocks) | Neptune is the **Blue Home Planet** and Mars the **Red Home Planet**, drawn about 80 px high. The rest are stickers scattered behind the board. |
| AstroRoverBlue.png, AstroRoverRed.png | 220 x 184 (= 110 x 92 game px at 2x) | 1 frame | Rover body **without** the laser barrel. Ground contact point is at x = 104, y = 164 (the wheel bottoms). Facing right. |
| AstroBarrelArmed.png, AstroBarrelEmpty.png | 80 x 40 | 1 frame | Laser barrel pointing **right (east)**; the pivot is at x = 4, y = 20 and the barrel is about 76 px long. The game rotates it to any of 6 directions. Armed has a red band and a gold lens, Empty is grey. |
| AstroShield.png | 1248 x 208 | 6 frames of 208 x 208 in a row: Blue intact, Blue cracked 1, Blue cracked 2, Red intact, Red cracked 1, Red cracked 2 | A circular glass dome, 104 px across inside the frame, team-coloured rim. **Opacity is baked in**: intact about 70 %, cracked about 42 % (the cracks themselves nearly opaque). |
| AstroBase.png | 480 x 60 | 3 frames of 160 x 60: Blue, Red, neutral | The flat oval base under every piece, 136 x 40 inside its frame, team coloured. |
| AstroShadow.png | 160 x 60 | 1 | Soft dark oval shadow, centred slightly lower right. |
| AstroHotRing.png | 200 x 80 | 1 | A red warning ring (ellipse outline) shown around an overcharged astronaut. |
| AstroBang.png | 80 x 100 | 1 | A red "!" with a white outline. |
| AstroZzz.png | 148 x 144 | 1 | The letters "z z Z" climbing up and to the right, white with black outline (the "stunned" mark). |
| AstroGlow.png | 256 x 256 | 1 | Soft round warm glow, bright centre fading to transparent. Tinted by the game. |
| AstroTiles.png | 500 x 100 | 5 tiles of 100 x 100 | Five ground textures, semi-transparent, drawn on a green hex: crater, rock slabs, dusty plain, pebbles, cracked ground. Must be seamless in the middle (the edges are cut to the hex). |
| AstroHexes.png | 960 x 880 | 19 frames of 192 x 220, 5 per row | **I generate this one from the tiles**, you do not need to make it. |
| AstroSky.png | 858 x 772 | 1 | The board background: dark with a soft centre glow. |
| AstroBeam.png | 1024 x 80 | 2 frames of 512 x 80 | A horizontal laser bar: a round left end (x 2 to 28), a middle that can be stretched (28 to 484), a round right end (484 to 510). Frame 1 is red outside, frame 2 blue outside, white core. |
| AstroBanner.png | 1176 x 1188 | 3 frames of 588 x 396: "Blue wins!", "Red wins!", "Draw!" | A banner board with big lettering shown over the board at the end. |

---

## PART 3: per-asset requests (paste one at a time)

Replace `[A or B]` with your chosen style. Attach the old image as a reference. Ask for Blue first, then say "Now the same, with the Red accent #e9475a".

1. **Astronaut, front pose.** "Create the astronaut sprite, pose 0: facing the viewer, standing, jetpack visible on the back. Blue accent #2f8fe8 on the helmet visor or robe trim. Fits a 108 x 160 portrait frame, feet at the very bottom. [A: white spacesuit, orange-red helmet visor] [B: robed sage with a pointed hat and a staff]. Style [A or B]."
2. **Astronaut turning poses.** "Same character as the last image, pose 1, 2 and 3: turning in three equal steps to face the viewer's left, then pose 4: seen from behind. Same height and feet position in every pose. Same style."
3. **Astronaut held pose.** "Same character, the 'wave' pose: arms up, as if lifted by the player. Same size."
4. **Drone.** "A small flying craft [A: rocket, arrowhead shape, red or blue; B: Eastern dragon] seen from above at a slight angle, 143 x 160 portrait, base at the bottom, Blue accent. Bold silhouette."
5. **Rover body.** "A slow six-wheeled vehicle [A: moon rover with solar panel, dome and antenna dish; B: stone guardian on wheels or a small golem cart] facing right, side view with slight top view, 110 x 92 proportion, wheels touching the ground at the bottom, Blue accent on the chassis. No laser barrel."
6. **Laser barrel.** "Just the laser barrel for that rover: a thin tube, pointing right, 80 x 40 px, pivot on the left end. Two versions: armed (red band, glowing gold lens) and empty (grey)."
7. **Shield, three stages.** "A transparent glass dome seen from above, circular, team-coloured rim, a white highlight on the upper left. Stage 1: intact. Stage 2: with a branching crack. Stage 3: with a second, bigger set of cracks. Keep the same size. Blue version, then Red."
8. **Home Planets / sky-keep.** "The Blue Home Planet [A: an ocean planet like Neptune; B: a floating pagoda keep with blue roofs] and the Red one [A: a red cratered planet like Mars; B: the same keep with red roofs]. Each fits an 80 x 80 px square when shrunk."
9. **Flame, four frames.** "One flame in four different flicker shapes, hanging downwards, each 25 to 30 px wide and 50 px tall, similar size and area, orange with a yellow core, on a transparent background."
10. **Explosion, six frames.** "A burst in six stages, left to right: bright starburst, round smoke puff, bigger drifting smoke, thin smoke, tiny remains, almost gone."
11. **Ground tiles.** "Five textures for a game board floor, each 100 x 100 px, semi-transparent, soft edges: crater, layered rock slabs, dusty plain with hatching, scattered pebbles, cracked ground. Muted green-grey, they sit on a darker green."
12. **Board background and extras.** "A dark, calm board background 858 x 772 with a soft light in the middle. Then a small set of decorations for behind the board: [A: planets, stars, rocks; B: floating islands, cherry-blossom branches, pagoda roofs, mist]."
13. **Marks.** "Three small marks: a red '!' with white outline, 'z z Z' in white with black outline climbing to the right, and a red warning ellipse ring."
14. **Win banners.** "A banner board in the style, three versions: 'Blue wins!' with Blue lettering, 'Red wins!' with Red lettering, 'Draw!' with grey lettering. 588 x 396 proportion."

---

## What to send back to me (Claude)

For each asset: single PNGs with transparent backgrounds, named like `astro_blue_pose0.png`, `astro_blue_pose1.png`, `shield_blue_stage2.png`, `flame_1.png` … Do not worry about exact sizes or sheets: I will crop, scale, align the anchors and assemble `art/*.png` exactly in the layout above. Also tell me which style (A or B) you used so I can adjust the tutorial and the colours of the board to match.
