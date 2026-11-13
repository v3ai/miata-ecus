#!/usr/bin/env python3
"""Steady-state temperature map of the daughterboard from its real copper.

Earlier revisions estimated every hot part on its own from a single-sided copper-area curve. That curve knows nothing
of the planes, of the copper on the other layers, or of the neighbours heating the same board. This model does:

  - every copper layer is rasterised from the board file (0.5 mm cells) into a sheet whose conductance follows its
    copper cover (385 W/m K, 35 um outside, 15.2 um inside: JLCPCB's figures) plus the laminate (0.5 W/m K in plane);
  - adjacent layers are joined through the laminate between them (0.3 W/m K across; JLCPCB's standard six-layer
    stack, recalled: 0.10 / 0.55 / 0.11 / 0.55 / 0.10 mm) and through every via barrel and plated hole (18 um
    plating), counted only between layers where its net really has copper;
  - the two faces lose heat to the air at h W/m2 K (natural convection plus radiation; 10 by default, 6 for a
    board boxed in above another board). Part bodies are not counted as cooling surface. The header pins are left
    out by default (the pessimistic figure); --pins adds them as a path into the motherboard (an estimate);
  - each part's loss goes into the cells under the pads that carry its heat (the tab of a DPAK or SOT-223, the
    exposed pad of the regulators, both leads of a diode); its junction is the mean temperature of those cells plus
    loss times the maker's junction-to-case or junction-to-lead resistance.

Result: the rise above the air around the board, per part and as a map. It is an estimate, not a measurement: the
air inside an ECU case is warmer than the cabin, and h is not known to better than a factor of 1.5.

Self-test (--selftest): a DPAK-sized source on 1 square inch of 1 oz copper on bare two-sided FR4, the classic
datasheet figure (about 40-50 C/W junction to ambient, as recalled from several makers' DPAK sheets; not re-read), to
show what the chosen h gives.

As a module: Model(board, h, pins).rise({ref: watts}) -> {ref: (watts, pad rise, junction rise)}.

usage: /usr/bin/python3 firmware/tools/board_thermal.py [board.kicad_pcb] [--h 10] [--pins] [--case seq,batch]
                                                        [--png out.png] [--selftest]
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CELL = 0.5e-3
K_CU, K_FR4_XY, K_FR4_Z = 385.0, 0.5, 0.3
T_OUT, T_IN = 35e-6, 15.2e-6
STACK6 = [0.0994e-3, 0.55e-3, 0.1088e-3, 0.55e-3, 0.0994e-3]          # dielectric between consecutive copper layers
STACK4 = [0.2104e-3, 1.065e-3, 0.2104e-3]                             # JLCPCB's standard four-layer stack (recalled)
VIA_PLATE = 18e-6
# Header pins (--pins): 0.64 mm square brass, about 9 mm from board to board through the socket contact: 5 mW/K as a
# bar, taken as 3 mW/K with the contact (assumed). The motherboard is one node: both faces of 154 x 162 mm at h, times
# 0.35 because a two-layer board fed along two rows of pins is far from isothermal (assumed).
G_PIN, MB_AREA, MB_FIN = 3e-3, 2 * 0.154 * 0.1616, 0.35

# junction to case / lead, C/W (maker's figures; the ones marked "read" are in research/rev0.10_design_audit.md)
RTH_J = {'VND7NV04TR-E': 2.1, 'VND14NV04': 1.8, 'SMCJ14A': 15.0, 'TPSMC16A': 15.0, 'ES1D': 20.0, 'SMCJ30A': 15.0,
         'LDL1117S33R': 15.0, 'LMR14020': 6.0, 'TLS115B0EJ': 10.0, 'SS34': 20.0, 'B360A': 15.0,
         'STM32F407VGT6': 20.0, 'ZXMS6004FFTA': 60.0}
# pads that carry the heat out of a part (default: all pads)
HEAT_PADS = {'VND7NV04TR-E': ('2',), 'VND14NV04': ('2',), 'LDL1117S33R': ('2',), 'LMR14020': ('9',),
             'TLS115B0EJ': ('9',), 'ZXMS6004FFTA': ('3',)}


def losses(case, l_mh=20.0, rpm=7200):
    """{ref: watts} at sustained high load. case: 'seq' sequential injection; 'batch' the 1989-93 wiring with the four
    clamp TVSs sharing equally; 'batch_hog' the same with one TVS of each pair taking both injectors' energy;
    'rev09' the rev 0.9 board, where each injector driver's own clamp takes the energy (sequential).
    Clamp energy per shot from sim_inj_clamp.py: 8.3 mJ per injector at 20 mH into a battery-referred TVS, 15.3 mJ
    into a driver's own clamp; both scale with the inductance."""
    e_tvs, e_drv = 8.3e-3 * l_mh / 20.0, 15.3e-3 * l_mh / 20.0
    p = {}
    for q in ('Q1', 'Q2', 'Q3', 'Q4'):
        p[q] = 1.2 ** 2 * 0.12 * 0.8                    # 1.2 A, 120 mOhm hot, 80 % duty
        if case == 'rev09':
            p[q] += e_drv * rpm / 120
    p.update({'Q5': 1.3 ** 2 * 0.12 * 0.6, 'Q6': 1.9 ** 2 * 0.12 * 0.6, 'Q7': 0.5 ** 2 * 0.12 * 0.5})
    seq, bat = e_tvs * rpm / 120, e_tvs * rpm / 60
    tvs = {'seq': [seq] * 4, 'batch': [bat] * 4, 'batch_hog': [2 * bat, 2 * bat, 0.0, 0.0], 'rev09': [0.0] * 4}[case]
    for i, w in enumerate(tvs):
        p[f'D{46 + i}'] = w
        p[f'D{42 + i}'] = 0.06 * w                      # clamp diode: 0.9 V of the 16 V clamp
    p.update({'U4': (5.0 - 3.3) * 0.25, 'U2': 0.30, 'D9': 0.15, 'L2': 0.05, 'U1': 0.33, 'U3': (13.5 - 5.0) * 0.035,
              'U14': (13.5 - 5.0) * 0.05, 'D7': 0.4 * 0.35, 'U102': 0.10, 'Q101': 1.0 ** 2 * 0.07 * 0.6,
              'U10': 0.10, 'U106': 0.10, 'U11': 0.05, 'U6': 0.05, 'U7': 0.05})
    for q in range(9, 16):
        p[f'Q{q}'] = 0.25 ** 2 * 0.6                    # relay / lamp low sides: 0.25 A, 0.6 ohm
    return p


