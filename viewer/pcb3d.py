"""Viewer assets for any board: photoreal surface maps, component model, parts table.

usage: pcb3d.py <board.kicad_pcb> <prefix> <daughter | mb:<year module>> [px on the long side]
writes (prefix '' = the daughterboard's historic names):
  <prefix>top_albedo/orm/normal.webp, <prefix>bottom_*.webp   board surfaces
  <prefix>board.glb.gz.b64.txt                                   merged component meshes
  <prefix>parts.json                                             parts table with 3D pick boxes
Board-local world frame: mm, Y up, board bottom face at y = 0, centred on the outline's bbox.
Parts with no KiCad 3D model (the TE harness header, the MAP sensor) get simple procedural models.
"""
import sys, os, json, math, subprocess, collections, re
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import pcbnew, trimesh

BOARD, PRE, KIND = sys.argv[1], sys.argv[2], sys.argv[3]
LONG = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'scripts')
OUT = os.environ.get('OUTDIR', HERE)           # where the assets go (default: next to the viewer)
MASK = os.environ.get('MASK', 'green')         # solder mask colour: green (the viewer) or black (README renders)
FINISH = os.environ.get('FINISH', 'hasl')      # pad finish: hasl (tin, the default) or enig (gold, README renders)
sys.path.insert(0, SCRIPTS)
WORK = os.path.join(HERE, 'work_' + (PRE or 'daughter'))
os.makedirs(WORK, exist_ok=True)
GLTFPACK = os.environ.get('GLTFPACK', 'gltfpack')        # npm i gltfpack, or set GLTFPACK to its path
ENV = dict(os.environ, KICAD6_3DMODEL_DIR='/usr/share/kicad/3dmodels', KICAD7_3DMODEL_DIR='/usr/share/kicad/3dmodels')
board = pcbnew.LoadBoard(BOARD)

# ---------------------------------------------------------------- layer rasters
LAYERS = ['F.Cu', 'B.Cu', 'F.Mask', 'B.Mask', 'F.SilkS', 'B.SilkS']
for L in LAYERS:
    svg = f'{WORK}/{L}.svg'
    subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--exclude-drawing-sheet', '--page-size-mode', '2',
                    '--black-and-white', '-l', L, '-o', svg, BOARD], check=True, capture_output=True)
