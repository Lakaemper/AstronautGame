"""Gives the ground tiles (frames 0-14) of art/fantasy/AstroHexes.png a faint dark green tint, starting from the untinted original
tools/fantasy_extract/AstroHexes_grey.png (run from the repository root)."""
from PIL import Image
import numpy as np
im = np.array(Image.open('tools/fantasy_extract/AstroHexes_grey.png').convert('RGBA')).astype(float)
m = np.array([.72, .86, .72]); add = np.array([-2, 2, -1])
tiles = im[:660]
tiles[..., :3] = np.clip(tiles[..., :3] * m + add, 0, 255)
Image.fromarray(im.astype('uint8'), 'RGBA').save('art/fantasy/AstroHexes.png')
print('tinted')