def raster(board_path, layer, nx, ny):
    """copper cover (0..1) of one layer per cell, [ny, nx]"""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    with tempfile.TemporaryDirectory() as td:
        svg, png = os.path.join(td, 'l.svg'), os.path.join(td, 'l.png')
        subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--exclude-drawing-sheet', '--page-size-mode', '2',
                        '--black-and-white', '-l', f'{layer},Edge.Cuts', '-o', svg, board_path],
                       check=True, capture_output=True)
        sub = 4
        subprocess.run(['rsvg-convert', '-w', str(nx * sub), '-h', str(ny * sub), '-b', 'white', svg, '-o', png],
                       check=True, capture_output=True)
        a = 1.0 - np.asarray(Image.open(png).convert('L'), dtype=float) / 255.0
    a = a[:ny * sub, :nx * sub].reshape(ny, sub, nx, sub).mean(axis=(1, 3))
    a[:1, :] = a[-1:, :] = 0; a[:, :1] = a[:, -1:] = 0          # the outline itself is not copper
    return a


def assemble(cover, thick, stack, vias, h_top, h_bot, pins=None, g_pin=0.0, g_mb=0.0):
    """Conductance matrix. cover: [nl, ny, nx] copper fraction; thick: copper thickness per layer; stack: dielectric
    between layers; vias: [(iy, ix, [connected layer indexes], hole diameter)]; pins: [(iy, ix)] header pins, each
    joined by g_pin (W/K) to one extra node, the motherboard, which loses g_mb (W/K) to the air."""
    nl, ny, nx = cover.shape
    n = nl * ny * nx
    idx = np.arange(n).reshape(nl, ny, nx)
    total = sum(stack)
    rows, cols, vals = [], [], []
    diag = np.zeros(n + 1)

    def link(a, b, g):
        a, b = np.ravel(a), np.ravel(b)
        g = np.ravel(g) if np.ndim(g) else np.full(a.size, float(g))
        rows.extend([a, b]); cols.extend([b, a]); vals.extend([-g, -g])
        np.add.at(diag, a, g); np.add.at(diag, b, g)

    for L in range(nl):
        s = cover[L] * K_CU * thick[L] + K_FR4_XY * total / nl      # each sheet carries its share of the laminate
        link(idx[L][:, :-1], idx[L][:, 1:], 2 * s[:, :-1] * s[:, 1:] / (s[:, :-1] + s[:, 1:]))
        link(idx[L][:-1, :], idx[L][1:, :], 2 * s[:-1, :] * s[1:, :] / (s[:-1, :] + s[1:, :]))
        if L + 1 < nl:
            link(idx[L], idx[L + 1], K_FR4_Z * CELL * CELL / stack[L])
    z = np.concatenate([[0.0], np.cumsum(stack)])
    for iy, ix, layers, hole in vias:
        for la, lb in zip(layers, layers[1:]):
            link([idx[la, iy, ix]], [idx[lb, iy, ix]], K_CU * math.pi * hole * VIA_PLATE / (z[lb] - z[la]))
    diag[idx[0].ravel()] += h_top * CELL * CELL
    diag[idx[-1].ravel()] += h_bot * CELL * CELL
    diag[n] += max(g_mb, 1e-9)
    for iy, ix in (pins or []):
        link([idx[-1, iy, ix]], [n], g_pin)                          # the pin is soldered on the bottom face
    m = sp.coo_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(n + 1)]),
                                                        np.concatenate(cols + [np.arange(n + 1)]))),
                      shape=(n + 1, n + 1)).tocsc()
    return m


