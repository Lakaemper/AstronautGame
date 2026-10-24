import json, math, pickle, colorsys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops
import numpy as np

OUT = r'C:\GitCopies\AstronautGame\art\fantasy'
os.makedirs(OUT, exist_ok=True)
L = lambda n: Image.open(f'cuts/{n}.png').convert('RGBA')
wiz = pickle.load(open('wiz.pkl', 'rb'))
theme = {}


def canvas(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def scaled(img, w=None, h=None, f=None):
    if f is not None: w, h = max(1, round(img.width * f)), max(1, round(img.height * f))
    elif w is None: w = max(1, round(img.width * h / img.height))
    elif h is None: h = max(1, round(img.height * w / img.width))
    r = img.resize((w, h), Image.LANCZOS)
    if w > img.width * 1.3: r = r.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    return r


def fit(img, w, h):
    f = min(w / img.width, h / img.height)
    return scaled(img, f=f)


def put(cv, img, x, y):
    cv.alpha_composite(img, (int(x), int(y)))


def place(cv, img, cx=None, bottom=None, left=None, cy=None):
    x = round(cx - img.width / 2) if cx is not None else left
    y = round(bottom - img.height) if bottom is not None else round(cy - img.height / 2)
    put(cv, img, x, y)


def hue_shift(img, fn):
    a = np.array(img).astype(float) / 255
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mx = a[..., :3].max(2); mn = a[..., :3].min(2); v = mx; d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.maximum(d, 1e-6), 0); gc = np.where(m, (mx - g) / np.maximum(d, 1e-6), 0); bc = np.where(m, (mx - b) / np.maximum(d, 1e-6), 0)
    h = np.where(mx == r, bc - gc, np.where(mx == g, 2 + rc - bc, 4 + gc - rc)); h = (h / 6) % 1.0; h = np.where(m, h, 0)
    h2, s2, v2 = fn(h, s, v)
    i = np.floor(h2 * 6).astype(int) % 6; f = h2 * 6 - np.floor(h2 * 6)
    p = v2 * (1 - s2); q = v2 * (1 - f * s2); t = v2 * (1 - (1 - f) * s2)
    rr = np.choose(i, [v2, q, p, p, t, v2]); gg = np.choose(i, [t, v2, v2, q, p, p]); bb = np.choose(i, [p, p, t, v2, v2, q])
    out = np.dstack([rr, gg, bb, al]); return Image.fromarray((out * 255 + .5).astype(np.uint8), 'RGBA')


def blue_to_red(img):
    def fn(h, s, v):
        sel = (h > 0.45) & (h < 0.72) & (s > 0.2)
        return np.where(sel, 0.015 + (h - 0.58) * 0.15, h) % 1.0, np.where(sel, np.minimum(1, s * 1.05), s), v
    return hue_shift(img, fn)


def save(img, name): img.save(os.path.join(OUT, name)); print(name, img.size)


# ---------------------------------------------------------------- wizards
order = [2, 3, 0, 1, 4]            # game frame idx 0..4 <- pose in the picture (front, front 3/4 (mirrored), profile, back 3/4, back)
flipped = {3}
S0 = 154 / 160
frames = {}
for col in ('blue', 'red'):
    ims = []
    for idx, p in enumerate(order):
        im = wiz[col][p]
        if p in flipped: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        ims.append(scaled(im, f=S0))
    ims.append(scaled(wiz[col][6], f=S0))        # wave: orb raised
    frames[col] = ims
widths = [max(frames['blue'][i].width, frames['red'][i].width) + 6 for i in range(6)]
rects = []; x = 2
for w in widths: rects.append([x, 0, w, 160]); x += w + 2
SW = x + 2
for col, name in (('blue', 'AstroAnimsheet.png'), ('red', 'AstroAnimsheetRed.png')):
    cv = canvas(SW, 160)
    for i, im in enumerate(frames[col]):
        r = rects[i]; place(cv, im, cx=r[0] + r[2] / 2, bottom=158)
    save(cv, name)
