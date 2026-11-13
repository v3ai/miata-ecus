#!/usr/bin/env python3
"""Track width against the current each piece of track really carries, layer by layer (daughterboard rev 0.10).

JLCPCB's standard six-layer board has 1 oz copper outside (35 um finished) and 0.5 oz inside (15.2 um in its stack-up
table), so the same width carries less on an inner layer. For each net that carries real current this

  1. builds a resistor network from the board file: every track segment (split where another track, a via or a pad
     meets it), every via (1 mOhm), every pad; a filled copper pour of the net joins whatever it touches (it is far
     wider than a track, so it is taken as a perfect conductor);
  2. feeds in the load cases below (current into the net at one pad, out at another) and solves for the current in
     every segment; cases on one net that happen at different times add as rms;
  3. works out each segment's temperature rise by IPC-2221 (I = k dT^0.44 A^0.725, A in square mils, k = 0.048 on an
     outer layer and 0.024 inside) from its width and its layer's copper thickness.

IPC-2221 is the older, conservative rule: it ignores the planes next to a track and the heat that runs along a short
segment into its vias and pads. Up to 10 C is OK, up to 20 C a CHECK, more a FAIL. A load whose pad the tracks do not
reach in this model (joined only through something not modelled) is reported as a CHECK, never passed silently.

Load cases (sustained worst cases; the sources are in research/rev0.10_design_audit.md and the circuit simulation):
  injector outputs   14.4 V / 12 ohm at 100 % duty: 1.2 A from the header pin to the driver; and the turn-off decay,
                     0.2 A rms at 7200 rpm in batch mode with 20 mH, from the header pin into the clamp diode
  clamp return       0.2 A rms from each clamp TVS back to the battery pins, the two injectors of a pair together
  idle valve 1.3 A (11 ohm), VVT valve 2.0 A (7 ohm, 100 % duty), boost valve 0.6 A
  logic supply       F1's 1.1 A hold current from the battery pins through D7, F1 and L1 into the buck converter (the
                     board draws 0.15-0.6 A), with 0.15 A to each tracking regulator
  +5 V               0.35 A to the 3.3 V regulator, 70 mA per CAN transceiver, 20-30 mA per driver or level shifter
  USB                0.5 A from the USB pin through D10 to the 3.3 V regulator (bench power, instead of the buck)
  sensor supplies    the TLS115's 150 mA each
  wideband heater    2 A rms through the heater switch (1 A once hot; the warm-up ramp is higher for seconds)
  relay, lamp and spare low-side outputs: 0.5 A; tach and ignition drive 0.05 A

usage: /usr/bin/python3 scripts/track_current.py board.kicad_pcb [--all]
Exits 1 on a FAIL.
"""
import collections
import math
import os
import sys
import numpy as np
import pcbnew
from pcbnew import ToMM

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_cwd = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402
os.chdir(_cwd)

OUTER_UM, INNER_UM = 35.0, 15.2
RHO = 1.72e-8 * 1.25            # ohm m, copper at about 85 C
R_VIA = 1e-3


def pads_on(net):
    return [(p['ref'], str(k)) for p in design.parts for k, v in p['pads'].items() if v == net]