def selftest(h):
    nx = ny = 160                                                    # 80 x 80 mm
    cover = np.zeros((2, ny, nx))
    c = nx // 2
    half = int(round(12.7e-3 / CELL))
    cover[0, c - half:c + half, c - half:c + half] = 1.0             # 1 square inch on top
    src = np.zeros(cover.size + 1)
    s = int(round(3e-3 / CELL))
    sv = src[:-1].reshape(cover.shape)
    sv[0, c - s:c + s, c - s:c + s] = 1.0 / (2 * s) ** 2             # 1 W over 6 x 6 mm
    t = spl.spsolve(assemble(cover, [T_OUT, T_OUT], [1.5e-3], [], h, h), src)[:-1].reshape(cover.shape)
    return float(t[0, c - s:c + s, c - s:c + s].mean())


class Model:
    def __init__(self, board_path, h=10.0, pins=False):
        import pcbnew
        sys.path.insert(0, os.path.join(ROOT, 'scripts'))
        cwd = os.getcwd(); os.chdir(os.path.join(ROOT, 'scripts'))
        import design
        os.chdir(cwd)
        self.h, self.with_pins = h, pins
        b = pcbnew.LoadBoard(board_path)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        bb = b.GetBoardEdgesBoundingBox()
        x0, y0 = pcbnew.ToMM(bb.GetLeft()) * 1e-3, pcbnew.ToMM(bb.GetTop()) * 1e-3
        nx = int(round(pcbnew.ToMM(bb.GetWidth()) * 1e-3 / CELL))
        ny = int(round(pcbnew.ToMM(bb.GetHeight()) * 1e-3 / CELL))
        ncu = b.GetCopperLayerCount()
        ids = [pcbnew.F_Cu] + [getattr(pcbnew, f'In{i}_Cu') for i in range(1, ncu - 1)] + [pcbnew.B_Cu]
        with tempfile.TemporaryDirectory() as td:
            filled = os.path.join(td, 'filled.kicad_pcb')
            b.Save(filled)
            self.cover = np.array([raster(filled, b.GetLayerName(i), nx, ny) for i in ids])
        self.layers = ncu
        thick = [T_OUT] + [T_IN] * (ncu - 2) + [T_OUT]
        stack = STACK6 if ncu == 6 else STACK4 if ncu == 4 else [1.5e-3]

        def cell(p):
            return (min(ny - 1, max(0, int((pcbnew.ToMM(p.y) * 1e-3 - y0) / CELL))),
                    min(nx - 1, max(0, int((pcbnew.ToMM(p.x) * 1e-3 - x0) / CELL))))
        # a via or plated hole joins the layers where its net has copper (a pour or a track end)
        ends, zones = {}, {}
        for t in b.GetTracks():
            if t.GetClass() != 'PCB_VIA':
                for q in (t.GetStart(), t.GetEnd()):
                    ends.setdefault((t.GetNetCode(), t.GetLayer()), []).append((q.x, q.y))
        ends = {k: np.array(v, dtype=float) for k, v in ends.items()}
        for z in b.Zones():
            for L in z.GetLayerSet().Seq():
                zones.setdefault((z.GetNetCode(), L), []).append(z)

        def joined(pos, nc, r, always=()):
            out = []
            for li, L in enumerate(ids):
                hit = li in always or any(z.HitTestFilledArea(L, pos, 0) for z in zones.get((nc, L), []))
                if not hit and (nc, L) in ends:
                    e = ends[(nc, L)]
                    hit = bool(np.any((e[:, 0] - pos.x) ** 2 + (e[:, 1] - pos.y) ** 2 < float(r) ** 2))
                if hit:
                    out.append(li)
            return out
        vias, pin_cells = [], []
        for t in b.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                conn = joined(t.GetPosition(), t.GetNetCode(), t.GetWidth() / 2)
                if len(conn) >= 2:
                    vias.append(cell(t.GetPosition()) + (conn, pcbnew.ToMM(t.GetDrill()) * 1e-3))
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetDrillSize().x <= 0 or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    continue
                conn = joined(p.GetPosition(), p.GetNetCode(), p.GetSize().x / 2, always=(0, len(ids) - 1))
                vias.append(cell(p.GetPosition()) + (conn, pcbnew.ToMM(p.GetDrillSize().x) * 1e-3))
                if fp.GetReference() in ('J1', 'J2'):
                    pin_cells.append(cell(p.GetPosition()))
        self.n_pins, self.n_vias = len(pin_cells), len(vias)
        m = assemble(self.cover, thick, stack, vias, h, h, pin_cells if pins else None, G_PIN, h * MB_AREA * MB_FIN)
        self.lu = spl.splu(m)
        # where each part's heat goes in
        by_ref = {p['ref']: p for p in design.parts}
        self.cells, self.value = {}, {}
        for fp in b.GetFootprints():
            ref = fp.GetReference()
            val = by_ref.get(ref, {}).get('value', fp.GetValue())
            want = HEAT_PADS.get(val)
            li = 0 if fp.GetLayer() == pcbnew.F_Cu else len(ids) - 1
            cl = set()
            for p in fp.Pads():
                if want and p.GetNumber() not in want:
                    continue
                bp = p.GetBoundingBox()
                (j0, i0) = cell(pcbnew.VECTOR2I(bp.GetLeft(), bp.GetTop()))
                (j1, i1) = cell(pcbnew.VECTOR2I(bp.GetRight(), bp.GetBottom()))
                cl |= {(j, i) for j in range(j0, j1 + 1) for i in range(i0, i1 + 1)}
            if cl:
                self.cells[ref] = (li, sorted(cl))
                self.value[ref] = val

    def rise(self, watts):
        """{ref: W} -> {ref: (W, mean rise of its heat pads, junction rise)}; .map (top layer), .mb, .mean, .peak"""
        src = np.zeros(self.cover.size + 1)
        sv = src[:-1].reshape(self.cover.shape)
        for ref, w in watts.items():
            if ref in self.cells and w > 0:
                li, cl = self.cells[ref]
                for j, i in cl:
                    sv[li, j, i] += w / len(cl)
        t = self.lu.solve(src)
        self.mb = float(t[-1])
        tt = t[:-1].reshape(self.cover.shape)
        self.map, self.mean, self.peak = tt[0], float(tt[0].mean()), float(tt.max())
        out = {}
        for ref, (li, cl) in self.cells.items():
            w = watts.get(ref, 0.0)
            tb = float(np.mean([tt[li, j, i] for j, i in cl]))
            out[ref] = (w, tb, tb + w * RTH_J.get(self.value[ref], 0.0))
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board', nargs='?', default=os.path.join(ROOT, 'daughterboard', 'miata_ecu_daughter.kicad_pcb'))
    ap.add_argument('--h', type=float, default=10.0)
    ap.add_argument('--case', default='seq,batch,batch_hog')
    ap.add_argument('--mh', type=float, default=20.0, help='injector inductance, mH')
    ap.add_argument('--png')
    ap.add_argument('--pins', action='store_true', help='count the header pins as a path into the motherboard')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        for h in (6.0, 10.0, 15.0):
            print(f'self-test, h = {h:.0f} W/m2K: a 6 x 6 mm source on 1 square inch of 1 oz copper, bare two-sided '
                  f'FR4: {selftest(h):.0f} C/W to the air')
        return 0
    m = Model(a.board, a.h, a.pins)
    print(f'{a.board}: {m.layers} copper layers, {m.n_vias} vias and plated holes, h = {a.h:.0f} W/m2K, '
          + (f'{m.n_pins} header pins into the motherboard' if a.pins else 'no heat through the header pins')
          + f', injectors {a.mh:.0f} mH, 7200 rpm')
    for case in a.case.split(','):
        pw = losses(case, a.mh)
        res = m.rise(pw)
        print(f'\ncase {case}: {sum(pw.values()):.1f} W on the board; board mean rise {m.mean:.0f} C, hottest copper '
              f'{m.peak:.0f} C above the air' + (f'; motherboard {m.mb:.0f} C' if a.pins else ''))
        for grp, refs in (('injector drivers', ['Q1', 'Q2', 'Q3', 'Q4']), ('valve drivers', ['Q5', 'Q6', 'Q7']),
                          ('clamp TVSs', [f'D{46 + i}' for i in range(4)]),
                          ('regulators', ['U4', 'U2', 'U3', 'U14']), ('processor', ['U1'])):
            rr = [(r,) + res[r] for r in refs if r in res and res[r][0] > 0]
            if rr:
                print(f'  {grp:17s}' + '; '.join(f'{r} {w:.2f} W: pads +{tb:.0f}, junction +{tj:.0f} C' for r, w, tb, tj in rr))
        if a.png:
            from PIL import Image
            v = m.map / max(1e-9, m.peak)
            img = np.zeros(v.shape + (3,), dtype=np.uint8)
            img[..., 0] = (255 * np.clip(v * 2, 0, 1)).astype(np.uint8)
            img[..., 1] = (255 * np.clip(2 - v * 2, 0, 1) * np.clip(v * 4, 0.15, 1)).astype(np.uint8)
            img[..., 2] = (255 * np.clip(1 - v * 2, 0, 1)).astype(np.uint8)
            Image.fromarray(img).resize((v.shape[1] * 4, v.shape[0] * 4), Image.NEAREST).save(
                a.png.replace('.png', f'_{case}.png'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
