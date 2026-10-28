"""Turns the blue flames and the blue crystal of the fantasy set orange (hue shift), from the untouched originals AstroFire_blue.png / AstroCrystal_blue.png
in this folder to art/fantasy/ (run from the repository root)."""
from PIL import Image
import numpy as np
def orange(src, dst):
    im = Image.open('tools/fantasy_extract/' + src).convert('RGBA'); a = im.getchannel('A')
    h, s, v = [np.array(c).astype(float) for c in im.convert('RGB').convert('HSV').split()]
    k = s > 25                                                    # keep greys/whites (bright cores) as they are
    h[k] = np.clip(h[k] * 0 + 24 + (h[k] - 150) * .25, 14, 36)   # blue range -> orange/amber (PIL hue 0..255: 24 = 34 deg)
    s[k] = np.clip(s[k] * 1.1, 0, 255)
    out = Image.merge('HSV', [Image.fromarray(c.astype('uint8')) for c in (h, s, v)]).convert('RGB'); out.putalpha(a)
    out.save('art/fantasy/' + dst)
orange('AstroFire_blue.png', 'AstroFire.png'); orange('AstroCrystal_blue.png', 'AstroCrystal.png'); print('ok')
