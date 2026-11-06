# Opening catalog for Astro Game

100 typical, good openings, **four moves for each side** (8 plies), produced by the AI playing both sides with a deeper search than the normal game
(branch `deeptest`, 2026-11-06; generator `JS/tools/openings_phase.js`). Blue (bottom) moves first, Red (top) answers. The lines are *typical computer play*, not proven best play:
no opening is proven to win (see `findings.md`). The number in front of each line is the **score after the 8 plies** from Blue's view, searched 5 plies deeper
(100 = about one astronaut; positive = good for Blue; odd search depths tilt a little to the positive side, so only compare the numbers with each other).

## Notation

* **Squares:** files **a-i** from left to right, ranks **1-9** from bottom to top. Blue's Home Planet stands on **e1**, Red's on **e9**; the central fire is on **e5**.
  Blue's back row is rank 1 (astronauts b1 d1 f1 h1, drone c1, smasher g1, Home Planet e1, shield e3); Red's back row is rank 9 (b9 d9 f9 h9, drone c9, smasher g9, shield e7).
  Ranks 1 and 9 have the files b-h (seven hexes; the corner hexes are cut off), ranks 3, 5, 7 have a-i (nine hexes), ranks 2, 4, 6, 8 have a-h (eight hexes, shifted half a hex to the right).
* **Pieces:** **A** astronaut, **S** smasher, **D** drone, **H** shield (dome), **C** Home Planet.
* **Moves:** `Ab1-b2` step of one hex; `Ad2~e4` jetpack jump (2 or more hexes, costs fuel); `Axb3` capture; `Sg1*g3` smasher landing (smash); `Dc1>c4` drone push;
  `Ae4+` refuel at the central fire (the astronaut stays put); `Ab1=c1` take fuel from the drone on c1 (the astronaut stays put). The shield and Home Planet use `-`.
* A line reads `1. <Blue> <Red>  2. ...`; here lines are written with ";" between full moves.

## The families

| Family | Typical first move | Idea |
|---|---|---|
| Centre Step | `Ad1-d2`, `Af1-e2`, `Ad1-c2` | bring an astronaut towards the centre, then jet to the fire (Ae4+ refuels there) |
| Flank Step | `Ah1-g2`, `Ah1-h2` | right-side advance, mostly paired with a drone feed |
| Right-Centre Step | `Af1-f2` | same, from the right |
| Wing Step | `Ab1-a2`, `Ab1-b2` | astronaut walks up the left edge while the others refuel |
| Drone Feed | `Ab1=c1`, `Ad1=c1` | fuel first: the astronaut next to the drone takes its charge, the astronaut behind takes the fire route later |
| Smasher Leap | `Sg1~f3`, `Sg1~g3` | smasher out on move 1 (weaker: the search rates these lowest) |

Red's usual answers: take the drone's fuel too (`Ab9=c9` / `Ad9=c9`), step an astronaut up (`Ab9-b8`, `Ad9-d8`, `Af9-e8`), then jump to a6-e6 or send the drone out (`Dc9-d6`).

## The 100 openings (sorted by family, best first)

### Centre Step