def cases():
    """[(net, case name, {(ref, pad): amps into the net})]"""
    out = []
    for i in range(4):
        n = f'OUT_INJ{i + 1}'
        hdr = [pp for pp in pads_on(n) if pp[0].startswith('J')][0]
        out.append((n, 'injector on', {hdr: 1.2, (f'Q{i + 1}', '2'): -1.2}))
        out.append((n, 'turn-off decay', {hdr: 0.2, (f'D{42 + i}', '2'): -0.2}))
        out.append((f'INJ{i + 1}_CL', 'turn-off decay', {(f'D{42 + i}', '1'): 0.2, (f'D{46 + i}', '1'): -0.2}))
    out.append(('VBAT_IN', 'logic supply', {('J1', '1'): 0.55, ('J1', '2'): 0.55, ('D7', '2'): -1.1}))
    # batch mode is the worst case: the two injectors of a pair (1+4, 2+3) decay together, the pairs take turns
    for pair in ((46, 49), (47, 48)):
        out.append(('VBAT_IN', f'clamp return D{pair[0]}+D{pair[1]}',
                    {(f'D{pair[0]}', '2'): 0.2, (f'D{pair[1]}', '2'): 0.2, ('J1', '1'): -0.2, ('J1', '2'): -0.2}))
    for n, q, a in (('OUT_IACV', 'Q5', 1.3), ('OUT_VVT', 'Q6', 2.0), ('OUT_BOOST', 'Q7', 0.6)):
        hdr = [pp for pp in pads_on(n) if pp[0].startswith('J')][0]
        out.append((n, 'valve on', {hdr: a, (q, '2'): -a}))
    out.append(('+12V_IN', 'logic supply', {('D7', '1'): 1.1, ('F1', '1'): -1.1}))
    out.append(('+12V', 'logic supply', {('F1', '2'): 1.1, ('L1', '1'): -0.8, ('U3', '8'): -0.15, ('U14', '8'): -0.15}))
    out.append(('+12V_F', 'logic supply', {('L1', '2'): 1.1, ('U2', '2'): -0.55, ('U2', '3'): -0.55}))
    out.append(('BUCK_SW', 'buck', {('U2', '8'): 1.0, ('L2', '1'): -1.0}))
    five = {('U4', '3'): -0.35, ('U11', '1'): -0.02, ('U12', '1'): -0.02, ('U6', '6'): -0.03, ('U7', '6'): -0.03,
            ('U13', '14'): -0.01, ('U9', '8'): -0.01, ('U10', '3'): -0.07, ('U106', '3'): -0.07, ('U103', '1'): -0.03}
    out.append(('+5V', 'from the buck', {**five, ('L2', '2'): -sum(five.values())}))
    out.append(('+5V', 'ALT from USB', {('D10', '1'): 0.5, ('U4', '3'): -0.5}))       # instead of the buck, not with it
    out.append(('USB_VBUS', 'from USB', {[pp for pp in pads_on('USB_VBUS') if pp[0].startswith('J')][0]: 0.5,
                                         ('D10', '2'): -0.5}))
    out.append(('V5_EXT', 'sensor supply', {('U14', '1'): 0.15,
                                            [pp for pp in pads_on('V5_EXT') if pp[0].startswith('J')][0]: -0.15}))
    out.append(('V5_SENS', 'sensor supply', {('U3', '1'): 0.15,
                                             [pp for pp in pads_on('V5_SENS') if pp[0].startswith('J')][0]: -0.15}))
    # wideband heater: 7.5 W at 7.5 V effective is 1 A rms once hot; 2 A covers the warm-up ramp (bound, assumed)
    out.append(('LSU_HTR_N', 'heater', {('J2', '37'): 1.0, ('J2', '38'): 1.0, ('Q101', '2'): -2.0}))
    out.append(('HTR_GND', 'heater', {('Q101', '3'): 2.0, ('J2', '39'): -1.0, ('J2', '40'): -1.0}))
    done = {c[0] for c in out}
    for net in sorted({v for p in design.parts for v in p['pads'].values() if v.startswith('OUT_')} - done):
        pp = pads_on(net)
        hdr = [x for x in pp if x[0].startswith('J')]
        drv = [x for x in pp if x[0].startswith('Q')]
        if hdr and drv:
            a = 0.05 if net.startswith(('OUT_IGN', 'OUT_TACH', 'OUT_ALT')) else 0.5
            out.append((net, 'output on', {hdr[0]: a, drv[0]: -a}))
    return out


def rise(amps, width_mm, um, inner):
    area = (width_mm / 0.0254) * (um / 25.4)          # square mils
    k = 0.024 if inner else 0.048
    return (abs(amps) / (k * area ** 0.725)) ** (1 / 0.44)


