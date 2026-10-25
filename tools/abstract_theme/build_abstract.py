"""Builds the ABSTRACT ("tournament") picture set into art/abstract/ with PIL only.

Flat geometric pieces, no textures: Blue = light blue, Red = deep rust, each with a contrasting outline; a neutral green-grey board with
a light orange refuel zone. Every file has the same name and (where the game cuts frames out of it with fixed rectangles) the same layout
as in art/ (see ART_BRIEF.md); the sheets that the game cuts with per-theme rectangles (astronaut, drone, planets, flames) are listed in
THEME_RECTS['abstract'] in index.html, TUTORIAL.html and ART_SHEET.html and in art/abstract/theme.json.
The hex shapes (frames of AstroHexes.png) are taken from art/AstroHexes.png, so run this from the repository root: python tools/abstract_theme/build_abstract.py
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'art', 'abstract')
os.makedirs(OUT, exist_ok=True)
SS = 4                                               # drawing is done 4x larger and scaled down, for smooth edges

LB, LB_LINE = (214, 233, 249), (22, 34, 46)          # Blue: light blue with a dark navy outline
RU, RU_LINE = (106, 36, 25), (242, 232, 218)         # Red: deep rust with a cream outline
SIDE = [(LB, LB_LINE), (RU, RU_LINE)]
AMBER, AMBER_LIGHT = (224, 162, 30), (247, 213, 106)
TILES = [(134, 143, 132), (128, 138, 126), (123, 132, 121)]     # slightly green grey, three tones (tint 0..2)
GRID = (103, 114, 99)
SKY = (42, 45, 43)
ORANGE = (255, 154, 60)
ALERT = (224, 64, 47)
FONT = next((p for p in (r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') if os.path.exists(p)), None)

def font(size):
    return ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()

def canvas(w, h, colour=(0, 0, 0, 0)):
    return Image.new('RGBA', (w * SS, h * SS), colour)

def done(im, w, h):
    return im.resize((w, h), Image.LANCZOS)

def disc(d, cx, cy, r, fill):
    d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=fill)

def poly(d, pts, fill):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

def thick_line(d, pts, width, fill):                  # a polyline with round joints
    P = [(x * SS, y * SS) for x, y in pts]
    d.line(P, fill=fill, width=int(width * SS), joint='curve')
    for x, y in P:
        d.ellipse([x - width * SS / 2, y - width * SS / 2, x + width * SS / 2, y + width * SS / 2], fill=fill)

def save(im, name):
    im.save(os.path.join(OUT, name))
    print('wrote', name, im.size)

# ------------------------------------------------------------------ astronaut: a helmet (disc + curved visor line), 6 identical frames of 168 x 168 (no turning)
def helmet(side):
    fill, line = SIDE[side]
    im = canvas(168, 168); d = ImageDraw.Draw(im)
    cx, cy, r, ow = 84, 92, 62, 9
    disc(d, cx, cy, r, line + (255,)); disc(d, cx, cy, r - ow, fill + (255,))
    curve = []                                         # quadratic curve from the left to the right end of the visor chord
    p0, p1, p2 = (cx - .866 * r, cy - .5 * r), (cx, cy + .3 * r), (cx + .866 * r, cy - .5 * r)
    for i in range(41):
        t = i / 40; curve.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    thick_line(d, curve, 8, line + (255,))
    g = done(im, 168, 168)
    return g if side == 0 else g.rotate(180)           # Red looks towards the other side of the board

for side, name in ((0, 'AstroAnimsheet.png'), (1, 'AstroAnimsheetRed.png')):
    sheet = Image.new('RGBA', (168 * 6, 168)); h = helmet(side)
    for i in range(6): sheet.paste(h, (168 * i, 0))
    save(sheet, name)

# ------------------------------------------------------------------ drone: a triangle pointing at the enemy, 168 x 168
def drone(side):
    fill, line = SIDE[side]
    im = canvas(168, 168); d = ImageDraw.Draw(im)
    def tri(inset):
        a = [(84, 22), (146, 138), (22, 138)]
        cx, cy = 84, 108
        return [(cx + (x - cx) * (1 - inset), cy + (y - cy) * (1 - inset)) for x, y in a]
    big = tri(0); poly(d, big, line + (255,))
    for x, y in big: disc(d, x, y, 0, line + (255,))
    poly(d, tri(.17), fill + (255,))
    disc(d, 84, 104, 11, line + (255,))
    g = done(im, 168, 168)
    return g if side == 0 else g.transpose(Image.FLIP_TOP_BOTTOM)
save(drone(0), 'AstroShipBlue.png'); save(drone(1), 'AstroShipRed.png')

# ------------------------------------------------------------------ smasher: a solid hexagon ringed by six dots, 220 x 184 (drawn with its centre at (104, 77))
def smasher(side):
    fill, line = SIDE[side]
    im = canvas(220, 184); d = ImageDraw.Draw(im)
    cx, cy = 104, 77
    def hexp(r): return [(cx + r * math.cos(math.radians(60 * i - 30)), cy + r * math.sin(math.radians(60 * i - 30))) for i in range(6)]
    poly(d, hexp(50), line + (255,))
    for x, y in hexp(50): disc(d, x, y, 4.5, line + (255,))
    poly(d, hexp(40), fill + (255,))
    for i in range(6):
        a = math.radians(60 * i); x, y = cx + 64 * math.cos(a), cy + 64 * math.sin(a)
        disc(d, x, y, 9, line + (255,)); disc(d, x, y, 6.2, fill + (255,))
    return done(im, 220, 184)
save(smasher(0), 'AstroSmasherBlue.png'); save(smasher(1), 'AstroSmasherRed.png')

# ------------------------------------------------------------------ Home Planets (AstroBG.png): a ring AND a disc in the side colour, 168 x 168 each; plus a transparent 'sticker' (the page has no scenery here)
def planet(side):                                    # a disc with a slanted elliptical ring (the ring passes behind the upper half of the disc)
    fill, line = SIDE[side]
    def ring_half(front):
        im = canvas(168, 168); d = ImageDraw.Draw(im)
        cx = cy = 84
        for rx, ry, col in ((76, 24, line), (70, 18, fill)):       # outline ellipse, then the ring body inside it ...
            d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=col + (255,))
        for rx, ry in ((59, 11),):                                  # ... and the hole
            d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=(0, 0, 0, 0))
        for rx, ry, col in ((53, 9, line),):                        # inner outline: redraw the hole edge
            pass
        m = Image.new('L', im.size, 0); md = ImageDraw.Draw(m)
        md.rectangle([0, (cy if front else 0) * SS, 168 * SS, (168 if front else cy) * SS], fill=255)
        im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
        return im.rotate(20, resample=Image.BICUBIC, center=(84 * SS, 84 * SS))
    base = ring_half(False)
    disc_im = canvas(168, 168); dd = ImageDraw.Draw(disc_im)
    disc(dd, 84, 84, 46, line + (255,)); disc(dd, 84, 84, 39, fill + (255,))
    im = Image.alpha_composite(Image.alpha_composite(base, disc_im), ring_half(True))
    return done(im, 168, 168)
bg = Image.new('RGBA', (336, 168)); bg.paste(planet(0), (0, 0)); bg.paste(planet(1), (168, 0)); save(bg, 'AstroBG.png')

# ------------------------------------------------------------------ shield: six frames of 208 x 208 (Blue 0/1/2 cracks, Red 0/1/2), a thick ring over a faint glass disc
def shield(side, cracks):
    fill, line = SIDE[side]
    im = canvas(208, 208)
    glass = canvas(208, 208); gd = ImageDraw.Draw(glass); disc(gd, 104, 104, 98, fill + (51,))
    im = Image.alpha_composite(im, glass)
    for r_out, r_in, col in ((102, 74, line), (98, 78, fill)):
        ring = canvas(208, 208); rd = ImageDraw.Draw(ring); disc(rd, 104, 104, r_out, col + (255,)); disc(rd, 104, 104, r_in, (0, 0, 0, 0))
        im = Image.alpha_composite(im, ring)
    cr = canvas(208, 208); cd = ImageDraw.Draw(cr)
    A = [(-72, -60), (-30, -20), (-46, 10), (10, 30), (32, 72)]
    B = [(62, -52), (22, -10), (52, 20), (76, 46)]
    C = [(-8, -88), (6, -42), (-14, -4)]
    for k, path in enumerate((A, B, C)):
        if k < (0 if cracks == 0 else 1 if cracks == 1 else 3):
            thick_line(cd, [(104 + x, 104 + y) for x, y in path], 6, line + (255,))
    mask = canvas(208, 208, (0, 0, 0, 0)); md = ImageDraw.Draw(mask); disc(md, 104, 104, 98, (255, 255, 255, 255))
    cr.putalpha(ImageChops.multiply(cr.getchannel('A'), mask.getchannel('A')))
    return done(Image.alpha_composite(im, cr), 208, 208)
sh = Image.new('RGBA', (1248, 208))
for i in range(6): sh.paste(shield(i // 3, i % 3), (208 * i, 0))
save(sh, 'AstroShield.png')

# ------------------------------------------------------------------ fire flames: four amber drops hanging tip-down (the game turns them upright), 32 x 50 each
def drop(tip_y, tip_dx):
    im = canvas(32, 50); d = ImageDraw.Draw(im)
    def shape(cy, r, ty, col, dx=0):
        disc(d, 16, cy, r, col)
        poly(d, [(16 - r * .97, cy + r * .25), (16 + r * .97, cy + r * .25), (16 + dx, ty)], col)
    shape(15, 12.5, tip_y, AMBER + (255,), tip_dx)
    shape(17, 6.5, tip_y - 12, AMBER_LIGHT + (255,), tip_dx * .5)
    return done(im, 32, 50)
fire = Image.new('RGBA', (128, 50))
for i, (ty, dx) in enumerate(((44, -2), (47, 2), (49, 0), (45, 3))): fire.paste(drop(ty, dx), (32 * i, 0))
save(fire, 'AstroFire.png')

# ------------------------------------------------------------------ explosions: the same frame rectangles as art/AstroExplosion.png (frames 3 and 4 are the grey smoke puffs)
BOOM = [[14, 0, 299, 200], [324, 0, 184, 200], [520, 0, 179, 200], [709, 0, 146, 200], [875, 0, 87, 200], [967, 0, 18, 200]]
ex = canvas(998, 200); ed = ImageDraw.Draw(ex)
def star(cx, cy, r1, r2, n, col):
    poly(ed, [(cx + (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n - math.pi / 2), cy + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n - math.pi / 2)) for i in range(2 * n)], col)
x, w = BOOM[0][0], BOOM[0][2]; star(x + w / 2, 100, 96, 52, 8, AMBER + (255,)); star(x + w / 2, 100, 62, 34, 8, AMBER_LIGHT + (255,))
x, w = BOOM[1][0], BOOM[1][2]; disc(ed, x + w / 2, 100, 84, AMBER + (255,)); disc(ed, x + w / 2, 100, 62, (0, 0, 0, 0)); star(x + w / 2, 100, 40, 22, 8, AMBER_LIGHT + (255,))
x, w = BOOM[2][0], BOOM[2][2]; disc(ed, x + w / 2, 100, 86, AMBER + (150,)); disc(ed, x + w / 2, 100, 74, (0, 0, 0, 0))
for k in range(8):
    a = k * math.pi / 4; disc(ed, x + w / 2 + 40 * math.cos(a), 100 + 40 * math.sin(a), 8, AMBER + (255,))
SMOKE = (208, 208, 200, 235)
x, w = BOOM[3][0], BOOM[3][2]; cx = x + w / 2
for dx, dy, r in ((0, 8, 56), (-34, 22, 40), (34, 22, 40), (0, -24, 40)): disc(ed, cx + dx, 100 + dy, r, SMOKE)
x, w = BOOM[4][0], BOOM[4][2]; cx = x + w / 2
for dx, dy, r in ((0, 6, 32), (-18, 16, 24), (18, 16, 24), (0, -14, 24)): disc(ed, cx + dx, 100 + dy, r, SMOKE)
x, w = BOOM[5][0], BOOM[5][2]; disc(ed, x + w / 2, 100, 8, SMOKE)
save(done(ex, 998, 200), 'AstroExplosion.png')

# ------------------------------------------------------------------ small things
save(Image.new('RGBA', (480, 60)), 'AstroBase.png')           # no base under the pieces: flat design
save(Image.new('RGBA', (160, 60)), 'AstroShadow.png')         # no shadow either

ring = canvas(200, 80); rd = ImageDraw.Draw(ring)             # overcharge warning ring
rd.ellipse([6 * SS, 8 * SS, 194 * SS, 72 * SS], outline=ALERT + (255,), width=9 * SS)
save(done(ring, 200, 80), 'AstroHotRing.png')

bang = canvas(80, 100); bd = ImageDraw.Draw(bang)            # '!' : cream outline first, the red shape on top
for grow, col in ((5, RU_LINE + (255,)), (0, ALERT + (255,))):
    poly(bd, [(40 - 14 - grow, 8 - grow), (40 + 14 + grow, 8 - grow), (40 + 8 + grow, 62 + grow), (40 - 8 - grow, 62 + grow)], col)
    disc(bd, 40, 82, 9 + grow, col)
save(done(bang, 80, 100), 'AstroBang.png')

zz = canvas(148, 144); zd = ImageDraw.Draw(zz)                # 'z z Z' in cream with a dark outline
for (x, y, s) in ((10, 78, 44), (46, 40, 58), (78, -2, 78)):
    zd.text((x * SS, y * SS), 'Z' if s > 70 else 'z', font=font(s * SS), fill=RU_LINE + (255,), stroke_width=4 * SS, stroke_fill=(37, 37, 31, 255))
save(done(zz, 148, 144), 'AstroZzz.png')

glow = Image.new('RGBA', (256, 256))                           # a faint amber glow behind fires
px = glow.load()
for yy in range(256):
    for xx in range(256):
        dd = math.hypot(xx - 127.5, yy - 127.5) / 128
        if dd < 1: px[xx, yy] = (255, 195, 70, int(150 * (1 - dd) ** 1.6))
save(glow, 'AstroGlow.png')

banner = Image.new('RGBA', (1176, 1188))                       # 'Blue wins' / 'Red wins' / 'Draw', frames of 1176 x 396
for i, (txt, fill, line, tcol) in enumerate((('Blue wins', LB, LB_LINE, LB_LINE), ('Red wins', RU, RU_LINE, RU_LINE), ('Draw', (207, 207, 200), (42, 45, 43), (42, 45, 43)))):
    fr = canvas(1176, 396); fd = ImageDraw.Draw(fr)
    fd.rounded_rectangle([30 * SS, 40 * SS, 1146 * SS, 356 * SS], radius=60 * SS, fill=line + (255,))
    fd.rounded_rectangle([46 * SS, 56 * SS, 1130 * SS, 340 * SS], radius=48 * SS, fill=fill + (255,))
    tw = fd.textlength(txt, font=font(170 * SS)); fd.text(((1176 * SS - tw) / 2, 198 * SS), txt, font=font(170 * SS), fill=tcol + (255,), anchor='lm')
    banner.paste(done(fr, 1176, 396), (0, 396 * i))
save(banner, 'AstroBanner.png')

Image.new('RGBA', (858, 772), SKY + (255,)).save(os.path.join(OUT, 'AstroSky.png')); print('wrote AstroSky.png (858, 772)')

# ------------------------------------------------------------------ the board hexes: the shapes come from art/AstroHexes.png
def flat_hex(colour, alpha=255, outline=False):
    im = canvas(192, 220); d = ImageDraw.Draw(im)
    pts = [(95.5, 2), (189, 55.75), (189, 164.25), (95.5, 217), (2, 164.25), (2, 55.75)]
    if outline:
        poly(d, pts, colour + (255,))
        inner = [(95.5 + (x - 95.5) * .985, 109.5 + (y - 109.5) * .985) for x, y in pts]
        im2 = canvas(192, 220); d2 = ImageDraw.Draw(im2); poly(d2, inner, (255, 255, 255, 255))
        a = ImageChops.subtract(im.getchannel('A'), im2.getchannel('A')); im.putalpha(a)
    else:
        poly(d, pts, colour + (alpha,))
    return done(im, 192, 220)
hexes = Image.new('RGBA', (960, 880))
for i in range(15): hexes.paste(flat_hex(TILES[i // 5]), ((i % 5) * 192, (i // 5) * 220))
hexes.paste(flat_hex(LB, 56), (0, 660)); hexes.paste(flat_hex(RU, 77), (192, 660)); hexes.paste(flat_hex(ORANGE, 82), (384, 660))
hexes.paste(flat_hex(GRID, outline=True), (576, 660))
save(hexes, 'AstroHexes.png')
tiles = Image.new('RGBA', (500, 100))
td = ImageDraw.Draw(tiles)
for i in range(5): td.rounded_rectangle([i * 100 + 6, 6, i * 100 + 94, 94], radius=10, fill=TILES[i % 3] + (255,), outline=GRID + (255,), width=2)
save(tiles, 'AstroTiles.png')

# ------------------------------------------------------------------ the frame table of this set (also written into THEME_RECTS['abstract'])
rects = {
    'frames': [[168 * i, 0, 168, 168] for i in range(5)], 'wave': [840, 0, 168, 168], 'drone': [0, 0, 168, 168],
    'neptune': [0, 0, 168, 168], 'mars': [168, 0, 168, 168], 'deco': [[330, 0, 6, 6]],
    'flame': [[32 * i, 0, 32, 50] for i in range(4)], 'flameN': [[32 * i, 0, 32, 50] for i in range(4)], 'flameK': [1, 1, 1, 1], 'turns': False, 'flat': True,
}
with open(os.path.join(OUT, 'theme.json'), 'w', encoding='utf-8') as f: json.dump(rects, f)
print('theme.json written')