1. `1. Ad1-d2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ad2~e4 Ab8~a6 ; 4. Ae4+ Dc9-d6`  (+161)
2. `1. Af1-e2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ae2-f3 Dc9-d6 ; 4. Ab1-a2 Ab8~a6`  (+121)
7. `1. Af1-e2 Ad9=c9 ; 2. Ad1=c1 Ad9-d8 ; 3. Ae2~e4 Dc9-a6 ; 4. Ad1-d2 Da6-d6`  (+92)
8. `1. Af1-e2 Ad9=c9 ; 2. Ab1=c1 Ad9-d8 ; 3. Ae2~e4 Dc9-a6 ; 4. Ad1-d2 Da6-d6`  (+92)
10. `1. Ad1-d2 Ab9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ad2~d4 Dc9-d6 ; 4. Ab1-a2 Dd6-d7`  (+90)
11. `1. Af1-e2 Ab9=c9 ; 2. Ad1=c1 Ah9-g8 ; 3. Ae2~e4 Dc9-a6 ; 4. Ad1-d2 Da6-e6`  (+90)
12. `1. Af1-e2 Af9-e8 ; 2. Ad1=c1 Ab9=c9 ; 3. Ae2~e4 Dc9-d6 ; 4. Ab1-a2 Dd6-e6`  (+90)
14. `1. Ad1-d2 Ad9=c9 ; 2. Ab1=c1 Ad9-d8 ; 3. Ad2~e4 Dc9-d6 ; 4. Ab1-a2 Dd6-c6`  (+86)
16. `1. Af1-e2 Ab9-b8 ; 2. Ad1=c1 Ad9=c9 ; 3. Ae2~e4 Ab8-b7 ; 4. Ae4+ Ab7-a6`  (+85)
18. `1. Ad1-d2 Ab9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ad2~d4 Dc9-d6 ; 4. Ab1-a2 Dd6-c6`  (+83)
21. `1. Ad1-d2 Ad9=c9 ; 2. Ab1=c1 Ad9-d8 ; 3. Ad2~d4 Dc9-d6 ; 4. Ab1-a2 Ad8-d7`  (+75)
24. `1. Ad1-c2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ac2-d3 Dc9-d6 ; 4. Ab1-a2 Ab8-c7`  (+71)
27. `1. Ad1-d2 Ad9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ad2~e4 Ab8-b7 ; 4. Ae4+ Ab7-b6`  (+68)
28. `1. Ad1-d2 Ab9-b8 ; 2. Ab1=c1 Ad9=c9 ; 3. Ad2~e4 Ab8-b7 ; 4. Ae4+ Ab7-b6`  (+68)
30. `1. Af1-e2 Ad9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Ab2=c1 Ab8-c7 ; 4. Ab2-c3 Ac7-b6`  (+67)
35. `1. Af1-e2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ae2~e4 Ab8-b7 ; 4. Ae4+ Ah9-g8`  (+61)
41. `1. Ad1-d2 Ah9-g8 ; 2. Ab1=c1 Ad9=c9 ; 3. Ad2~d4 Ag8-g7 ; 4. Ad4+ Ag7-g6`  (+57)
42. `1. Ad1-c2 Ab9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Ah1-g2 Ad9-d8 ; 4. Ac2=c1 Ab8-c7`  (+55)
44. `1. Ad1-d2 Ab9-b8 ; 2. Ab1-b2 Ab8=c9 ; 3. Ab2=c1 Ab8-c7 ; 4. Ad2~e4 Ad9-d8`  (+55)
48. `1. Af1-e2 Ab9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ae2-f3 Dc9-a6 ; 4. Ad1-d2 Ae8-f7`  (+55)
50. `1. Af1-e2 Ad9=c9 ; 2. Ab1=c1 Ad9-d8 ; 3. Ae2-f3 Ad8~e6 ; 4. Af3-e4 Ah9-g8`  (+54)
51. `1. Af1-e2 Ad9=c9 ; 2. Ad1=c1 Ad9-d8 ; 3. Ae2-f3 Ad8~e6 ; 4. Af3-e4 Af9-e8`  (+54)
52. `1. Ad1-c2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Af1-e2 Ab8-c7 ; 4. Ab1-b2 Ad9-d8`  (+54)
53. `1. Ad1-c2 Ab9=c9 ; 2. Ac2=c1 Af9-e8 ; 3. Ac2-c3 Ab9-b8 ; 4. Ab1-b2 Ab8-c7`  (+53)
54. `1. Ad1-c2 Ab9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ac2-c3 Ab9-b8 ; 4. Ac3-b4 Ab8-c7`  (+53)
57. `1. Ad1-d2 Ab9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ad2-d3 Dc9-d6 ; 4. Ab1-a2 Ae8-f7`  (+53)
58. `1. Ad1-d2 Ad9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ad2-d3 Dc9-d6 ; 4. Ad3-c4 Ad9-d8`  (+52)
60. `1. Ad1-c2 Ad9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Ac2=c1 Ab8-c7 ; 4. Ac2-c3 Ac7-b6`  (+50)
63. `1. Ad1-c2 Ab9=c9 ; 2. Ac2=c1 Ab9-b8 ; 3. Ac2-d3 Ab8-c7 ; 4. Af1-e2 Af9-e8`  (+48)
75. `1. Ad1-c2 Ad9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ac2-c3 Ag8-h7 ; 4. Ac3-b4 Ad9-c8`  (+38)
77. `1. Ad1-d2 Ah9-g8 ; 2. Af1-e2 Ad9=c9 ; 3. Ab1=c1 Ag8-h7 ; 4. Ad2~e4 Ah7-g6`  (+38)
86. `1. Ad1-c2 Ad9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ac2-c3 Ab8-c7 ; 4. Ac3-b4 Ac7-b6`  (+35)
99. `1. Af1-e2 Ad9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ae2-f3 Ae8-f7 ; 4. Af3-e4 Af7-e6`  (+26)

### Flank Step