theme['frames'] = rects[:5]; theme['wave'] = rects[5]

# ---------------------------------------------------------------- drones (dragons)
dw = max(L('drone_blue').width, L('drone_red').width) + 8; dh = max(L('drone_blue').height, L('drone_red').height) + 8
for src, name in (('drone_blue', 'AstroShipBlue.png'), ('drone_red', 'AstroShipRed.png')):
    cv = canvas(dw, dh); place(cv, L(src), cx=dw / 2, bottom=dh - 3); save(cv, name)
theme['drone'] = [0, 0, dw, dh]

# ---------------------------------------------------------------- smashers (the ogre; the laser barrels were removed with the laser)
for src, name in (('rover_blue', 'AstroSmasherBlue.png'), ('rover_red', 'AstroSmasherRed.png')):
    cv = canvas(220, 184); place(cv, fit(L(src), 214, 168), cx=108, bottom=176); save(cv, name)

# ---------------------------------------------------------------- shield: 6 frames of 208 x 208
CR1 = [[[-.05, -1], [.05, -.55], [-.12, -.2], [.1, .1], [0, .5], [.08, 1]], [[.1, .1], [.45, .2], [.6, .5], [.95, .55]], [[-.12, -.2], [-.5, -.1], [-.7, .25], [-1, .3]], [[.05, -.55], [.4, -.7], [.65, -.5], [.95, -.6]]]
CR2 = [[[-.12, -.2], [-.2, .3], [-.35, .65], [-.3, 1]], [[.1, .1], [.3, .45], [.55, .8]], [[.05, -.55], [-.3, -.75], [-.6, -.7], [-.9, -.5]]]
base_sh = L('shield').resize((198, 198), Image.LANCZOS)


def with_alpha(im, k):
    a = im.getchannel('A').point(lambda v: int(v * k)); r = im.copy(); r.putalpha(a); return r


