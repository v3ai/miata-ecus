#!/usr/bin/env python3
"""Injector turn-off clamp study (ngspice): where the injector's stored energy goes, how fast the current decays, and
what each fault does, for three ways of clamping:

  DRV   the driver's own active clamp (daughterboard rev 0.9 as ordered);
  BAT   rev 0.10: per injector, a fast diode from the driver's drain to a TVS that returns to the ECU's battery
        input (drain -|>|- x -|<TVS|- VBAT_IN), the TVS scripts/design.py fits unless a row says otherwise;
  GND   reference: a TVS from the drain to ground (the 1989-93 motherboard's D3/D4, SMCJ30A).

usage: sim_inj_clamp.py [outdir]        (needs ngspice; about 20 s)

Numbers and where they come from
  VND7NV04 (ST DS, Doc ID 7383 rev 4, read 2026-11-13): VCLAMP 40 / 45 / 55 V at 3.5 A, -40..150 C; VCLTH 36 V at
      2 mA (the clamp starts to conduct there); RDS(on) 60 mOhm at 25 C, 120 mOhm over temperature; Ilim 6 A min;
      EAS 200 mJ single pulse. Modelled as a breakdown diode drain-ground: "min" 36 V at 2 mA rising to 40 V at 3.5 A,
      "typ" 41 -> 45 V, "max" 51 -> 55 V (the 4 V rise is ST's for the minimum part; assumed the same for the others).
  SMCJxxA (Littelfuse SMCJ series DS, read 2026-11-13): VBR at 1 mA 16A 17.8-19.7 V, 15A 16.7-18.5 V, 14A 15.6-17.2 V,
      18A 20.0-22.1 V, 30A 33.3-36.8 V; dynamic resistance from VC at IPP (16A: 26.0 V at 57.7 A -> 0.11 ohm);
      6.5 W on an infinite heat sink, RthJL 15 C/W, RthJA 75 C/W, Tj 150 C. VBR temperature coefficient: the DS gives
      the formula without the number; 0.1 %/C assumed (Vishay tabulates 0.084-0.089 %/C for 15-18 V parts of its
      1.5KE family, read 2026-11-13).
  TPSMC16A (Vishay doc 88407, read 2026-11-13), the part fitted: 15.2-16.8 V at 1 mA, 22.5 V at 66.7 A, junction to
      185 C, temperature coefficient 0.078 %/C maximum. Same SMC package.
  Injector: Mazda specifies 12-16 ohm. The inductance is NOT known for Miata injectors: 8 mH was assumed up to
      rev 0.9; a published fit for a 14.8 ohm port injector gives 20.3 mH (Sensors 2020, 20, 4151). So 5-20 mH is
      swept, and anything that only passes at 8 mH is marked.
"""
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 and __name__ == '__main__' else tempfile.mkdtemp()
os.makedirs(OUT, exist_ok=True)
R_MB, R_HARN, R_FEED = 0.03, 0.05, 0.05      # motherboard track, injector feed wire, ECU feed wire (as circuit_sim_full)
ALPHA = 0.001                                 # TVS breakdown temperature coefficient, 1/C (assumed, see above)
TVS = {'13A': (14.4, 15.9, 21.5, 69.8), '14A': (15.6, 17.2, 23.2, 64.7), '15A': (16.7, 18.5, 24.4, 61.5),
       '16A': (17.8, 19.7, 26.0, 57.7), '18A': (20.0, 22.1, 29.2, 51.4), '30A': (33.3, 36.8, 48.4, 31.0),
       # Vishay TPSMC16A (doc 88407, read 2026-11-13): 15.2-16.8 V at 1 mA, 22.5 V at 66.7 A, 185 C junction,
       # temperature coefficient 0.078 %/C maximum
       'T16A': (15.2, 16.8, 22.5, 66.7)}
TVS_ALPHA = {'T16A': 0.00078}
PART_KEY = {'SMCJ14A': '14A', 'TPSMC16A': 'T16A'}            # design.py value -> key above
NAME = {'T16A': 'TPSMC16A'}                                  # the others are SMCJ + key


def _fitted():
    """the clamp TVS scripts/design.py fits (D46), as a key above"""
    here, cwd = os.path.dirname(os.path.abspath(__file__)), os.getcwd()
    scripts = os.path.join(here, '..', '..', 'scripts')
    try:
        sys.path.insert(0, scripts); os.chdir(scripts)
        import design
        return PART_KEY[next(p['value'] for p in design.parts if p['ref'] == 'D46')]
    except Exception:
        return '14A'
    finally:
        os.chdir(cwd)