3. `1. Ah1-g2 Ad9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ag2-g3 Ab8~a6 ; 4. Ad1-c2 Ad9-d8`  (+112)
13. `1. Ah1-h2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ah2-h3 Ab8~a6 ; 4. Ah3~h5 Aa6-b5`  (+89)
22. `1. Ah1-g2 Ad9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ag2-g3 Ab8~b6 ; 4. Ab1-b2 Ah9-g8`  (+74)
23. `1. Ah1-g2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ag2-h3 Ab8~b6 ; 4. Ab1-b2 Af9-e8`  (+74)
25. `1. Ah1-h2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ah2-i3 Ab8~a6 ; 4. Ad1-d2 Aa6-b5`  (+70)
62. `1. Ah1-g2 Ab9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ag2-g3 Ag8-g7 ; 4. Af1-e2 Ab9-b8`  (+48)
64. `1. Ah1-g2 Ad9=c9 ; 2. Ad1=c1 Ah9-g8 ; 3. Ag2-g3 Ag8-g7 ; 4. Af1-e2 Ab9-b8`  (+48)
65. `1. Ah1-h2 Ad9=c9 ; 2. Ab1=c1 Ad9-d8 ; 3. Ah2-h3 Ad8~e6 ; 4. Af1-e2 Ae6+`  (+48)
72. `1. Ah1-h2 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ah2-i3 Ab8-b7 ; 4. Af1-e2 Ad9-d8`  (+39)
76. `1. Ah1-g2 Ab9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ag2-h3 Ag8-g7 ; 4. Ad1-d2 Ag7-f6`  (+38)
79. `1. Ah1-h2 Ad9=c9 ; 2. Ab1=c1 Ah9-g8 ; 3. Ah2-h3 Ag8-g7 ; 4. Af1-e2 Ag7-f6`  (+37)
82. `1. Ah1-g2 Ab9=c9 ; 2. Ad1=c1 Ah9-g8 ; 3. Ag2-h3 Ag8-g7 ; 4. Af1-e2 Ag7-f6`  (+37)
92. `1. Ah1-h2 Ah9-g8 ; 2. Ad1=c1 Ad9=c9 ; 3. Ah2-h3 Ag8-g7 ; 4. Ad1-d2 Ag7-f6`  (+32)
94. `1. Ah1-h2 Ad9=c9 ; 2. Ad1=c1 Ad9-d8 ; 3. Ah2-h3 Ad8-d7 ; 4. Ad1-d2 Af9-f8`  (+31)
96. `1. Ah1-g2 Ad9=c9 ; 2. Ad1=c1 Ah9-g8 ; 3. Ag2-g3 Ag8-g7 ; 4. Ad1-d2 Af9-e8`  (+30)
100. `1. Ah1-h2 Ad9=c9 ; 2. Ad1=c1 Ah9-g8 ; 3. Ah2-i3 Ag8-g7 ; 4. Ad1-d2 Ag7-f6`  (+25)

### Right-Centre Step

4. `1. Af1-f2 Ab9-b8 ; 2. Ab1=c1 Ad9=c9 ; 3. Af2-g3 Ab8~a6 ; 4. Ab1-b2 Af9-e8`  (+97)
6. `1. Af1-f2 Af9-e8 ; 2. Ad1=c1 Ab9-b8 ; 3. Af2-g3 Ab8=c9 ; 4. Ah1-g2 Ab8~a6`  (+93)
20. `1. Af1-f2 Ab9=c9 ; 2. Af2-f3 Dc9-a6 ; 3. Ad1-d2 Da6-d6 ; 4. Ab1-a2 Ad9-d8`  (+76)
47. `1. Af1-f2 Af9-e8 ; 2. Ah1-g2 Ah9-g8 ; 3. Af2-f3 Ab9-b8 ; 4. Af3-e4 Ab8=c9`  (+55)
49. `1. Af1-f2 Ah9-g8 ; 2. Ab1=c1 Af9-e8 ; 3. Af2-f3 Ab9-b8 ; 4. Af3-e4 Ad9=c9`  (+55)
69. `1. Af1-f2 Ad9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Af2-g3 Ab8-c7 ; 4. Ad1-c2 Ac7-b6`  (+43)
89. `1. Af1-f2 Ab9-b8 ; 2. Ab1=c1 Af9-e8 ; 3. Af2-g3 Ad9=c9 ; 4. Ab1-b2 Ab8-c7`  (+33)

### Wing Step

