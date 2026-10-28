from lib import *
def save(img, name): img.save('cuts/' + name + '.png'); print(name, img.size)
def parts(box, gap=3, minw=8, pocket=True):
    ps = split_cols(box, gap=gap, minw=minw)
    return [cut(p, pocket) for p in ps]
items = {}
items['drone_blue'] = cut((8, 198, 230, 388), 'all'); items['drone_red'] = cut((224, 198, 424, 388), 'all')
items['rover_blue'] = cut((418, 200, 652, 388), 'all'); items['rover_red'] = cut((654, 200, 890, 388), 'all')
items['barrel_on'] = cut((890, 262, 1014, 382)); items['barrel_off'] = cut((1108, 262, 1250, 382))
items['shield'] = cut((1294, 196, 1508, 388), False)
for k, v in items.items(): save(v, k)
fl = parts((15, 418, 252, 528), gap=2); [save(x, f'flame{i}') for i, x in enumerate(fl)]
ex = [cut(b, False) for b in refine((262, 404, 1008, 530), [468, 566, 684, 800, 912])]; [save(x, f'boom{i}') for i, x in enumerate(ex)]
save(cut((1040, 404, 1180, 522)), 'bang'); save(cut((1190, 418, 1332, 508)), 'zzz'); save(cut((1332, 414, 1512, 506), 'all'), 'hotring')
save(cut((405, 546, 548, 694)), 'island_blue'); save(cut((548, 550, 690, 694)), 'island_red')
dec = [cut(b) for b in refine((690, 556, 1162, 718), [790, 897, 1003, 1088], win=15)]; [save(x, f'deco{i}') for i, x in enumerate(dec)]
save(cut((1162, 552, 1318, 708), 'all'), 'crystal'); save(cut((1330, 600, 1512, 708)), 'shadow')
tl = [cut(b, False) for b in refine((20, 746, 456, 828), [98, 168, 238, 308, 378], win=10)]; [save(x, f'tile{i}') for i, x in enumerate(tl)]
hx = [cut(b, False) for b in refine((460, 746, 830, 832), [540, 610, 680, 750], win=10)]; [save(x, f'hexo{i}') for i, x in enumerate(hx)]
bn = [cut(b) for b in refine((826, 738, 1280, 870), [1066], win=25)]; [save(x, f'banner{i}') for i, x in enumerate(bn)]
save(cut((1262, 768, 1516, 822)), 'beam')