FITTED = _fitted()
DRV = {'min': (36.0, 4.0 / 3.5), 'typ': (41.0, 4.0 / 3.5), 'max': (51.0, 4.0 / 3.5)}
rows = []


def trapz(y, t):
    return float(np.trapezoid(y, t)) if hasattr(np, 'trapezoid') else float(np.trapz(y, t))


def tvs_model(name, part, corner='typ', tj=25.0):
    lo, hi, vc, ipp = TVS[part]
    bv = {'min': lo, 'typ': (lo + hi) / 2, 'max': hi}[corner] * (1 + TVS_ALPHA.get(part, ALPHA) * (tj - 25))
    rs = (vc - hi) / ipp
    return f'.model {name} d(bv={bv:.3f} ibv=1m is=1e-12 rs={rs:.3f} cjo=2n)', bv


def run(name, net, vecs, step='0.5u', stop='9m'):
    cir, dat = os.path.join(OUT, name + '.cir'), os.path.join(OUT, name + '.dat')
    if os.path.exists(dat):
        os.remove(dat)
    open(cir, 'w').write(net + f"""
.options method=gear reltol=2e-3 abstol=1e-9 vntol=1e-5 gmin=1e-10 itl4=200
.tran {step} {stop} 0 {step}
.control
run
wrdata {dat} {' '.join(vecs)}
.endc
.end
""")
    r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dat):
        raise RuntimeError(name + ': ' + r.stdout[-2000:] + r.stderr[-2000:])
    a = np.loadtxt(dat)
    d = {'t': a[:, 0]}
    for i, v in enumerate(vecs):
        d[v] = a[:, 2 * i + 1]
    return d


