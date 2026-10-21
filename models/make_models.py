"""Printable 3D models of three Astro Game pieces, built from simple solids (no libraries needed):
the astronaut, the rover and the Red drone (rocket ship).

    python make_models.py [scale]          writes *.stl and preview.html next to this file

Units are millimetres. Every piece stands on a flat round base of 1 inch (25.4 mm) across and 4 mm thick, the usual size of a tabletop
miniature base. The astronaut is about 41 mm tall. Pass a scale (for example 0.8) to resize everything, base included.

Curves use SEG = 64 segments around. Every figure is a union of closed shapes that overlap each other; slicers (PrusaSlicer, Cura,
Bambu Studio) merge these automatically. Thinnest parts: solar panel 1.5 mm, rover wheels 2.2 mm, mast 2 mm. All pieces have a flat bottom.
"""
import base64, json, math, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SEG = 64                       # segments round a curve: higher = rounder (and bigger files)
BASE_D, BASE_H = 25.4, 4.0     # 1 inch round base, 4 mm thick

# ---------------------------------------------------------------- mesh helpers (a mesh is a list of ((x,y,z),(x,y,z),(x,y,z)))
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def volume(m): return sum(dot(a, cross(b, c)) for a, b, c in m) / 6
def oriented(m):                                   # make the normals point outwards (positive volume)
    return m if volume(m) >= 0 else [(a, c, b) for a, b, c in m]
def moved(m, dx=0, dy=0, dz=0): return [tuple((v[0] + dx, v[1] + dy, v[2] + dz) for v in t) for t in m]
def scaled(m, sx, sy, sz): return oriented([tuple((v[0] * sx, v[1] * sy, v[2] * sz) for v in t) for t in m])
def rotated(m, axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    def r(v):
        x, y, z = v
        if axis == 'x': return (x, y * c - z * s, y * s + z * c)
        if axis == 'y': return (x * c + z * s, y, -x * s + z * c)
        return (x * c - y * s, x * s + y * c, z)
    return [tuple(r(v) for v in t) for t in m]
def edges_ok(m):                                   # every edge of a closed shape is used by exactly two triangles
    cnt = {}
    for t in m:
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]
            k = tuple(sorted((tuple(round(c, 5) for c in a), tuple(round(c, 5) for c in b))))
            cnt[k] = cnt.get(k, 0) + 1
    return all(v == 2 for v in cnt.values())

def lathe(profile, n=SEG, closed=False):
    """Revolve a (radius, height) outline round the vertical axis. An open outline that starts and ends on the axis gives a solid; a
    closed outline (closed=True, not crossing the axis) gives a ring, tube or shell."""
    profile = [(0 if abs(r) < 1e-9 else r, z) for r, z in profile]          # points that should lie on the axis lie exactly on it
    pts = list(profile) + ([profile[0]] if closed else [])
    tris = []
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        if r0 == 0 and r1 == 0: continue
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            p = lambda r, z, a: (r * math.cos(a), r * math.sin(a), z)
            A, B, C, D = p(r0, z0, a0), p(r0, z0, a1), p(r1, z1, a1), p(r1, z1, a0)
            if r0 == 0: tris.append((A, C, D))
            elif r1 == 0: tris.append((A, B, C))
            else: tris += [(A, B, C), (A, C, D)]
    return oriented(tris)
def cylinder(r, h, n=SEG, r2=None): return lathe([(0, 0), (r, 0), (r if r2 is None else r2, h), (0, h)], n)
def ellipsoid(rx, ry, rz, n=SEG, nv=SEG // 2):
    prof = [(0, -1)] + [(math.sin(math.pi * k / nv), -math.cos(math.pi * k / nv)) for k in range(1, nv)] + [(0, 1)]
    return scaled(lathe(prof, n), rx, ry, rz)
def prism(poly, z0, z1):                            # extrude a CONVEX polygon (x, y) between two heights
    c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)); tris = []; n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        tris += [((c[0], c[1], z0), (b[0], b[1], z0), (a[0], a[1], z0)), ((c[0], c[1], z1), (a[0], a[1], z1), (b[0], b[1], z1)),
                 ((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)), ((a[0], a[1], z0), (b[0], b[1], z1), (a[0], a[1], z1))]
    return oriented(tris)
def octagon(w, h, cut):                              # rectangle with the corners cut
    x, y = w / 2, h / 2
    return [(-x + cut, -y), (x - cut, -y), (x, -y + cut), (x, y - cut), (x - cut, y), (-x + cut, y), (-x, y - cut), (-x, -y + cut)]
def along_x(m, x0, y=0, z=0): return moved(rotated(m, 'y', 90), x0, y, z)   # a vertical solid lying along +x, starting at x0
def along_y(m, y0, x=0, z=0): return moved(rotated(m, 'x', -90), x, y0, z)  # ... along +y
def base(): return lathe([(0, 0), (BASE_D / 2, 0), (BASE_D / 2, BASE_H * .55), (BASE_D / 2 - 1.0, BASE_H), (0, BASE_H)], SEG * 2)
def join(*parts):
    out = []
    for p in parts: out += p
    return out