def cracks(stage):
    S = 4; lay = Image.new('RGBA', (208 * S, 208 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = 92 * S; c = 104 * S
    polys = CR1 + (CR2 if stage >= 2 else [])
    for col, lw, off in (((255, 255, 255, 235), 4.6, 1.8), ((11, 22, 64, 235), 2.6, 0)):
        for pl in polys:
            pts = [(c + x * r + off * S, c + y * r + off * S) for x, y in pl]
            d.line(pts, fill=col, width=int(lw * S * .9), joint='curve')
    mask = Image.new('L', lay.size, 0); ImageDraw.Draw(mask).ellipse([c - r, c - r, c + r, c + r], fill=255)
    lay.putalpha(ImageChops.multiply(lay.getchannel('A'), mask))
    return lay.resize((208, 208), Image.LANCZOS)


sheet = canvas(6 * 208, 208)
for team in (0, 1):
    base = base_sh if team == 0 else blue_to_red(base_sh)
    for st in range(3):
        fr = canvas(208, 208); put(fr, with_alpha(base, .9 if st == 0 else .66), 5, 5)
        if st: fr.alpha_composite(cracks(st))
        put(sheet, fr, (team * 3 + st) * 208, 0)
save(sheet, 'AstroShield.png')

# ---------------------------------------------------------------- bases (3 x 160 x 60), shadow, ring, marks, glow
S = 4
cvb = canvas(480, 60)
for i, col in enumerate([(47, 143, 232), (233, 71, 90), (120, 120, 120)]):
    big = Image.new('RGBA', (160 * S, 60 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big); cx, cy = 80 * S, 30 * S
    d.ellipse([cx - 70 * S, cy - 21 * S, cx + 70 * S, cy + 21 * S], fill=(28, 22, 16, 255))
    d.ellipse([cx - 66 * S, cy - 18 * S, cx + 66 * S, cy + 18 * S], fill=(201, 162, 74, 255))
    d.ellipse([cx - 62 * S, cy - 15 * S, cx + 62 * S, cy + 15 * S], fill=col + (255,))
    d.ellipse([cx - 52 * S, cy - 13 * S, cx + 40 * S, cy + 2 * S], fill=tuple(min(255, int(c * 1.25 + 20)) for c in col) + (120,))
    put(cvb, big.resize((160, 60), Image.LANCZOS), i * 160, 0)
save(cvb, 'AstroBase.png')
cv = canvas(160, 60); place(cv, L('shadow'), cx=83, cy=31); save(cv, 'AstroShadow.png')
cv = canvas(200, 80); place(cv, fit(L('hotring'), 198, 78), cx=100, cy=40); save(cv, 'AstroHotRing.png')
cv = canvas(80, 100); place(cv, fit(L('bang'), 76, 96), cx=40, cy=50); save(cv, 'AstroBang.png')
cv = canvas(148, 144); place(cv, fit(L('zzz'), 140, 100), cx=82, cy=64); save(cv, 'AstroZzz.png')
gl = Image.new('RGBA', (256, 256)); px = gl.load()
for yy in range(256):
    for xx in range(256):
        dd = math.hypot(xx - 127.5, yy - 127.5) / 128
        a = max(0.0, 1 - dd); a = a * a * (3 - 2 * a)
        px[xx, yy] = (int(150 + 60 * (1 - dd)), int(200 + 40 * (1 - dd)), 255, int(255 * a))
save(gl, 'AstroGlow.png')
cry = canvas(160, 160); place(cry, fit(L('crystal'), 150, 150), cx=80, bottom=156); save(cry, 'AstroCrystal.png')

# ---------------------------------------------------------------- flames (hanging down, 4 frames in 179 x 50)
fl = canvas(179, 50)
for (x, y, w, h), n in zip([[12, 0, 25, 50], [51, 0, 26, 50], [94, 0, 29, 50], [144, 0, 22, 50]], range(4)):
    im = L(f'flame{n}').transpose(Image.FLIP_TOP_BOTTOM); im = fit(im, w, h); place(fl, im, cx=x + w / 2, cy=y + h / 2)
save(fl, 'AstroFire.png')
# ---------------------------------------------------------------- explosion
ex = canvas(998, 200)
for (x, y, w, h), n in zip([[14, 0, 299, 200], [324, 0, 184, 200], [520, 0, 179, 200], [709, 0, 146, 200], [875, 0, 87, 200], [967, 0, 18, 200]], range(6)):
    im = fit(L(f'boom{n}'), w, h); place(ex, im, cx=x + w / 2, cy=y + h / 2 if n else 100)
save(ex, 'AstroExplosion.png')

# ---------------------------------------------------------------- hexes and tiles
HS2 = 108; HW2 = HS2 * math.sqrt(3) / 2 * 2          # 187 px wide, 216 px high
def hex_poly(cx, cy, r, S=1): return [(cx + r * math.cos(math.radians(60 * i - 30)) * S, cy + r * math.sin(math.radians(60 * i - 30)) * S) for i in range(6)]
def hex_mask(w, h, r, cx, cy):
    S = 4; m = Image.new('L', (w * S, h * S), 0); ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in hex_poly(cx, cy, r)], fill=255)
    return m.resize((w, h), Image.LANCZOS)
tiles = []
for n in range(5):
    t = L(f'tile{n}'); w, h = t.size
    inner = t.crop((int(w * .11), int(h * .13), int(w * .89), int(h * .87)))
    inner = inner.resize((190, 218), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    inner = ImageEnhance.Color(inner).enhance(.7); inner = ImageEnhance.Brightness(inner).enhance(.62); inner = ImageEnhance.Contrast(inner).enhance(.9)   # calm ground, so the pieces stand out
    tiles.append(inner)
def tint(im, t):
    if t == 0: return im
    r, g, b, a = im.split()
    if t == 1: return Image.merge('RGBA', (r.point(lambda v: min(255, int(v * 1.08))), g.point(lambda v: min(255, int(v * 1.08))), b.point(lambda v: min(255, int(v * 1.04))), a))
    return Image.merge('RGBA', (r.point(lambda v: int(v * .9)), g.point(lambda v: int(v * .95)), b.point(lambda v: min(255, int(v * 1.02))), a))
hexes = canvas(960, 880); mask = hex_mask(192, 220, HS2, 96, 110)
for t in range(3):
    for k in range(5):
        fr = canvas(192, 220); tile = tint(tiles[k], t); fr.alpha_composite(tile, (1, 1))
        a = ImageChops.multiply(fr.getchannel('A'), mask); fr.putalpha(a); put(hexes, fr, k * 192, t * 220)
for i, col in enumerate([(58, 160, 255, 120), (255, 90, 110, 120), (255, 225, 77, 96)]):
    fr = canvas(192, 220); fr.paste(Image.new('RGBA', (192, 220), col), (0, 0), mask); put(hexes, fr, i * 192, 3 * 220)
S = 4; ol = Image.new('RGBA', (192 * S, 220 * S), (0, 0, 0, 0)); ImageDraw.Draw(ol).polygon([(x * S, y * S) for x, y in hex_poly(96, 110, HS2)], outline=(16, 12, 8, 210), width=4 * S)
put(hexes, ol.resize((192, 220), Image.LANCZOS), 3 * 192, 3 * 220)
save(hexes, 'AstroHexes.png')
tl = canvas(500, 100)
for k in range(5): put(tl, tiles[k].resize((100, 100), Image.LANCZOS), k * 100, 0)
save(tl, 'AstroTiles.png')

# ---------------------------------------------------------------- sky
pan = Image.open('src.webp').convert('RGB').crop((22, 868, 822, 990))
sky = pan.resize((858, 772), Image.LANCZOS).filter(ImageFilter.GaussianBlur(7))
sky = ImageEnhance.Brightness(sky).enhance(.5); sky = ImageEnhance.Color(sky).enhance(.85)
save(sky.convert('RGBA'), 'AstroSky.png')

# ---------------------------------------------------------------- banner: 3 frames of 1176 x 396
fnt = ImageFont.truetype(r'C:\Windows\Fonts\georgiab.ttf', 60)
bn = canvas(1176, 3 * 396)
grey = L('banner0').convert('LA').convert('RGBA')
for i, (src, text, col) in enumerate([(L('banner0'), 'Blue wins!', (20, 40, 110)), (L('banner1'), 'Red wins!', (120, 20, 20)), (grey, 'Draw!', (60, 60, 60))]):
    im = scaled(src, f=1.75); fr = canvas(1176, 396); place(fr, im, cx=588, cy=198)
    d = ImageDraw.Draw(fr); tw = d.textlength(text, font=fnt)
    cx = 588 - im.width / 2 + im.width * .4; cy = 198 - im.height / 2 + im.height * .62
    d.text((cx, cy), text, font=fnt, anchor='mm', fill=(255, 240, 200, 255), stroke_width=7, stroke_fill=col + (255,))
    put(bn, fr, 0, i * 396)
save(bn, 'AstroBanner.png')

# (the laser beam picture was removed with the laser)

# ---------------------------------------------------------------- sticker sheet (Home Planets + decoration)
items = [('neptune', L('island_blue')), ('mars', L('island_red'))] + [(f'deco{i}', L(f'deco{i}')) for i in range(5)]
X = 4; Y = 4; rowh = 0; SWD = 520; rects = {}
for name, im in items:
    if X + im.width + 4 > SWD: X = 4; Y += rowh + 4; rowh = 0
    rects[name] = [X, Y, im.width, im.height]; X += im.width + 4; rowh = max(rowh, im.height)
bg = canvas(SWD, Y + rowh + 4)
for name, im in items: put(bg, im, rects[name][0], rects[name][1])
save(bg, 'AstroBG.png')
theme['neptune'] = rects['neptune']; theme['mars'] = rects['mars']; theme['deco'] = [rects[f'deco{i}'] for i in range(5)]
json.dump(theme, open(os.path.join(OUT, 'theme.json'), 'w'), indent=1)
print(json.dumps(theme))