def bench(name, mode, L=8e-3, R=12.0, vb=14.4, drv='typ', tvs=None, tvs_corner='typ', tvs_tj=25.0, fault=None,
          n_inj=1, n_drv=1, mb_tvs=None, ton=6e-3, vfeed=None, tvs_each=None):
    """One injector wire: n_inj injectors in parallel on it, n_drv drivers (each with its own clamp parts in mode
    BAT). fault: None, 'tvs_open', 'tvs_short', 'diode_short'. mb_tvs: a TVS part on the motherboard node to ground.
    tvs_each: [(corner, junction temperature), ...] per driver, for clamp TVSs that differ from each other.
    Returns a dict of energies (J; 'e_tvs_each' per driver), peak drain voltage and decay times."""
    tvs = tvs or FITTED
    bvd, rsd = DRV[drv]
    net = [f'* {name}', f'Vb vb 0 {vb}', f'Rh vb a {R_HARN}',
           f'Vf vf 0 {vb if vfeed is None else vfeed}', f'Rfeed vf vbi {R_FEED}', 'Cvbi vbi 0 10u']
    for k in range(n_inj):
        net += [f'Rl{k} a b{k} {R}', f'Ll{k} b{k} w {L}']
    net += [f'Rw w mb {R_MB}']
    vecs = ['v(mb)']
    if mb_tvs or mode == 'GND':
        m, _ = tvs_model('dmb', mb_tvs or '30A', 'max')
        net += [m, 'Dmb 0 tvm dmb', 'Vtvm mb tvm 0']
        vecs.append('i(Vtvm)')
    for j in range(n_drv):
        net += [f'Rs{j} mb o{j} {0.01 * (j + 1)}', f'Vg{j} g{j} 0 PULSE(0 5 0.1m 1u 1u {ton + 2e-6 * j} 100m)',
                f'Vdi{j} o{j} d{j} 0',
                f'Bq{j} d{j} 0 I = V(g{j}) > 2.5 ? min(6.0, V(d{j})/0.06) : 0',
                f'Dcl{j} 0 cl{j} ddrv', f'Vcl{j} d{j} cl{j} 0', f'Dby{j} 0 d{j} dbody']
        vecs += [f'i(Vcl{j})', f'i(Vdi{j})']
        if mode == 'BAT' and fault != 'tvs_open':
            # drain -|>|- x -|<TVS|- VBAT_IN
            net += [f'Vk{j} o{j} k{j} 0']
            net += [f'Rks{j} k{j} x{j} 1m'] if fault == 'diode_short' else [f'Dk{j} k{j} x{j} dfast']
            net += [f'Rzs{j} x{j} z{j} 1m'] if fault == 'tvs_short' else [f'Dz{j} z{j} x{j} dz{j if tvs_each else ""}']
            net += [f'Vz{j} z{j} vbi 0']
            vecs += [f'i(Vk{j})', f'v(x{j})', 'v(vbi)', f'v(o{j})']
    mz, bvz = tvs_model('dz', tvs, tvs_corner, tvs_tj)
    for j, (cj, tjj) in enumerate(tvs_each or []):
        net.append(tvs_model(f'dz{j}', tvs, cj, tjj)[0])
    net += [mz, f'.model ddrv d(bv={bvd} ibv=2m is=1e-14 rs={rsd:.3f})', '.model dbody d(is=1e-9 n=1.2 rs=0.02)',
            # ES1D-class ultrafast: about 0.9 V at 1 A
            '.model dfast d(is=2e-9 n=1.7 rs=0.06 tt=20n cjo=20p)']
    d = run(name, '\n'.join(net), vecs)
    t = d['t']
    toff = 0.1e-3 + 1e-6 + ton
    res = {'vpk': float(np.max(d['v(mb)'])), 'bvz': bvz}
    e_drv = sum(trapz(np.where(d[f'i(Vcl{j})'] > 0, d['v(mb)'] * d[f'i(Vcl{j})'], 0), t) for j in range(n_drv))
    res['e_drv'] = e_drv
    res['e_mb'] = trapz(np.where(d['i(Vtvm)'] > 0, d['v(mb)'] * d['i(Vtvm)'], 0), t) if 'i(Vtvm)' in d else 0.0
    e_tvs = e_dio = 0.0
    res['e_tvs_each'] = []
    if f'i(Vk0)' in d:
        for j in range(n_drv):
            ik = d[f'i(Vk{j})']
            m = (t > toff) & (ik > 0)
            res['e_tvs_each'].append(trapz(np.where(m, (d[f'v(x{j})'] - d['v(vbi)']) * ik, 0), t))
            e_tvs += res['e_tvs_each'][-1]
            e_dio += trapz(np.where(m, (d[f'v(o{j})'] - d[f'v(x{j})']) * ik, 0), t)
            res[f'ik_on{j}'] = float(np.mean(ik[(t > 3e-3) & (t < toff - 0.2e-3)]))   # clamp current while the driver is on
    res['e_tvs'], res['e_dio'] = e_tvs, e_dio
    iinj = sum(d[f'i(Vdi{j})'] for j in range(n_drv))                # wire current seen by the drivers (on-state)
    i0 = float(np.mean(iinj[(t > toff - 0.3e-3) & (t < toff - 0.05e-3)]))
    res['i0'] = i0
    # injector current after turn-off = everything leaving the wire node: driver clamps + BAT clamps + motherboard TVS
    itot = sum(d[f'i(Vcl{j})'] for j in range(n_drv)) + sum(d[f'i(Vdi{j})'] * 0 for j in range(n_drv))
    if 'i(Vk0)' in d:
        itot = itot + sum(d[f'i(Vk{j})'] for j in range(n_drv))
    if 'i(Vtvm)' in d:
        itot = itot + d['i(Vtvm)']
    after = t > toff + 2e-6 * n_drv + 5e-6          # after the last of the drivers on this wire has switched off
    for frac, key in ((0.35, 't35'), (0.05, 't05')):
        idx = np.where(after & (itot < frac * i0))[0]
        res[key] = float(t[idx[0]] - toff) if len(idx) else float('nan')
    return res


def pair_share(L, corners=('min', 'max'), dt=0.0, rpm=7200, tag='', tvs=None):
    """Two injectors and two drivers on one wire (1989-93, batch): the two clamp TVSs sit in parallel, and the one
    with the lower breakdown takes the larger share. dt: how much hotter the first one runs (its breakdown rises with
    temperature, which pushes current back to the other). Returns ([W per TVS at rpm], peak V)."""
    r = bench(f'I_share{tag}_{int(L * 1e3)}', 'BAT', L=L, n_inj=2, n_drv=2, tvs=tvs,
              tvs_each=[(corners[0], 60.0 + dt), (corners[1], 60.0)])
    return [e * rpm / 60 for e in r['e_tvs_each']], r['vpk']          # batch: each wire fires once per revolution