head = open(f'{WORK}/F.Cu.svg').read(2000)
BW, BH = (float(v) for v in re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', head).groups())
if BW >= BH:
    W = LONG; H = int(round(LONG * BH / BW))
else:
    H = LONG; W = int(round(LONG * BW / BH))
for L in LAYERS:
    subprocess.run(['rsvg-convert', '-w', str(W), '-h', str(H), '-b', 'white', f'{WORK}/{L}.svg', '-o', f'{WORK}/{L}.png'], check=True)
bb = board.ComputeBoundingBox(False)          # the SVG page covers every item, incl. silk past the edge
cxk, cyk = pcbnew.ToMM(bb.Centre().x), pcbnew.ToMM(bb.Centre().y)
ox, oy = cxk - BW / 2, cyk - BH / 2           # KiCad mm of the raster's top-left corner
sx, sy = W / BW, H / BH
PX = BW / W
CX, CZ = ox + BW / 2, oy + BH / 2             # world origin in KiCad mm
rng = np.random.default_rng(7)
print(f'{PRE or "daughter"}: {BW:.2f} x {BH:.2f} mm, raster {W} x {H}')


def lay(name):
    return np.array(Image.open(f'{WORK}/{name}.png').convert('L')) < 128


def px(x, y):
    return (pcbnew.ToMM(x) - ox) * sx, (pcbnew.ToMM(y) - oy) * sy


# outline from Edge.Cuts (works for notched / rounded outlines)
ps = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(ps)
im = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(im)
for k in range(ps.OutlineCount()):
    o = ps.Outline(k)
    d.polygon([px(o.CPoint(i).x, o.CPoint(i).y) for i in range(o.PointCount())], fill=255)
inside = np.array(im) > 127
outside = ~inside
edge_band = inside & (ndi.distance_transform_edt(inside) < 6)
yy, xx = np.mgrid[0:H, 0:W]


def disc(mask, cx, cy, r, val=True):
    x0, x1 = int(max(0, cx - r - 2)), int(min(W, cx + r + 3))
    y0, y1 = int(max(0, cy - r - 2)), int(min(H, cy + r + 3))
    sub = (xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2 <= r * r
    mask[y0:y1, x0:x1][sub] = val


holes = np.zeros((H, W), bool)
via_hole = np.zeros((H, W), bool)
for t in board.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        cx, cy = px(t.GetPosition().x, t.GetPosition().y)
        disc(via_hole, cx, cy, pcbnew.ToMM(t.GetDrillValue()) / 2 * sx)
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetDrillSize().x > 0:
            cx, cy = px(p.GetPosition().x, p.GetPosition().y)
            disc(holes, cx, cy, pcbnew.ToMM(p.GetDrillSize().x) / 2 * sx)


def noise(scale, amp):
    n = ndi.gaussian_filter(rng.standard_normal((H // scale + 2, W // scale + 2)), 1.0)
    n = ndi.zoom(n, scale, order=1)[:H, :W]
    return n / (np.abs(n).max() + 1e-9) * amp


weave = (np.sin(xx * PX * 2 * np.pi / 0.42) * np.sin(yy * PX * 2 * np.pi / 0.42)) * 0.5
mottle = noise(64, 1.0) + noise(8, 0.35)
# solder mask over bare laminate / over copper, plugged-via dimples
MASKS = {'green': ([8, 54, 30], [22, 92, 46], [5, 26, 14]),
         'black': ([11, 12, 13], [27, 28, 30], [4, 4, 5])}
C_LAM, C_CU, C_DIMPLE = (np.array(c, float) for c in MASKS[MASK])
C_HASL = np.array([214, 178, 104] if FINISH == 'enig' else [206, 207, 203], float); C_SILK = np.array([238, 238, 230], float)
C_BARE = np.array([92, 98, 58], float)


def build(side, cu, mask_open, silk):
    cu = cu & ~outside
    exposed = mask_open & cu & ~edge_band
    silk = silk & ~mask_open & ~edge_band & ~outside
    masked = ~exposed & ~outside
    h = ndi.gaussian_filter(cu * 0.035, 1.6 * PX * 0 + 1.6)
    dist = ndi.distance_transform_edt(exposed)
    dome = 0.02 if FINISH == 'enig' else 0.12                # ENIG is flat; HASL solder domes on the pads
    h = np.where(exposed, 0.035 + np.minimum(dist * PX, 0.25) * dome, h)
    h += ndi.gaussian_filter(silk * 0.022, 0.8)
    h -= ndi.gaussian_filter(via_hole * 0.03, 1.0)
    h += weave * 0.0012 * (~cu & masked) + mottle * 0.0008
    gy, gx = np.gradient(h, PX)
    n = np.dstack([-gx * 2.2, gy * 2.2, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = ((n * 0.5 + 0.5) * 255).astype(np.uint8)
    cov = ndi.gaussian_filter(cu.astype(float), 1.2)[..., None]
    col = C_LAM * (1 - cov) + C_CU * cov
    col *= (1 + mottle[..., None] * 0.05 + (weave * (cov[..., 0] < 0.5))[..., None] * 0.04)
    col = np.where(via_hole[..., None] & masked[..., None], C_DIMPLE, col)
    s = ndi.gaussian_filter(silk.astype(float), 0.7)[..., None]
    col = col * (1 - s) + C_SILK * (1 + mottle[..., None] * 0.02) * s
    hasl = C_HASL * (1 + (noise(4, 1.0) * (0.02 if FINISH == 'enig' else 0.05))[..., None])
    bare = mask_open & ~cu & ~edge_band & ~outside
    col = np.where(bare[..., None], C_BARE * (1 + mottle[..., None] * 0.05), col)
    col = np.where(exposed[..., None], hasl, col)
    alpha = np.where(outside | holes, 0, 255).astype(np.uint8)
    albedo = np.dstack([np.clip(col, 0, 255).astype(np.uint8), alpha])
    clear = np.where(masked & ~bare & ~(s[..., 0] > 0.5), 255, 0).astype(np.uint8)
    rough = np.where(exposed, (0.2 + noise(4, 0.03)) if FINISH == 'enig' else (0.32 + noise(4, 0.08)), np.where(s[..., 0] > 0.5, 0.82, np.where(bare, 0.7, 0.42 + mottle * 0.04)))
    orm = np.dstack([clear, np.clip(rough * 255, 0, 255).astype(np.uint8), (np.where(exposed, 255, 0)).astype(np.uint8)])
    for k, a, mode, q in (('albedo', albedo, 'RGBA', 90), ('orm', orm, 'RGB', 90), ('normal', normal, 'RGB', 92)):
        Image.fromarray(a, mode).save(f'{OUT}/{PRE}{side}_{k}.webp', quality=q, method=6)


build('top', lay('F.Cu'), lay('F.Mask'), lay('F.SilkS'))
build('bottom', lay('B.Cu'), lay('B.Mask'), lay('B.SilkS'))
print('surface maps done')

# ---------------------------------------------------------------- parts table
if KIND == 'daughter':
    import design
    meta = {p['ref']: p for p in design.parts}
else:
    import importlib, mb_common
    M = importlib.import_module(KIND.split(':')[1]); M.build_parts()
    meta = {p['ref']: p for p in mb_common.parts}
MPN = json.load(open(os.path.join(SCRIPTS, 'mpn.json')))
EXTRA_MPN = {'TE 174917-6': ('TE Connectivity', '174917-6')}
rows = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref.startswith('H'):
        continue
    b = fp.GetBoundingBox(False, False)
    md = meta.get(ref, {})
    r = dict(ref=ref, value=md.get('value', fp.GetValue()), lcsc=md.get('lcsc', ''), desc=md.get('desc', ''),
             fp=fp.GetFPIDAsString().split(':')[-1],
             x0=round(pcbnew.ToMM(b.GetLeft()) - ox, 3), y0=round(pcbnew.ToMM(b.GetTop()) - oy, 3),
             x1=round(pcbnew.ToMM(b.GetRight()) - ox, 3), y1=round(pcbnew.ToMM(b.GetBottom()) - oy, 3))
    m = MPN.get(r['lcsc'])
    if m and m.get('mpn'):
        r['mfr'], r['mpn'] = m['mfr'], m['mpn']
    elif r['value'] in EXTRA_MPN:
        r['mfr'], r['mpn'] = EXTRA_MPN[r['value']]
    rows.append(r)

# ---------------------------------------------------------------- component model
step = f'{WORK}/board.step'
# This KiCad install lacks a few library models: point those footprints at an equivalent body that it has
# (the exposed pad of the SOIC-8 parts is underneath, out of sight). Crystal, tactile switches and the
# parts with no library model at all get procedural models below.
SUBST = {'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm': 'Package_SO.3dshapes/SO-8_3.9x4.9mm_P1.27mm.wrl',
         'Infineon_PG-DSO-8-27_3.9x4.9mm_EP2.65x3mm': 'Package_SO.3dshapes/SO-8_3.9x4.9mm_P1.27mm.wrl',
         'Fuse_1812_4532Metric': 'Capacitor_SMD.3dshapes/C_1812_4532Metric.wrl'}
MODELDIR = '/usr/share/kicad/3dmodels/'
sub_board = pcbnew.LoadBoard(BOARD)
nsub = 0
for fp in sub_board.GetFootprints():
    key = fp.GetFPIDAsString().split(':')[-1]
    if key in SUBST:
        models = [m for m in fp.Models()]          # the API hands out copies: rebuild the list
        fp.Models().clear()
        for m in models:
            f = m.m_Filename.replace('${KICAD6_3DMODEL_DIR}/', MODELDIR).replace('${KICAD7_3DMODEL_DIR}/', MODELDIR)
            if not os.path.exists(f) and not os.path.exists(os.path.splitext(f)[0] + '.step'):
                m.m_Filename = MODELDIR + SUBST[key]; nsub += 1
            fp.Add3DModel(m)
step_src = f'{WORK}/step_src.kicad_pcb'
sub_board.Save(step_src)
print('substituted models:', nsub)
subprocess.run(['kicad-cli', 'pcb', 'export', 'step', '--subst-models', '-f', '-o', step, step_src], env=ENV, capture_output=True)
import cascadio
cascadio.step_to_glb(step, f'{WORK}/board.glb', tol_linear=0.02, tol_angular=0.4)
src = trimesh.load(f'{WORK}/board.glb')


def to_world(v):
    v = v * 1000.0
    return np.column_stack([v[:, 0] - CX, v[:, 2], -v[:, 1] - CZ])


groups = collections.defaultdict(list)
boxes, brd = [], None
for node in src.graph.nodes_geometry:
    T, gname = src.graph[node]
    g = src.geometry[gname].copy(); g.apply_transform(T)
    mesh = trimesh.Trimesh(to_world(np.asarray(g.vertices)), np.asarray(g.faces), process=False)
    ext = mesh.bounds[1] - mesh.bounds[0]
    if ext[0] > 0.6 * BW and ext[2] > 0.6 * BH and ext[1] < 2.0:
        brd = mesh; continue
    vis = g.visual
    col = tuple(int(c) for c in (vis.material.baseColorFactor[:3] if hasattr(vis, 'material')
                                 and vis.material.baseColorFactor is not None else (128, 128, 128)))
    groups[col].append(mesh); boxes.append(mesh.bounds)


# procedural models for footprints without a usable KiCad model
def fp_frame(ref):
    fp = board.FindFootprintByReference(ref)
    x0, y0 = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
    th = math.radians(fp.GetOrientationDegrees())
    def f(lx, ly, z):
        X = x0 + lx * math.cos(th) + ly * math.sin(th); Y = y0 - lx * math.sin(th) + ly * math.cos(th)
        return (X - CX, z, Y - CZ)
    return f


def cuboid(f, lx0, lx1, ly0, ly1, z0, z1):
    b = trimesh.creation.box(bounds=[[lx0, ly0, z0], [lx1, ly1, z1]])
    v = np.array([f(*p) for p in b.vertices])
    m = trimesh.Trimesh(v, b.faces, process=False)
    if np.linalg.det(np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]])) < 0:   # (x,y,z)->(x,z,y) mirrors: flip winding
        m.invert()
    return m


def cylinder(f, lx, ly, z, r, length, axis='-y', sections=24):
    c = trimesh.creation.cylinder(radius=r, height=length, sections=sections)
    v = c.vertices.copy()                                  # axis along local z, centred
    if axis == '-y':
        loc = np.column_stack([lx + v[:, 0], ly - length / 2 + v[:, 2], z + v[:, 1]])
    else:
        loc = np.column_stack([lx + v[:, 0], ly + v[:, 1], z + length / 2 + v[:, 2]])
    m = trimesh.Trimesh(np.array([f(*p) for p in loc]), c.faces, process=False)
    if axis == '-y':
        m.invert(); m.invert()
    m.fix_normals()
    return m


BLACK, DARK, TIN, CERAMIC = (24, 24, 26), (12, 12, 13), (165, 163, 146), (111, 102, 81)
extra = collections.defaultdict(list)
if True:                       # procedural models (both boards)
    for fp in board.GetFootprints():
        name = fp.GetFPIDAsString()
        ref = fp.GetReference()
        f = fp_frame(ref)
        if re.search(r'TE_\d+-\d+_\d+P$', name):
            # right-angle Mazda ECU header (174917 / 176122 / 178780 family): housing on the board, shroud over
            # the board edge with one opening per plug. Sizes from the footprint's own pads and outline.
            o = fp.GetPosition()
            pads = [(p.GetNumber(), pcbnew.ToMM(p.GetPosition().x - o.x), pcbnew.ToMM(p.GetPosition().y - o.y))
                    for p in fp.Pads() if p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH]
            th = math.radians(fp.GetOrientationDegrees())
            loc = [(n, x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)) for n, x, y in pads]
            xs = [x for _, x, _ in loc]
            lx0, lx1 = min(xs) - 3.9, max(xs) + 3.9
            extra[BLACK] += [cuboid(f, lx0 - 4.4, lx1 + 4.4, -15.5, 1.8, 1.6, 14.6), cuboid(f, lx0, lx1, -25.5, -15.5, 2.6, 14.6)]
            for plug in sorted({n[0] for n, _, _ in loc if n}):
                px = [x for n, x, _ in loc if n and n[0] == plug]
                extra[DARK].append(cuboid(f, min(px) - 1.0, max(px) + 1.0, -25.62, -24.0, 4.4, 12.8))
            for n, lx, ly in loc:
                extra[TIN].append(cuboid(f, lx - 0.32, lx + 0.32, ly - 0.32, ly + 0.32, -3.0, 1.7))
        elif 'Micro-Fit_3.0' in name and name.endswith('Horizontal'):
            # right-angle Molex Micro-Fit (no 3D model in this KiCad install): housing = the footprint's Fab outline,
            # mating face (local -y) with one dark cavity per contact, pins through the board
            src = open(f'/usr/share/kicad/footprints/Connector_Molex.pretty/{name.split(":")[1]}.kicad_mod').read()
            fab = [tuple(map(float, m)) for m in re.findall(
                r'fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(layer "F.Fab"', src)]
            fx = [v for a, b, c, d in fab for v in (a, c)]; fy = [v for a, b, c, d in fab for v in (b, d)]
            pins = [(pcbnew.ToMM(p.GetPos0().x), pcbnew.ToMM(p.GetPos0().y))
                    for p in fp.Pads() if p.GetNumber()]
            mrows = sorted({round(y, 2) for _, y in pins}); mcols = sorted({round(x, 2) for x, _ in pins})
            hgt = 3.6 + 3.0 * len(mrows)
            x0, x1, y0, y1 = min(fx), max(fx), min(fy), max(fy)
            extra[BLACK].append(cuboid(f, x0, x1, y0, y1, 1.6, 1.6 + hgt))
            for k in range(len(mrows)):
                zc = 1.6 + 2.2 + 3.0 * (len(mrows) - 1 - k)
                for x in mcols:
                    extra[DARK].append(cuboid(f, x - 1.05, x + 1.05, y0 - 0.12, y0 + 0.6, zc - 1.05, zc + 1.05))
            for x, y in pins:
                extra[TIN].append(cuboid(f, x - 0.32, x + 0.32, y - 0.32, y + 0.32, -3.0, 1.7))
        elif name.endswith('Crystal_SMD_5032-2Pin_5.0x3.2mm'):
            # 5032 ceramic crystal: tan ceramic base, seam-welded metal lid
            extra[CERAMIC].append(cuboid(f, -2.5, 2.5, -1.6, 1.6, 1.6, 1.95))
            extra[TIN].append(cuboid(f, -2.3, 2.3, -1.4, 1.4, 1.95, 2.75))
        elif name.endswith('SW_Push_1P1T_XKB_TS-1187A'):
            # XKB TS-1187A 5.1 x 5.1 mm SMD tactile switch, 1.5 mm tall: black base, steel cover, round black plunger,
            # four gull-wing terminals out to the pads
            extra[BLACK].append(cuboid(f, -2.55, 2.55, -2.55, 2.55, 1.6, 2.5))
            extra[TIN].append(cuboid(f, -2.55, 2.55, -2.55, 2.55, 2.5, 2.7))
            extra[BLACK].append(cylinder(f, 0, 0, 2.7, 1.25, 0.4, axis='z'))
            for p in fp.Pads():
                px, py = pcbnew.ToMM(p.GetPos0().x), pcbnew.ToMM(p.GetPos0().y)
                x0, x1 = sorted((px, px * 0.85))
                extra[TIN].append(cuboid(f, x0 - 0.35, x1 + 0.35, py - 0.35, py + 0.35, 1.6, 1.75))
        elif name.endswith('MPX5700_867C_Flat'):
            # 867C dual side-port body lying flat, the two barbs out of the edge opposite the leads
            extra[BLACK].append(cuboid(f, -14.95, 14.95, -5.3, 12.9, 1.6, 9.2))
            for lx in (-4.6, 4.6):
                extra[BLACK].append(cylinder(f, lx, -5.3, 5.4, 3.1, 2.5))
                extra[BLACK].append(cylinder(f, lx, -7.8, 5.4, 2.0, 8.5))
                extra[BLACK].append(cylinder(f, lx, -12.0, 5.4, 2.45, 1.6))
            for k in range(6):
                lx = -6.35 + 2.54 * k
                extra[TIN].append(cuboid(f, lx - 0.25, lx + 0.25, 12.9, 16.8, 2.4, 2.65))
                extra[TIN].append(cuboid(f, lx - 0.25, lx + 0.25, 16.3, 16.8, -2.0, 2.65))
        elif name.endswith('MPX5700AP_867B_Flat'):
            # 867B unibody lying flat, marking up (same geometry as scripts/mk_map_fp.py): a 3.2 mm flange in the
            # lozenge outline with the two mounting holes, the full-height lozenge body between them, one barb leaving the far edge
            # 4 mm toward pin 6, six leads bent 90 deg down into the board
            from shapely.geometry import Point as SP
            from shapely.ops import unary_union as SU
            YC, HX, PX = 3.81, 23.11 / 2, 4.0
            hull = SU([SP(0, YC).buffer(8.85, 64), SP(-HX, YC).buffer(3.3, 32), SP(HX, YC).buffer(3.3, 32)]).convex_hull
            flange = hull.difference(SP(-HX, YC).buffer(2.0, 32)).difference(SP(HX, YC).buffer(2.0, 32))
            from shapely.geometry import box as SB
            boss = hull.intersection(SB(-HX + 3.0, -20, HX - 3.0, 20)).buffer(-0.3).buffer(0.3)

            def slab(poly, z0, z1):
                m = trimesh.creation.extrude_polygon(poly, z1 - z0)
                v = np.array([f(x, y, z + z0) for x, y, z in m.vertices])
                m = trimesh.Trimesh(v, m.faces, process=False); m.fix_normals(); m.unmerge_vertices(); return m   # crisp edges
            extra[BLACK] += [slab(flange, 1.6, 4.2), slab(boss, 4.2, 8.4)]
            # barb: profile (radius, distance beyond the body edge), revolved about the port axis
            edge = YC - (8.85 ** 2 - PX ** 2) ** 0.5
            prof = [(0, -1.0), (2.0, -1.0), (2.0, 1.0), (1.65, 1.0), (1.65, 4.5), (2.3, 4.5), (1.7, 11.0), (0, 11.0)]
            rv = trimesh.creation.revolve([(r, t) for r, t in prof], sections=32)
            zc = 5.0
            v = np.array([f(PX + x, edge - t, zc + y) for x, y, t in rv.vertices])
            rv = trimesh.Trimesh(v, rv.faces, process=False); rv.fix_normals()
            extra[BLACK].append(rv)
            for k in range(6):
                lx = -6.35 + 2.54 * k
                extra[TIN].append(cuboid(f, lx - 0.4, lx + 0.4, 12.0, 16.8, 3.0, 3.3))
                extra[TIN].append(cuboid(f, lx - 0.25, lx + 0.25, 16.3, 16.8, -2.0, 3.3))
for col, ms in extra.items():
    for m in ms:
        groups[col].append(m); boxes.append(m.bounds)

scene = trimesh.Scene()
METAL = {(165, 163, 146), (164, 163, 146), (198, 196, 160), (181, 129, 54), (111, 101, 80), (111, 102, 81)}
for col, ms in groups.items():
    m = trimesh.util.concatenate(ms)
    metal = col in METAL
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=list(col) + [255], metallicFactor=0.85 if metal else 0.0,
        roughnessFactor=0.35 if metal else 0.6, doubleSided=False))
    scene.add_geometry(m, geom_name=f'parts_{col[0]}_{col[1]}_{col[2]}')
if brd is not None:
    brd.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=[29, 79, 51, 255], metallicFactor=0.0, roughnessFactor=0.7))
    scene.add_geometry(brd, geom_name='board')