5. `1. Ab1-a2 Af9-e8 ; 2. Ad1=c1 Ab9=c9 ; 3. Aa2-b3 Ab9-b8 ; 4. Ad1-d2 Ab8~a6`  (+95)
29. `1. Ab1-a2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Aa2-b3 Ab8-b7 ; 4. Ad1-c2 Ad9-d8`  (+68)
39. `1. Ab1-b2 Ab9=c9 ; 2. Ab2=c1 Af9-e8 ; 3. Ab2-c3 Ab9-b8 ; 4. Af1-e2 Ab8-b7`  (+57)
40. `1. Ab1-b2 Ad9=c9 ; 2. Ad1=c1 Af9-e8 ; 3. Ab2-c3 Ad9-c8 ; 4. Ac3-b4 Ac8-c7`  (+57)
43. `1. Ab1-a2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Af1-e2 Ab8-c7 ; 4. Ad1-c2 Ad9-d8`  (+55)
45. `1. Ab1-a2 Ab9=c9 ; 2. Ad1=c1 Ad9-d8 ; 3. Aa2-b3 Ab9-b8 ; 4. Ah1-g2 Ab8-c7`  (+55)
46. `1. Ab1-a2 Ad9-d8 ; 2. Ad1=c1 Ab9=c9 ; 3. Aa2-b3 Ab9-b8 ; 4. Ab3-a4 Ab8-b7`  (+55)
55. `1. Ab1-b2 Af9-e8 ; 2. Ad1=c1 Ab9=c9 ; 3. Ab2-c3 Ab9-b8 ; 4. Ac3-b4 Ab8-c7`  (+53)
56. `1. Ab1-b2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ab2-b3 Ab8-c7 ; 4. Ab3-b4 Ah9-g8`  (+53)
59. `1. Ab1-a2 Ah9-g8 ; 2. Ad1=c1 Ab9=c9 ; 3. Aa2-b3 Ab9-b8 ; 4. Ab3-a4 Ab8-b7`  (+50)
61. `1. Ab1-a2 Ab9=c9 ; 2. Ad1=c1 Af9-e8 ; 3. Aa2-b3 Ab9-b8 ; 4. Ab3-a4 Ab8-c7`  (+48)
67. `1. Ab1-b2 Ad9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ab2-c3 Ab8-c7 ; 4. Ac3-b4 Ac7-c6`  (+44)
73. `1. Ab1-b2 Ab9-b8 ; 2. Ah1-g2 Ad9=c9 ; 3. Ad1=c1 Ab8-b7 ; 4. Ag2-g3 Ab7-b6`  (+39)
78. `1. Ab1-a2 Ad9=c9 ; 2. Ad1=c1 Ad9-d8 ; 3. Aa2~b4 Ad8-d7 ; 4. Af1-e2 Ad7-c6`  (+37)
81. `1. Ab1-b2 Ad9=c9 ; 2. Ab2=c1 Ah9-g8 ; 3. Ab2-b3 Ag8-h7 ; 4. Ah1-g2 Ad9-c8`  (+37)
83. `1. Ab1-b2 Ab9=c9 ; 2. Ab2=c1 Ad9-d8 ; 3. Ab2-b3 Ab9-b8 ; 4. Ah1-h2 Ab8-b7`  (+36)
84. `1. Ab1-a2 Ab9=c9 ; 2. Ad1=c1 Ab9-b8 ; 3. Ad1-d2 Ab8-c7 ; 4. Ad2-d3 Ad9-d8`  (+35)
88. `1. Ab1-b2 Ad9=c9 ; 2. Ab2=c1 Ad9-d8 ; 3. Ab2-b3 Ad8-d7 ; 4. Ah1-g2 Ad7-d6`  (+33)
95. `1. Ab1-b2 Ab9=c9 ; 2. Ab2=c1 Ab9-b8 ; 3. Ab2~b4 Ab8-c7 ; 4. Ad1-c2 Ad9-d8`  (+31)

### Drone Feed

