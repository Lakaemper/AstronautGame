import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
SRC = Image.open('src.webp').convert('RGB')
A = np.array(SRC).astype(int)
def bgmask(box, pocket=True):
    x0, y0, x1, y1 = box
    a = A[y0:y1, x0:x1]
    mx = a.max(2); mn = a.min(2)
    like = ((mx - mn) <= 14) & (mn >= 196)
    lab, n = ndi.label(like, structure=np.ones((3, 3)))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    if pocket == 'all':
        for i in range(1, n + 1):
            if i in border: continue
            m = lab == i
            if m.sum() >= 28: bg |= m
    elif pocket:                       # enclosed light-grey pockets that are big and flat (the checkerboard seen through gaps)
        for i in range(1, n + 1):
            if i in border: continue
            m = lab == i; ar = m.sum()
            if ar >= 70:
                vals = a[m][:, 0]
                if vals.std() < 24 and vals.min() >= 200 and vals.mean() >= 218:   # checkerboard is flat; hair/glass is not
                    bg |= m
    return bg
def cut(box, pocket=True, erode=1, trim=True):
    x0, y0, x1, y1 = box
    bg = bgmask(box, pocket)
    fg = ~bg
    # remove tiny specks
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    if n:
        sizes = ndi.sum(fg, lab, range(1, n + 1))
        for i, s in enumerate(sizes, 1):
            if s < 40: fg[lab == i] = False
    if erode: fg = ndi.binary_erosion(fg, iterations=erode)
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    rgb = SRC.crop(box)
    out = rgb.convert('RGBA'); out.putalpha(alpha)
    if trim:
        bb = out.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        if bb: out = out.crop(bb)
    return out
def split_cols(box, gap=3, minw=20):
    x0, y0, x1, y1 = box
    fg = ~bgmask(box, False)
    cols = fg.sum(0) > 0
    parts = []; start = None; blank = 0
    for i, c in enumerate(cols):
        if c:
            if start is None: start = i
            blank = 0; end = i
        else:
            if start is not None:
                blank += 1
                if blank >= gap:
                    if end - start >= minw: parts.append((x0 + start, y0, x0 + end + 1, y1))
                    start = None
    if start is not None and end - start >= minw: parts.append((x0 + start, y0, x0 + end + 1, y1))
    return parts
def montage(imgs, path, bg=(70, 70, 90), pad=8):
    h = max(i.height for i in imgs); w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    m = Image.new('RGB', (w, h + 2 * pad), bg); x = pad
    for i in imgs:
        m.paste(i, (x, pad + h - i.height), i); x += i.width + pad
    m.save(path)

def refine(box, guesses, win=12):
    x0, y0, x1, y1 = box
    fg = ~bgmask(box, False); cols = fg.sum(0)
    out = [x0]
    for g in guesses:
        lo = max(1, g - x0 - win); hi = min(len(cols) - 1, g - x0 + win)
        out.append(x0 + lo + int(np.argmin(cols[lo:hi])))
    out.append(x1)
    return [(out[i], y0, out[i + 1], y1) for i in range(len(out) - 1)]
