from lib import *
import json
def refine(box, guesses, win=14):
    x0,y0,x1,y1 = box
    fg = ~bgmask(box, False); cols = fg.sum(0)
    out = [x0]
    for g in guesses:
        lo = max(1, g - x0 - win); hi = min(len(cols) - 1, g - x0 + win)
        out.append(x0 + lo + int(np.argmin(cols[lo:hi])))
    out.append(x1)
    return out
res = {}
# wizards
for name, box, guesses in [('blue', (8, 0, 774, 170), [138, 240, 345, 445, 543, 643]), ('red', (776, 0, 1536, 170), [905, 1003, 1107, 1208, 1305, 1405])]:
    xs = refine(box, guesses)
    parts = [(xs[i], 0, xs[i+1], 170) for i in range(7)]
    imgs = [cut(p) for p in parts]
    res[name] = imgs
    montage(imgs, f'w_{name}.png')
    print(name, xs, [i.size for i in imgs])
import pickle; pickle.dump({k:[i for i in v] for k,v in res.items()}, open('wiz.pkl','wb'))