class Net:
    """resistor network of one net's copper"""

    def __init__(self, board, name):
        self.b, self.name = board, name
        self.six = board.GetCopperLayerCount() >= 6
        self.parent = {}
        segs = []                                     # (layer id, (x0, y0), (x1, y1), width)
        vias = []
        for t in board.GetTracks():
            if t.GetNetname() != name:
                continue
            if t.GetClass() == 'PCB_VIA':
                vias.append((ToMM(t.GetPosition().x), ToMM(t.GetPosition().y), ToMM(t.GetWidth()) / 2))
            else:
                segs.append((t.GetLayer(), (ToMM(t.GetStart().x), ToMM(t.GetStart().y)),
                             (ToMM(t.GetEnd().x), ToMM(t.GetEnd().y)), ToMM(t.GetWidth())))
        self.pads = {}
        for fp in board.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname() == name:
                    self.pads.setdefault((fp.GetReference(), p.GetNumber()), []).append(p)
        zones = [z for z in board.Zones() if z.GetNetname() == name and z.IsFilled()]
        # split every segment where something meets it
        pts_by_layer = collections.defaultdict(list)
        for L, a, b_, w in segs:
            pts_by_layer[L] += [a, b_]
        self.edges = []                               # (node a, node b, layer, width, length mm)
        for L, a, b_, w in segs:
            cand = list(pts_by_layer[L]) + [(x, y) for x, y, r in vias]
            cand += [(ToMM(p.GetPosition().x), ToMM(p.GetPosition().y)) for pl in self.pads.values() for p in pl]
            dx, dy = b_[0] - a[0], b_[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 1e-6:
                continue
            ts = {0.0, 1.0}
            for (x, y) in cand:
                t = ((x - a[0]) * dx + (y - a[1]) * dy) / (ln * ln)
                if 0.0 < t < 1.0 and math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) < 0.02:
                    ts.add(round(t, 6))
            ts = sorted(ts)
            for t0, t1 in zip(ts, ts[1:]):
                p0 = (round(a[0] + t0 * dx, 3), round(a[1] + t0 * dy, 3))
                p1 = (round(a[0] + t1 * dx, 3), round(a[1] + t1 * dy, 3))
                self.edges.append((('pt', L, p0), ('pt', L, p1), L, w, (t1 - t0) * ln))
        nodes = {n for e in self.edges for n in e[:2]}
        # vias join the layers at their position
        self.res = []                                 # extra resistors (a, b, ohm)
        for k, (x, y, r) in enumerate(vias):
            vn = ('via', k)
            nodes.add(vn)
            for n in list(nodes):
                if n[0] == 'pt' and math.hypot(n[2][0] - x, n[2][1] - y) < r:
                    self.res.append((vn, n, R_VIA))
        # pads: every track point and via inside the pad
        for key, pl in self.pads.items():
            pn = ('pad',) + key
            nodes.add(pn)
            for p in pl:
                for n in list(nodes):
                    if n[0] == 'pt' and p.IsOnLayer(n[1]) and p.HitTest(pcbnew.VECTOR2I(pcbnew.FromMM(n[2][0]), pcbnew.FromMM(n[2][1])), pcbnew.FromMM(0.02)):
                        self.union(pn, n)
                for k, (x, y, r) in enumerate(vias):
                    if p.HitTest(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)), pcbnew.FromMM(r)):
                        self.union(pn, ('via', k))
        # pours: a perfect conductor joining what lies in its filled copper
        for zi, z in enumerate(zones):
            zn = ('zone', zi)
            for L in z.GetLayerSet().Seq():
                def inside(x, y):
                    return z.HitTestFilledArea(L, pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)), 0)
                for n in list(nodes):
                    if n[0] == 'pt' and n[1] == L and inside(*n[2]):
                        self.union(zn, n)
                for k, (x, y, r) in enumerate(vias):
                    if inside(x, y):
                        self.union(zn, ('via', k))
                for key, pl in self.pads.items():
                    for p in pl:
                        if p.IsOnLayer(L) and inside(ToMM(p.GetPosition().x), ToMM(p.GetPosition().y)):
                            self.union(zn, ('pad',) + key)
        self.n_zones = len(zones)

    def find(self, a):
        self.parent.setdefault(a, a)
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def solve(self, inject):
        """{(ref, pad): amps} -> ([(edge, amps)], [pads not reached])"""
        idx = {}

        def nid(n):
            return idx.setdefault(self.find(n), len(idx))
        cond = []
        for a, b_, L, w, ln in self.edges:
            um = INNER_UM if (self.six and self.b.GetLayerName(L).startswith('In')) else OUTER_UM
            r = RHO * (ln * 1e-3) / (w * 1e-3 * um * 1e-6)
            cond.append((nid(a), nid(b_), 1.0 / max(r, 1e-7)))
        for a, b_, r in self.res:
            cond.append((nid(a), nid(b_), 1.0 / r))
        missing = [k for k in inject if k not in self.pads]
        src = {nid(('pad',) + k): 0.0 for k in inject if k in self.pads}
        for k, a in inject.items():
            if k in self.pads:
                src[nid(('pad',) + k)] += a
        n = len(idx)
        g = np.zeros((n, n))
        for a, b_, c in cond:
            if a != b_:
                g[a, a] += c; g[b_, b_] += c; g[a, b_] -= c; g[b_, a] -= c
        # connected components: solve only the one that holds the injection pads; report pads outside it
        comp = list(range(n))

        def cf(a):
            while comp[a] != a:
                comp[a] = comp[comp[a]]
                a = comp[a]
            return a
        for a, b_, c in cond:
            comp[cf(a)] = cf(b_)
        roots = collections.Counter(cf(i) for i in src)
        main = roots.most_common(1)[0][0] if roots else None
        unreached = missing + [k for k in inject if k in self.pads and cf(nid(('pad',) + k)) != main]
        keep = [i for i in range(n) if cf(i) == main]
        if len(keep) < 2 or unreached:
            return [], unreached
        pos = {i: j for j, i in enumerate(keep)}
        gm = g[np.ix_(keep, keep)]
        rhs = np.zeros(len(keep))
        for i, a in src.items():
            rhs[pos[i]] += a
        gm[0, :] = 0; gm[0, 0] = 1; rhs[0] = 0            # reference node
        v = np.linalg.solve(gm + np.eye(len(keep)) * 1e-12, rhs)
        out = []
        for (a, b_, L, w, ln) in self.edges:
            ia, ib = nid(a), nid(b_)
            if ia in pos and ib in pos and ia != ib:
                um = INNER_UM if (self.six and self.b.GetLayerName(L).startswith('In')) else OUTER_UM
                r = max(RHO * (ln * 1e-3) / (w * 1e-3 * um * 1e-6), 1e-7)
                out.append(((a, b_, L, w, ln), (v[pos[ia]] - v[pos[ib]]) / r))
        return out, unreached