B = BASE_H   # every figure stands on top of the base: its z = 0 is B
# ---------------------------------------------------------------- the pieces
def astronaut():
    p = [base()]
    for s in (-1, 1):
        p += [moved(ellipsoid(3.4, 4.4, 2.6), s * 3.6, .8, B + 2.0),                  # boots
              moved(cylinder(2.7, 8), s * 3.4, 0, B + 3),                               # legs
              moved(rotated(ellipsoid(2.4, 2.6, 6.2), 'y', -s * 10), s * 8.3, 0, B + 15.5),   # arms
              moved(ellipsoid(2.8, 2.8, 2.8), s * 9.6, .6, B + 9.2)]                    # mitts
    p += [moved(ellipsoid(7.0, 5.4, 9.5), 0, 0, B + 15),                                # suit
          moved(ellipsoid(6.2, 3.1, 8.2), 0, -6.4, B + 16.5),                           # backpack
          moved(cylinder(1.6, 2.4), -2.5, -6.4, B + 24), moved(cylinder(1.6, 2.4), 2.5, -6.4, B + 24),
          moved(cylinder(4.8, 3), 0, 0, B + 21.5),                                      # neck
          moved(ellipsoid(8.6, 8.2, 8.2), 0, 0, B + 28.5),                              # helmet
          moved(ellipsoid(6.7, 3.5, 5.5), 0, 5.0, B + 28.9)]                            # visor (bulges out of the helmet)
    return join(*p)

def rover():
    """The rover is built at a larger size and then shrunk to 70% so that it fits the 25.4 mm base (the barrel, wheels and chassis stay inside it)."""
    body = [moved(prism(octagon(28, 16, 3.5), 0, 7.5), -1, 0, 3.5),                   # chassis (heights are measured from the top of the base)
            moved(ellipsoid(6.5, 5.5, 6.2), 3, 0, 11)]                                  # cockpit dome
    for x in (-10, 0, 10):                                                              # six wheels standing on the base, with hubs
        body += [along_y(cylinder(4.6, 3.2), 8.3, x, 4.6), along_y(cylinder(1.8, 4.2), 8.3, x, 4.6),
                 along_y(cylinder(4.6, 3.2), -11.5, x, 4.6), along_y(cylinder(1.8, 4.2), -12.5, x, 4.6)]
    body += [moved(cylinder(1.4, 5), -9, 0, 10.5), moved(rotated(prism([(-6.5, -4.5), (6.5, -4.5), (6.5, 4.5), (-6.5, 4.5)], 0, 2.2), 'y', -12), -9, 0, 15.5),   # solar panel on a post
             moved(cylinder(1.5, 9), 10, 5, 10.5), moved(cylinder(.8, 3.2, SEG, 4.6), 10, 5, 19.5),                                                              # mast and dish
             along_x(cylinder(1.9, 5.5), 12, 0, 9), along_x(cylinder(2.8, 2.5), 12, 0, 9)]                                                                       # laser barrel with collar
    return join(base(), moved(scaled(join(*body), .7, .7, .7), 0, 0, B))

def drone_red():                                        # the Red drone: a rocket ship with swept wings and two engine pods (rounded shapes only)
    z = B + 5.5                                         # the ship hovers on a short stem
    p = [base(), moved(cylinder(2.8, 6.5), 0, 0, B),
         moved(lathe([(0, 0), (4.2, 0), (5.6, 3), (6.0, 8), (5.2, 14), (3.4, 19.5), (1.6, 23.2), (0, 25)]), 0, 0, z),       # fuselage with a rounded nose
         moved(ellipsoid(3.6, 3.0, 5.5), 0, 3.6, z + 13)]                                                                    # canopy
    for s in (-1, 1):
        p += [moved(rotated(ellipsoid(6.0, 1.5, 5.0), 'y', s * 25), s * 6.6, 0, z + 7.5),                                    # swept wings
              moved(lathe([(0, 0), (2.8, 0), (2.2, 2.5), (2.2, 8), (1.6, 9.5), (0, 9.5)]), s * 7.6, 0, z + .5)]            # engine pods
    return join(*p)

PIECES = [('astronaut', astronaut, '#e9e2cf', 'Astronaut (Blue and Red, same shape)'),
          ('rover', rover, '#6fa8e6', 'Rover (laser barrel points forward)'),
          ('drone_red_ship', drone_red, '#f0646f', 'Red drone: rocket ship')]

def write_stl(path, name, mesh):
    with open(path, 'wb') as f:
        f.write(name.encode()[:79].ljust(80, b' ')); f.write(struct.pack('<I', len(mesh)))
        for a, b, c in mesh:
            n = cross(sub(b, a), sub(c, a)); l = math.sqrt(dot(n, n)) or 1
            f.write(struct.pack('<12fH', n[0] / l, n[1] / l, n[2] / l, *a, *b, *c, 0))

if __name__ == '__main__':
    data = []
    for name, fn, colour, title in PIECES:
        mesh = oriented(scaled(fn(), SCALE, SCALE, SCALE) if SCALE != 1 else fn())
        xs, ys, zs = [[v[i] for t in mesh for v in t] for i in range(3)]
        write_stl(os.path.join(HERE, name + '.stl'), name, mesh)
        flat = [c for t in mesh for v in t for c in v]
        data.append({'name': name, 'title': title, 'colour': colour, 'tris': len(mesh),
                     'size': [round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1), round(max(zs) - min(zs), 1)],
                     'b64': base64.b64encode(struct.pack('<%df' % len(flat), *flat)).decode()})
        print('%-16s %6d triangles, %4.1f x %4.1f x %4.1f mm' % (name, len(mesh), max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))
    html = open(os.path.join(HERE, 'preview_template.html'), encoding='utf8').read().replace('/*DATA*/[]', json.dumps(data))
    open(os.path.join(HERE, 'preview.html'), 'w', encoding='utf8').write(html)
    print('wrote', len(PIECES), 'STL files and preview.html')