def rec(group, case, text, verdict='OK'):
    rows.append((group, case, text, verdict))
    print(f'{verdict:5s} {group:10s} {case:44s} {text}')


mJ = lambda e: f'{e * 1e3:.2f} mJ'

def main():
    base = {}
    # ---- A. the three clamps, typical parts, 14.4 V, 12 ohm, over the inductance range ------------------------------
    for L in (5e-3, 8e-3, 12e-3, 20e-3):
        for mode in ('DRV', 'BAT', 'GND'):
            r = bench(f'A_{mode}_{int(L * 1e3)}', mode, L=L, mb_tvs='30A' if mode == 'GND' else None)
            base[(mode, L)] = r
            heat = {'DRV': r['e_drv'], 'BAT': r['e_tvs'] + r['e_dio'] + r['e_drv'], 'GND': r['e_mb'] + r['e_drv']}[mode]
            rec('A typical', f'{mode} {L * 1e3:.0f} mH',
                f'peak {r["vpk"]:.1f} V; in the ECU {mJ(heat)} per shot (driver {mJ(r["e_drv"])}, TVS {mJ(r["e_tvs"] + r["e_mb"])}, '
                f'diode {mJ(r["e_dio"])}); stored 1/2 L I^2 = {mJ(0.5 * L * r["i0"] ** 2)}; current to 35 % in '
                f'{r["t35"] * 1e6:.0f} us, to 5 % in {r["t05"] * 1e6:.0f} us')

    # ---- B. choice of TVS: clamp level against the driver's own clamp, and reverse battery ------------------------------
    for part in ('T16A', '14A', '15A', '16A', '18A'):
        lo, hi, vc, ipp = TVS[part]
        worst = bench(f'B_{part}_w', 'BAT', L=20e-3, vb=15.5, drv='min', tvs=part, tvs_corner='max', tvs_tj=150)
        typ = bench(f'B_{part}_t', 'BAT', L=20e-3, vb=14.4, drv='typ', tvs=part)
        share = worst['e_drv'] / max(1e-12, worst['e_drv'] + worst['e_tvs'] + worst['e_dio'])
        rev_ok = lo > 16.0 - 1.4        # reverse battery at -16 V: TVS sees 16 V less two diode drops
        rec('B TVS', NAME.get(part, 'SMCJ' + part) + (' (fitted)' if part == FITTED else ''),
            f'typical: peak {typ["vpk"]:.1f} V, 35 % in {typ["t35"] * 1e6:.0f} us; worst case (TVS at its maximum and 150 C, '
            f'driver clamp at its minimum, 15.5 V): peak {worst["vpk"]:.1f} V, driver takes {share * 100:.0f} % of the heat; '
            f'reverse battery -16 V: {"blocks" if rev_ok else "CONDUCTS"} (VBR min {lo} V)',
            'OK' if rev_ok and typ['e_drv'] < 1e-5 else 'CHECK')

    # ---- C. battery voltage: decay time and energy ----------------------------------------------------------------------
    for vb in (9.0, 12.0, 14.4, 16.0):
        b = bench(f'C_BAT_{vb}', 'BAT', L=12e-3, vb=vb)
        g = bench(f'C_DRV_{vb}', 'DRV', L=12e-3, vb=vb)
        rec('C battery', f'{vb} V, 12 mH',
            f'BAT: peak {b["vpk"]:.1f} V, to 35 % in {b["t35"] * 1e6:.0f} us, TVS {mJ(b["e_tvs"])}; '
            f'DRV: peak {g["vpk"]:.1f} V, to 35 % in {g["t35"] * 1e6:.0f} us, driver {mJ(g["e_drv"])}')

    # ---- D. average power at 7200 rpm: sequential (one shot per 720 deg) and batch (one per revolution) -------------
    RPM = 7200
    for L in (8e-3, 12e-3, 20e-3):
        b = base[('BAT', L)] if ('BAT', L) in base else bench(f'D_{L}', 'BAT', L=L)
        g = base[('DRV', L)]
        seq, bat = RPM / 120, RPM / 60
        rec('D power', f'{L * 1e3:.0f} mH, {RPM} rpm',
            f'BAT: TVS {b["e_tvs"] * seq:.2f} W sequential / {b["e_tvs"] * bat:.2f} W batch per injector, diode '
            f'{b["e_dio"] * seq * 1e3:.0f} / {b["e_dio"] * bat * 1e3:.0f} mW; DRV: driver clamp {g["e_drv"] * seq:.2f} / '
            f'{g["e_drv"] * bat:.2f} W', 'OK' if b['e_tvs'] * bat < 1.5 else 'CHECK')

    # ---- E. faults -----------------------------------------------------------------------------------------------------------
    for fault, what in (('tvs_open', 'TVS or diode open'), ('tvs_short', 'TVS shorted'), ('diode_short', 'diode shorted')):
        r = bench(f'E_{fault}', 'BAT', L=20e-3, fault=fault)
        ion = r.get('ik_on0', 0.0)
        rec('E fault', what,
            f'peak {r["vpk"]:.1f} V; driver clamp {mJ(r["e_drv"])}'
            + (f'; the driver is in current limit while on: {-ion:.1f} A from the battery input through the TVS (forward) '
               f'and the shorted diode, the injector gets no voltage' if abs(ion) > 0.01 else
               f'; to 35 % in {r["t35"] * 1e6:.0f} us'),
            'CHECK')

    # ---- F. overvoltage: 24 V jump start, and the supply held at 40-45 V (load dump, clamped by D6) --------------
    for vb in (24.0, 40.0, 45.0):
        r = bench(f'F_{vb}', 'BAT', L=20e-3, vb=vb, drv='min')
        g = bench(f'F_GND_{vb}', 'GND', L=20e-3, vb=vb, drv='min', mb_tvs='30A', ton=1e-3)
        rec('F overvolt', f'supply {vb:.0f} V',
            f'BAT: peak {r["vpk"]:.1f} V, driver clamp {mJ(r["e_drv"])} per shot, TVS {mJ(r["e_tvs"])}; '
            f'GND reference: TVS to ground {mJ(g["e_mb"])} in 8 ms (continuous conduction above its breakdown)',
            'CHECK' if vb > 30 else 'OK')

    # ---- H. 1989-95 with the jumpers on PAIR: two injectors and two drivers on one wire -----------------------------
    for mb in (None, '30A'):
        r = bench(f'H_pair_{mb}', 'BAT', L=20e-3, n_inj=2, n_drv=2, mb_tvs=mb)
        rec('H pair', '2 injectors, 2 drivers' + (' + motherboard SMCJ30A' if mb else ''),
            f'peak {r["vpk"]:.1f} V; daughterboard TVSs {mJ(r["e_tvs"])} together, motherboard TVS {mJ(r["e_mb"])}, '
            f'drivers {mJ(r["e_drv"])}; to 35 % in {r["t35"] * 1e6:.0f} us')

    # ---- I. the same wire with unequal clamp TVSs: who takes the energy? ---------------------------------------------
    # Worst case the datasheets allow: one part at the bottom of its breakdown range, the other at the top. The low
    # one takes nearly everything; it only hands current over once it runs hotter by the spread divided by its
    # temperature coefficient (about 100 C for a 1.6 V spread). What that does to its temperature is the board
    # model's "batch_hog" case (board_thermal.py); here only the electrical split.
    for part in ('14A', 'T16A'):
        for L in (8e-3, 20e-3):
            eq, _ = pair_share(L, ('typ', 'typ'), tag=f'_{part}eq', tvs=part)
            rows_ = []
            for dt in (0.0, 50.0, 100.0):
                p, vpk = pair_share(L, ('min', 'max'), dt, tag=f'_{part}d{int(dt)}', tvs=part)
                rows_.append(f'{dt:.0f} C hotter: {p[0]:.2f} / {p[1]:.2f} W')
            rec('I sharing', f'{NAME.get(part, "SMCJ" + part)}, {L * 1e3:.0f} mH, 7200 rpm batch',
                f'equal parts {eq[0]:.2f} / {eq[1]:.2f} W; parts at the two ends of the range, the low one '
                + '; '.join(rows_), 'CHECK' if L > 10e-3 else 'OK')

    with open(os.path.join(OUT, 'inj_clamp_report.txt'), 'w') as f:
        for g, c, tx, v in rows:
            f.write(f'{v}\t{g}\t{c}\t{tx}\n')
    print('report:', os.path.join(OUT, 'inj_clamp_report.txt'))


if __name__ == '__main__':
    main()