def main(path, show_all=False):
    b = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    six = b.GetCopperLayerCount() >= 6
    print(f'{path}: {b.GetCopperLayerCount()} copper layers; outer {OUTER_UM:.0f} um'
          + (f', inner {INNER_UM:.1f} um' if six else ''))
    by_net = collections.defaultdict(list)
    for net, case, inj in cases():
        by_net[net].append((case, inj))
    fails = checks = 0
    worst_all = 0.0
    # the released board carries the schematic's net names (link_board.py): find each net by one of its pads
    on_board = {(fp.GetReference(), p.GetNumber()): p.GetNetname() for fp in b.GetFootprints() for p in fp.Pads()}
    for net in sorted(by_net):
        names = {on_board[k] for _, inj in by_net[net] for k in inj if k in on_board}
        nw = Net(b, names.pop() if len(names) == 1 else net)
        sq = collections.defaultdict(float)          # edge -> sum of squares of the cases' currents
        alt = collections.defaultdict(float)         # edge -> largest square among the "ALT" cases (other supply)
        notes = []
        for case, inj in by_net[net]:
            assert abs(sum(inj.values())) < 1e-9, (net, case)
            cur, unreached = nw.solve(inj)
            if unreached:
                notes.append(f'{case}: {", ".join(r + "." + p for r, p in unreached)} not reached by tracks or pours')
            for e, a in cur:
                if case.startswith('ALT'):
                    alt[e] = max(alt[e], a * a)
                else:
                    sq[e] += a * a
        for e, a2 in alt.items():
            sq[e] = max(sq[e], a2)
        rows = []
        for (a, b_, L, w, ln), s in sq.items():
            name = b.GetLayerName(L)
            inner = six and name.startswith('In')
            amps = math.sqrt(s)
            rows.append((rise(amps, w, INNER_UM if inner else OUTER_UM, inner), amps, name, w, ln, a[2]))
        rows.sort(reverse=True)
        if rows:
            dt, amps, layer, w, ln, at = rows[0]
        else:
            dt, amps, layer, w, ln, at = 0.0, 0.0, '-', 0.0, 0.0, (0, 0)
        v = 'OK' if dt <= 10 else 'CHECK' if dt <= 20 else 'FAIL'
        if notes and v == 'OK':
            v = 'CHECK'
        fails += v == 'FAIL'; checks += v == 'CHECK'
        worst_all = max(worst_all, dt)
        inner_amp = max([r[1] for r in rows if r[2].startswith('In')], default=0.0)
        inner_mm = sum(r[4] for r in rows if r[2].startswith('In') and r[1] > 0.01)
        if show_all or v != 'OK' or inner_mm:
            print(f'[{v:5s}] {net:12s} worst {dt:5.1f} C: {amps:.2f} A in {w} mm on {layer} near '
                  f'({at[0] - 100:.1f}, {at[1] - 50:.1f})'
                  + (f'; inner layers carry up to {inner_amp:.2f} A over {inner_mm:.1f} mm' if inner_mm else '')
                  + (f'; {nw.n_zones} pour(s)' if nw.n_zones else ''))
            for s in notes:
                print('          ' + s)
    print(f'{len(by_net)} nets, {sum(len(v) for v in by_net.values())} load cases: {fails} FAIL, {checks} CHECK, '
          f'worst rise {worst_all:.1f} C (IPC-2221)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--all' in sys.argv))