scene.export(f'{WORK}/merged.glb', include_normals=True)
subprocess.run([GLTFPACK, '-i', f'{WORK}/merged.glb', '-o', f'{WORK}/q.glb'], check=True, capture_output=True)
import gzip, base64
open(f'{OUT}/{PRE}board.glb.gz.b64.txt', 'w').write(base64.b64encode(gzip.compress(open(f'{WORK}/q.glb', 'rb').read(), 9)).decode())

# pick boxes: union of meshes whose centre falls in the footprint rectangle
cent = np.array([(b[0] + b[1]) / 2 for b in boxes])
for p in rows:
    ax, az = p['x0'] + ox - CX, p['y0'] + oy - CZ
    bx, bz = p['x1'] + ox - CX, p['y1'] + oy - CZ
    lo = np.array([ax, 1.6, az]); hi = np.array([bx, 1.8, bz])
    ins = (cent[:, 0] >= ax) & (cent[:, 0] <= bx) & (cent[:, 2] >= az) & (cent[:, 2] <= bz)
    for i in np.nonzero(ins)[0]:
        lo = np.minimum(lo, boxes[i][0]); hi = np.maximum(hi, boxes[i][1])
    hi[1] = max(hi[1], 1.8)
    p['box'] = [round(float(x), 3) for x in (*lo, *hi)]
json.dump(dict(size=[round(BW, 4), round(BH, 4)], centre=[round(CX - 100, 4), round(CZ - 50, 4)], parts=rows),
          open(f'{OUT}/{PRE}parts.json', 'w'), separators=(',', ':'))
print('parts', len(rows), 'meshes', len(boxes), 'groups', len(groups), 'board mesh', brd is not None)