9. `1. Ab1=c1 Ab9=c9 ; 2. Ad1-d2 Ad9-d8 ; 3. Ad2~e4 Dc9-d6 ; 4. Ab1-a2 Dd6-d7`  (+90)
15. `1. Ab1=c1 Ad9=c9 ; 2. Af1-e2 Ad9-d8 ; 3. Ae2-f3 Ad8-d7 ; 4. Af3-e4 Dc9-a6`  (+85)
17. `1. Ab1=c1 Ab9=c9 ; 2. Ad1-d2 Ab9-b8 ; 3. Ad2~e4 Dc9-d6 ; 4. Ab1-a2 Ab8-b7`  (+84)
19. `1. Ad1=c1 Ad9=c9 ; 2. Ab1-b2 Ad9-d8 ; 3. Ab2-c3 Ad8-d7 ; 4. Ac3-b4 Ad7-d6`  (+77)
26. `1. Ab1=c1 Ab9=c9 ; 2. Ad1-d2 Ah9-g8 ; 3. Ad2~d4 Ag8-h7 ; 4. Ad4+ Ah7~h5`  (+70)
31. `1. Ab1=c1 Ad9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Ab2-b3 Ab8-c7 ; 4. Af1-e2 Ac7-b6`  (+65)
32. `1. Ad1=c1 Ab9=c9 ; 2. Af1-e2 Ah9-g8 ; 3. Ae2~e4 Ag8-h7 ; 4. Ae4+ Ah7-g6`  (+63)
33. `1. Ad1=c1 Ad9=c9 ; 2. Ah1-g2 Ad9-d8 ; 3. Ag2-g3 Ad8-d7 ; 4. Ab1-b2 Ab9-b8`  (+62)
34. `1. Ad1=c1 Ad9=c9 ; 2. Ab1-b2 Af9-e8 ; 3. Ab2-c3 Ad9-c8 ; 4. Ac3-b4 Ac8-d7`  (+62)
36. `1. Ad1=c1 Ad9=c9 ; 2. Ab1-b2 Ad9-d8 ; 3. Ad1-d2 Ad8~e6 ; 4. Ab2-c3 Ae6+`  (+61)
38. `1. Ad1=c1 Ab9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Af1-e2 Ab8-c7 ; 4. Ab2-c3 Ad9-d8`  (+59)
66. `1. Ad1=c1 Ab9=c9 ; 2. Ad1-d2 Ab9-b8 ; 3. Ad2~e4 Ab8~b6 ; 4. Ae4+ Ad9-d8`  (+45)
68. `1. Ad1=c1 Ab9=c9 ; 2. Ab1-b2 Ah9-g8 ; 3. Ab2-c3 Ag8-g7 ; 4. Ac3-b4 Ab9-b8`  (+44)
71. `1. Ab1=c1 Ad9=c9 ; 2. Ab1-b2 Ad9-d8 ; 3. Ah1-g2 Ad8~e6 ; 4. Ab2-c3 Ae6+`  (+41)
74. `1. Ad1=c1 Ab9=c9 ; 2. Ad1-d2 Ad9-d8 ; 3. Ad2~e4 Af9-e8 ; 4. Ae4+ Ad8-d7`  (+38)
80. `1. Ab1=c1 Ad9=c9 ; 2. Ah1-g2 Ah9-g8 ; 3. Ag2-h3 Ag8-g7 ; 4. Af1-e2 Ag7-f6`  (+37)
85. `1. Ab1=c1 Ab9=c9 ; 2. Ab1-b2 Ab9-b8 ; 3. Ab2-c3 Ab8-c7 ; 4. Ah1-g2 Ad9-d8`  (+35)
91. `1. Ad1=c1 Ab9=c9 ; 2. Ad1-d2 Ab9-b8 ; 3. Ad2~e4 Ab8-b7 ; 4. Ae4+ Ab7~b5`  (+32)
93. `1. Ad1=c1 Ab9=c9 ; 2. Ad1-d2 Ab9-b8 ; 3. Ad2~e4 Ab8~a6 ; 4. Ae4+ Aa6-b5`  (+32)
98. `1. Ab1=c1 Ad9=c9 ; 2. Af1-e2 Af9-e8 ; 3. Ae2-f3 Ae8-f7 ; 4. Af3-e4 Af7-e6`  (+26)

### Smasher Leap

37. `1. Sg1~f3 Ab9=c9 ; 2. Ab1=c1 Af9-e8 ; 3. Ab1-b2 Ae8~d6 ; 4. Dc1-d4 Ab9-b8`  (+59)
70. `1. Sg1~f3 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Af1-e2 Ab8-b7 ; 4. Ab1-b2 Ah9-g8`  (+41)
87. `1. Sg1~g3 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ad1-d2 Ab8-c7 ; 4. Ab1-b2 Af9-e8`  (+34)
90. `1. Sg1~f3 Ad9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Ad1-d2 Ab8-c7 ; 4. Ab1-b2 Ad9-d8`  (+33)
97. `1. Sg1~f3 Ab9=c9 ; 2. Ab1=c1 Ab9-b8 ; 3. Af1-e2 Ab8-c7 ; 4. Ab1-b2 Ah9-g8`  (+28)
