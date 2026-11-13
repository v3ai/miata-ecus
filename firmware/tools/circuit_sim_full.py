#!/usr/bin/env python3
"""Whole-board circuit simulations, the companion of circuit_sim.py (same conventions and report format), run in
ngspice:

  P. daughterboard power-up, sequencing, cold crank (ISO 16750-2 starting profiles), brown-out and key-off;
  O. every motherboard's outputs into real car loads, year by year, from the daughterboard driver through the
     motherboard to the harness cavity;
  I. every motherboard's inputs with real sensors, year by year, incl. sensor wires shorted to battery;
  W. the on-board wideband: LSU 4.9 equivalent on the FOME/rusEFI front end, ESR injection, heater.

usage: circuit_sim_full.py [outdir]     (needs ngspice on the PATH; runs in about 1.5 minutes)

Component values and connectivity come from scripts/design.py, scripts/wideband.py and the scripts/mb_*.py
year modules (asserted below, so a design change that breaks an assumption stops the run). Datasheet numbers are
quoted with their source; anything marked "assumed" is an engineering estimate, not a datasheet value.

Verdicts: OK / CHECK (works, with a caveat in the note) / FAIL (outside a datasheet limit or does not work; exits
non-zero) / REF (not the board as built: a proposed fix or an alternative, kept to show what it would change).
"""
import math
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, '..', '..', 'scripts'))
sys.path.insert(0, SCRIPTS)
import design            # noqa: E402  (daughterboard parts, incl. the wideband block from wideband.py)
import mb_y8993, mb_y9495, mb_na96, mb_nb1, mb_nb2   # noqa: E402,E401  (the 1989-95 board as fitted for each range)
import sim_inj_clamp as IC   # noqa: E402  (injector clamp bench, rev 0.10)

OUT = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()
os.makedirs(OUT, exist_ok=True)
results = []
T0 = time.time()


# ---- helpers (same behaviour as circuit_sim.py's; circuit_sim.py runs its simulations on import) -----------------
def spice(name, netlist, vectors):
    """Run a transient/ac netlist in batch mode, return {vector: np.array} from wrdata (first column = time/freq)."""
    cir = os.path.join(OUT, name + '.cir')
    dat = os.path.join(OUT, name + '.dat')
    if os.path.exists(dat):
        os.remove(dat)
    with open(cir, 'w') as f:
        f.write(netlist.replace('@DAT@', dat).replace('@VEC@', ' '.join(vectors)))
    r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dat):
        raise RuntimeError(name + ': ' + r.stdout[-2500:] + r.stderr[-2500:])
    a = np.loadtxt(dat)
    if a.ndim == 1:
        a = a[None, :]
    cols = {'time': a[:, 0]}
    for i, v in enumerate(vectors):
        cols[v] = a[:, 2 * i + 1]
    return cols


def spice_op(name, netlist, exprs):
    """Run an .op netlist and return {expr: value} printed by 'print expr'."""
    cir = os.path.join(OUT, name + '.cir')
    body = netlist.replace('@PRINT@', '\n'.join(f'print {e}' for e in exprs))
    with open(cir, 'w') as f:
        f.write(body)
    r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        if ' = ' in line:
            k, v = line.split(' = ', 1)
            try:
                out[k.strip()] = float(v.split()[0])
            except ValueError:
                pass
    missing = [e for e in exprs if e.lower() not in out]
    if missing:
        raise RuntimeError(name + ': missing ' + str(missing) + '\n' + r.stdout[-2500:] + r.stderr[-1500:])
    return {e: out[e.lower()] for e in exprs}


def record(area, check, value, verdict, note=''):
    results.append((area, check, value, verdict, note))


def tran_ctl(step, stop, tmax=None):
    return f""".tran {step} {stop} 0 {tmax or step}
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""


def sv(s):
    """'4.7k' -> 4700, '10u/50V' -> 1e-5, '2.2uH' -> 2.2e-6, '62' -> 62"""
    s = str(s).split('/')[0].strip().rstrip('HFR') or '0'
    mult = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3, 'M': 1e6}
    return float(s[:-1]) * mult[s[-1]] if s[-1] in mult else float(s)


DB = {p['ref']: p for p in design.parts}


def val(ref, parts=None):
    return sv((DB if parts is None else parts)[ref]['value'])


def on(ref, *nets_, parts=DB):
    """Assert a part sits on the given nets (the simulation's topology assumption)."""
    have = set(v for v in parts[ref]['pads'].values() if v)
    assert set(nets_) <= have, f'{ref} is on {sorted(have)}, the simulation assumes {nets_}'
    return parts[ref]


def between(a, b, kind='R', parts=DB):
    """The part of type kind connecting nets a and b (exactly one)."""
    hits = [p for p in parts.values() if p['ref'].startswith(kind) and
            {a, b} == set(v for v in p['pads'].values() if v)]
    assert len(hits) == 1, f'expected one {kind} between {a} and {b}, found {[h["ref"] for h in hits]}'
    return hits[0]


def pin_avg(t, v, t1, t2):
    m = (t >= t1) & (t <= t2)
    return float(np.mean(v[m])) if m.any() else float('nan')


def energy(t, v, i):
    p = v * i
    p = np.where(i > 0, p, 0.0)
    return float(np.trapezoid(p, t)) if hasattr(np, 'trapezoid') else float(np.trapz(p, t))


def integ(t, y):
    return float(np.trapezoid(y, t)) if hasattr(np, 'trapezoid') else float(np.trapz(y, t))


# ---- common device models -----------------------------------------------------------------------------------------
# Diodes as circuit_sim.py: SS34 Schottky, 1N4148WS, BAT54 (Schottky), SMCJ30A (D6), SMAJ33A (D11/D12) at the bad end
# of its 36.7-40.6 V breakdown, SMCJ40A (1989-93 D3/D4 to rev 0.7; Littelfuse: VBR 44.4-49.1 V at 1 mA, VC 64.5 V at
# 23.3 A, so about 0.66 ohm dynamic), SMCJ30A at the top of its 33.3-36.8 V breakdown (1989-93 D3/D4 from rev 0.8;
# VC 48.4 V at 31 A, so about 0.37 ohm dynamic).
MODELS = """.model dss34 d(is=5u n=1.1 rs=0.03)
.model d4148 d(is=2.5n n=1.75 rs=0.6)
.model dbat54 d(is=2e-7 n=1.05 rs=2.5)
.model d30 d(bv=34.5 ibv=1m is=1e-12 rs=0.45)
.model d33max d(bv=40.6 ibv=1m is=1e-12 rs=1.7)
.model d33min d(bv=36.7 ibv=1m is=1e-12 rs=1.7)
.model d40max d(bv=49.1 ibv=1m is=1e-12 rs=0.66)
.model d40min d(bv=44.4 ibv=1m is=1e-12 rs=0.66)
.model d30max d(bv=36.8 ibv=1m is=1e-12 rs=0.37)
.model desd d(is=1e-14 n=1)
.model dbe d(is=1e-14 n=1)
"""

# STM32F407 (DS8626): VDD 1.8-3.6 V; "VDDA and VSSA must be connected to VDD and VSS"; POR/PDR 1.8 V. rusEFI programs
# BOR level 1 at start-up (stm32_common.cpp; ST HAL: "supply voltage ranges from 2.10 to 2.40 V"), modelled as 2.2 V
# falling / 2.3 V rising (assumed inside that range). At 168 MHz the flash needs 5 wait states for VDD 2.7-3.6 V
# (RM0090 wait-state table, recalled), which is what rusEFI configures: between BOR1 and 2.7 V the core is not reset
# but runs its flash out of spec.
F4_BOR_FALL, F4_BOR_RISE, F4_VMIN_168 = 2.2, 2.3, 2.7
# STM32F103x8 (DS5319, read from st.com 2026-11-01): VDD 2.0-3.6 V; "a maximum difference of 300 mV between VDD and
# VDDA can be tolerated during power-up and operation"; standard (non-FT) I/O VIN max VDD+0.3 V, injected current
# +-5 mA per pin, +-25 mA total; FT pins: no positive injection. POR/PDR 1.92/1.88 V typical (Table 11, recalled).
F1_PDR_FALL, F1_POR_RISE, F1_VMIN, F1_DIFF = 1.88, 1.92, 2.0, 0.3
# Analog-mode limit on STM32 pins (FT or TTa) with the ADC connected: VDDA + 0.3 V; exceeding it injects into VDDA
# (ST knowledge-base article "What is the maximum input voltage that can be applied to my STM32 GPIO", and the ST
# moderator answer for an F2 PA2 in analog mode). Digital FT pins: VDD + 4 V absolute maximum.
AN_MAX = 3.3 + 0.3
FT_MAX = 3.3 + 4.0
VIL, VIH = 0.3 * 3.3, 0.7 * 3.3

YEARS = [('1989-93', mb_y8993), ('1994-95', mb_y9495), ('1996-97', mb_na96), ('1999-2000', mb_nb1), ('2001-05', mb_nb2)]
MB = {}
for _y, _m in YEARS:
    _ps = [dict(p) for p in _m.build_parts()]
    MB[_y] = {p['ref']: p for p in _ps}


def harness(year):
    """{daughterboard net: [cavities]} of the year's harness header J1. A cavity on a motherboard-only net (HARN_xx:
    jumpers and option links) counts for every daughterboard net its fitted 0R links reach, and for none if they are
    open (1989-95: the tach output only reaches 2I through JP5, which is left open)."""
    group = {}
    for p in MB[year].values():
        if p['value'] == '0R' and p['lcsc'] and len(p['pads']) == 2 and not p.get('desc', '').upper().startswith('NOT FITTED'):
            x, y_ = p['pads'].values()
            gx, gy = group.get(x, {x}), group.get(y_, {y_})
            for n in gx | gy:
                group[n] = gx | gy
    out = {}
    for cav, net in MB[year]['J1']['pads'].items():
        if not net:
            continue
        nets_ = [net] if not net.startswith('HARN_') else sorted(n for n in group.get(net, ()) if not n.startswith('HARN_'))
        for n in nets_:
            out.setdefault(n, []).append(cav)
    return out


# =================================================================================================================
# P. Power-up and supply sequencing (daughterboard)
# =================================================================================================================
# Chain (design.py): VBAT_IN -> D6 SMCJ30A to GND, D7 SS34 -> +12V_IN -> F1 nSMD050 PTC -> +12V (D12 SMAJ33A, C24,
# R7+C16 damper) -> L1 2.2 uH (0.3 ohm, its BOM description) -> +12V_F (C17, C18) -> U2 LMR14020 -> +5V
# (C22/C23/C59, C26, C34/C35, C57, C108, C117) -> U4 AMS1117-3.3 -> +3V3; U103 REF3033 from +5V -> WB_VDDA
# (F103 VDDA, C107/C109, R101/R102 virtual-ground divider); U3 TLS115B0 tracks +5V from +12V -> V5_SENS.
for ref, nets_ in (('D7', ('VBAT_IN', '+12V_IN')), ('F1', ('+12V_IN', '+12V')), ('D12', ('+12V', 'GND')),
                   ('L1', ('+12V', '+12V_F')), ('U2', ('+12V_F', 'BUCK_FB', 'BUCK_SS')), ('U4', ('+5V', '+3V3')),
                   ('U103', ('+5V', 'WB_VDDA')), ('U3', ('+12V', '+5V', 'V5_SENS')), ('FB1', ('+3V3', '+3V3A')),
                   ('U102', ('+3V3', 'WB_VDDA'))):
    on(ref, *nets_)
assert DB['U2']['pads']['3'] == '+12V_F', 'LMR14020 EN (pin 3) is assumed tied to VIN'
assert DB['U3']['pads']['7'] == '+12V', 'TLS115 EN (pin 7) is assumed tied to its input'
# LMR14020 (TI datasheet, read 2026-11-01): VIN 4-40 V; UVLO rising 3.5/3.7/3.9 V, 285 mV hysteresis; VREF 0.75 V;
# SS current 3 uA, t_ss = Css * VREF / Iss; current limit 2.5/3.2/3.8 A; in dropout the high side stays on for 5-6
# cycles, then refreshes BOOT (so Vout ~ Vin - I * (Rds 0.18 ohm max + L2 67 mOhm)).
VREF_BUCK = 0.75
V5_NOM = VREF_BUCK * (1 + val('R9') / val('R10'))
T_SS = val('C20') * VREF_BUCK / 3e-6
# U4, the +3V3 regulator (design.py value):
# AMS1117-3.3 (rev 0.6 and before; AMS datasheet, waveshare copy): 3.267-3.333 V at 25 C, 3.235-3.365 V over
# temperature; dropout 1.1 V typ / 1.3 V max at 800 mA, "decreasing at lower load currents"; quiescent 5 mA typ. At this
# board's ~0.15 A the dropout is assumed 1.0 V typical; 1.3 V (datasheet max) is the worst case.
# LDL1117S33R (rev 0.7; ST datasheet via LCSC): dropout 350 mV typ / 600 mV max at 1.2 A, -40..125 C, quiescent 500 uA.
# At ~0.15 A the PMOS pass device's dropout scales with current (about 45 mV typ / 75 mV max); 0.15 V typical and
# 0.3 V worst case are assumed here, to cover the weaker gate drive while +5V is low.
LDOS = {'AMS1117-3.3': dict(name='AMS1117', vdo=1.0, vdo_max=1.3, iq=5e-3, vmin=3.235, vmax=3.365),
        'LDL1117S33R': dict(name='LDL1117', vdo=0.15, vdo_max=0.3, iq=0.5e-3, vmin=3.234, vmax=3.366)}
LDO = LDOS[DB['U4']['value']]
# rev 0.7: Schottky D30 from WB_VDDA (anode) to +3V3, so VDDA can't stay up while VDD collapses (key-off, brown-out)
VDDA_CLAMP = any(r.startswith('D') and p['pads'].get('1') == '+3V3' and p['pads'].get('2') == 'WB_VDDA'
                 for r, p in DB.items())
# REF3033 (TI REF30xx datasheet SBVS032H): 3.294-3.306 V; dropout 1 mV typ / 50 mV max (no load); VIN min VREF+50 mV;
# 25 mA load max, 45 mA short-circuit; 50 uA quiescent. Below its minimum input it is assumed to follow VIN - 50 mV
# (the worst case for the VDDA - VDD check; the datasheet does not specify it).
# TLS115B0 (Infineon datasheet v1.11): VIN 4-45 V; dropout 250 mV typ / 500 mV max at 150 mA; tracking +-5 mV;
# current limit 151 mA min; EN tied to IN (as here) = always on.
# Loads (assumed): +3V3 0.15 A (F407 at 168 MHz, F103, two CAN transceivers, LEDs; scaled down below 1.8 V);
# +5V 10 mA besides the regulators (level shifter, TC4427, LM2903, driver-input pull-downs); V5_SENS 35 mA (MAP, TPS,
# CLT/IAT pull-ups, two hall pull-ups). Effective capacitance with DC bias (assumed): 10 uF 1206/50 V at 12 V -> 7 uF,
# 10 uF 0805 at 5 V -> 6 uF, at 3.3 V -> 7 uF; 4.7 uF 0603 -> 3 uF.
C12_EFF, C5_EFF, C33_EFF = 7e-6, 6 * 6e-6 + 2e-6 + 0.5e-6, 7e-6 + 3 * 3e-6 + 1.5e-6


# +3V3 load: about 0.15 A for the two processors, LEDs and pull-ups (F407 at 168 MHz about 90-110 mA, F103 about 30 mA;
# ST datasheet figures, recalled), plus 0.10 A while a microSD card writes (SD default-speed maximum over one second:
# Swissbit AN2111, read 2026-11-13) on
# boards that have the socket. F1 and L1 resistance by part: the 0.5 A 1206 fuse about 0.5 ohm and the 1210 inductor
# 0.3 ohm (rev 0.9); the 1.1 A 1812 fuse about 0.2 ohm and the moulded inductor about 0.03 ohm (rev 0.10; typical
# catalogue values, not read from the makers' sheets).
I33 = 0.15 + (0.10 if 'J4' in DB else 0.0)
RF1 = 0.5 if '050' in DB['F1']['value'] else 0.2
RL1 = 0.3 if DB['L1']['fp'].endswith('L_1210_3225Metric') else 0.03
F1_HOLD_A = 0.5 if '050' in DB['F1']['value'] else 1.1


def power_net(pwl, tstop, tmax, vdo=None, i33=None, clamp=None, keyoff=None, rf1=None, iq=None):
    vdo = LDO['vdo'] if vdo is None else vdo
    clamp = VDDA_CLAMP if clamp is None else clamp
    iq = LDO['iq'] if iq is None else iq
    i33 = I33 if i33 is None else i33
    rf1 = RF1 if rf1 is None else rf1
    if keyoff is None:
        src = f'Vsrc src 0 PWL({pwl})\nRsrc src vbat 0.02\nRvb vbat 0 1k'
    else:   # main relay contact opens at t = keyoff; the motherboard loads on VBAT_IN (heater, valves) take it down
        src = (f'Vsrc src 0 12.6\nVk k 0 PWL(0 5 {keyoff} 5 {keyoff + 1e-5} 0)\nSkey src vbat k 0 skey\n'
               f'.model skey sw(vt=2.5 ron=0.02 roff=1e9)\nRvb vbat 0 100')
    ib = (f'(V(en) > 0.5 ? min(3.2, max(0, (min({V5_NOM}*min(V(ss),{VREF_BUCK})/{VREF_BUCK}, V(p12f)-0.1)'
          f' - V(v5))/0.02)) : 0)')
    ia = f'min(1.1, max(0, (min(3.3, V(v5)-{vdo}) - V(v33))/0.02))'
    ir = 'min(0.045, max(0, (min(3.3, V(v5)-0.05) - V(vdda))/0.05))'
    it = 'min(0.35, max(0, (min(V(v5), V(p12)-0.25) - V(v5s))/0.05))'
    fix = 'Dfix vdda v33 dbat54' if clamp else ''
    return f"""* daughterboard supply chain (behavioural regulators)
{src}
Cvb vbat 0 1u
D6 0 vbat d30
D7 vbat p12in dss34
Rf1 p12in p12 {rf1}
D12 0 p12 d33min
C24 p12 0 1u
R7 p12 damp {val('R7')}
C16 damp 0 {C12_EFF}
L1 p12 l1x {val('L1')}
Rl1 l1x p12f {RL1}
C17 p12f 0 {C12_EFF}
C18 p12f 0 {C12_EFF}
* LMR14020: UVLO 3.70 V rising / 3.415 V falling; soft-start 3 uA into C20
Vone one 0 1
Suv one en p12f 0 suvlo
.model suvlo sw(vt=3.5575 vh=0.1425 ron=1 roff=1e9)
Ren en 0 1meg
Css ss 0 {val('C20')}
Bss 0 ss I = V(en) > 0.5 ? (V(ss) < 1.0 ? 3u : 0) : -V(ss)/1k
Bbk 0 v5 I = {ib}
Bbki p12f 0 I = {ib}*V(v5)/(0.85*max(V(p12f),1))
C5v v5 0 {C5_EFF}
Bl5 v5 0 I = 0.01*min(1, max(V(v5),0)/3)
* U4 3.3 V LDO (dropout vdo)
Bam 0 v33 I = {ia}
Bami v5 0 I = {ia} + {iq}*min(1, max(V(v5),0)/2)
C33 v33 0 {C33_EFF}
Bl33 v33 0 I = {i33}*min(1, max(V(v33),0)/1.8)
* REF3033 -> F103 VDDA (C107 + C109; R101/R102 2k and the ADC: about 1.25 kohm)
Brf 0 vdda I = {ir}
Brfi v5 0 I = {ir} + 50u*min(1, max(V(v5),0)/2)
Cvdda vdda 0 {val('C107') + val('C109')}
Rvdda vdda 0 1.25k
{fix}
* TLS115B0 tracking +5V, fed from +12V
Btl 0 v5s I = {it}
Btli p12 0 I = {it} + 7m*min(1, max(V(p12),0)/4)
Cv5s v5s 0 2u
Bl5s v5s 0 I = 0.035*min(1, max(V(v5s),0)/3)
{MODELS}
.tran {tmax} {tstop} 0 {tmax}
.control
run
linearize v(vbat) v(p12) v(p12f) v(v5) v(v33) v(vdda) v(v5s)
wrdata @DAT@ @VEC@
.endc
.end
"""


PV = ['v(vbat)', 'v(p12)', 'v(p12f)', 'v(v5)', 'v(v33)', 'v(vdda)', 'v(v5s)']


def reset_model(t, vdd, fall, rise, rpu=40e3, cnrst=None):
    """NRST: held low by the internal reset while VDD is below the threshold (hysteresis), then charged by the
    internal pull-up (RPU 40 kohm typical, assumed for both MCUs) into the NRST capacitor. The core runs once
    NRST > 0.7 VDD. Returns the run mask."""
    tau = rpu * (cnrst if cnrst is not None else val('C15'))
    nrst, inreset, run = 0.0, True, np.zeros(len(t), bool)
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]
        if inreset and vdd[k] > rise:
            inreset = False
        elif not inreset and vdd[k] < fall:
            inreset = True
        if inreset:
            nrst = 0.0
        else:
            nrst += (vdd[k] - nrst) * min(1.0, dt / tau)
        run[k] = (not inreset) and nrst > 0.7 * vdd[k]
    return run


def power_metrics(d, t_from=0.0):
    t = d['time']
    m = t >= t_from
    v33, vdda, v5, v5s = d['v(v33)'], d['v(vdda)'], d['v(v5)'], d['v(v5s)']
    live = m & (np.maximum(vdda, v33) > 1.0)
    diff = vdda - v33
    dt = np.gradient(t)
    over = live & (np.abs(diff) > F1_DIFF)
    run4 = reset_model(t, v33, F4_BOR_FALL, F4_BOR_RISE)
    run1 = reset_model(t, v33, F1_PDR_FALL, F1_POR_RISE, cnrst=val('C116'))
    unsafe4 = m & run4 & (v33 < F4_VMIN_168)
    unsafe1 = m & run1 & (v33 < F1_VMIN)
    # a reset happened inside the window if the run mask went false after being true
    reset4 = bool(np.any(run4[:-1][m[:-1]] & ~run4[1:][m[:-1]]))
    return dict(dmax=float(np.max(diff[live])) if live.any() else 0.0,
                dmin=float(np.min(diff[live])) if live.any() else 0.0,
                tover=float(np.sum(dt[over])), v33min=float(np.min(v33[m])), v5min=float(np.min(v5[m])),
                v5smin=float(np.min(v5s[m])), vddamin=float(np.min(vdda[m])),
                unsafe4=float(np.sum(dt[unsafe4])), unsafe1=float(np.sum(dt[unsafe1])), reset4=reset4,
                run4_end=bool(run4[-1]), run1_end=bool(run1[-1]))


def monotonic(t, v, t1, t2, tol=0.02):
    m = (t >= t1) & (t <= t2)
    x = v[m]
    return float(np.max(np.maximum.accumulate(x) - x)) if len(x) else 0.0


def iso_crank(us6, us, t8=0.5, tr=0.1, ub=12.0):
    """ISO 16750-2 starting profile as a PWL (board first powered from 0 V at 1 ms)."""
    t0 = 0.03
    pts = [(0, 0), (1e-3, 0), (1.1e-3, ub), (t0, ub), (t0 + 5e-3, us6), (t0 + 20e-3, us6), (t0 + 70e-3, us),
           (t0 + 70e-3 + t8, us), (t0 + 70e-3 + t8 + tr, ub), (t0 + 70e-3 + t8 + tr + 0.03, ub)]
    return ' '.join(f'{a:.6g} {b:.6g}' for a, b in pts), pts[-1][0], t0


iso_crank_pwl_II, iso_crank_stop_II, _ = iso_crank(4.5, 6.5)


# -- P1/P2: power-up: main relay closes (12.6 V step) and a slow 100 ms ramp (weak battery / bench supply)
for label, pwl, tstop, tmax in (('main relay closes onto 12.6 V', '0 0 1m 0 1.05m 12.6 40m 12.6', '40m', '5u'),
                                ('slow ramp 0 -> 13.5 V in 100 ms', '0 0 100m 13.5 140m 13.5', '140m', '20u')):
    d = spice('pwr_up', power_net(pwl, tstop, tmax), PV)
    dw = spice('pwr_up_w', power_net(pwl, tstop, tmax, vdo=LDO['vdo_max']), PV)
    pmw = power_metrics(dw)
    t = d['time']
    mono = {n: monotonic(t, d[f'v({k})'], 0, t[-1]) for n, k in (('+5V', 'v5'), ('+3V3', 'v33'),
                                                                   ('VDDA', 'vdda'), ('V5_SENS', 'v5s'))}
    worst = max(mono.values())
    fin = {k: d[f'v({k})'][-1] for k in ('v5', 'v33', 'vdda', 'v5s')}
    record('Power-up', f'{label}: rails monotonic',
           f'+5V {fin["v5"]:.2f} V, +3V3 {fin["v33"]:.2f} V, VDDA {fin["vdda"]:.3f} V, V5_SENS {fin["v5s"]:.2f} V; '
           f'largest dip during the rise {worst * 1000:.0f} mV',
           'OK' if worst < 0.02 and abs(fin['v5'] - 5.0) < 0.1 else 'FAIL')
    pm = power_metrics(d)
    trk = (d['v(p12)'] > 5.6) & (t > t[-1] * 0.5)
    record('Power-up', f'{label}: TLS115 V5_SENS tracking +5V',
           f'|+5V - V5_SENS| {np.max(np.abs(d["v(v5)"][trk] - d["v(v5s)"][trk])) * 1000:.0f} mV in regulation '
           '(model: 5 mV tracking + output impedance; datasheet +-5 mV)', 'OK')
    worst = max(pm['dmax'], pmw['dmax'])
    record('Power-up', f'{label}: F103 VDDA - VDD (limit 300 mV)',
           f'VDDA (REF3033) leads VDD ({LDO["name"]}) by up to {pm["dmax"] * 1000:.0f} mV ({pmw["dmax"] * 1000:.0f} mV '
           f'with {LDO["vdo_max"]:g} V dropout), over 300 mV for {max(pm["tover"], pmw["tover"]) * 1000:.1f} ms',
           'OK' if worst < F1_DIFF else 'FAIL',
           f'REF3033 drops ~50 mV, {LDO["name"]} ~{LDO["vdo"]:g} V: while +5V rises the F103 VDDA leads its VDD by about '
           'the difference (STM32F103x8 datasheet: 300 mV max during power-up and operation)')
    if label.startswith('slow'):
        record('Power-up', f'{label}: F407 runs below 2.7 V after reset release',
               f'{pm["unsafe4"] * 1000:.1f} ms with NRST released and VDD < 2.7 V',
               'OK' if pm['unsafe4'] < 1e-4 else 'CHECK',
               'reset is released at BOR1 (~2.3 V); the core starts on the 16 MHz HSI (0 wait states, fine down to 1.8 V). '
               'Only a problem if the firmware reaches the 168 MHz PLL/flash-wait-state switch before VDD > 2.7 V')
    else:
        record('Power-up', f'{label}: soft-start and reset release',
               f'LMR14020 soft-start {T_SS * 1000:.1f} ms (C20 {val("C20") * 1e9:.0f} nF x 0.75 V / 3 uA); F407 NRST '
               f'(C15 100 nF, 40k pull-up) releases about {40e3 * val("C15") * math.log(1 / 0.3) * 1000:.1f} ms after VDD passes BOR1',
               'OK')

# -- reference: the rev 0.6 AMS1117 (about 1 V dropout) in the same slow ramp and ISO level II crank
if LDO['name'] != 'AMS1117':
    old = LDOS['AMS1117-3.3']
    d = spice('pwr_up_ams', power_net('0 0 100m 13.5 140m 13.5', '140m', '20u', vdo=old['vdo'], iq=old['iq'], clamp=False), PV)
    pm = power_metrics(d)
    dc = spice('pwr_crank_ams', power_net(iso_crank_pwl_II, iso_crank_stop_II, '50u', vdo=old['vdo_max'], iq=old['iq'],
                                          clamp=False), PV)
    pmc = power_metrics(dc, 0.03)
    record('Power-up', 'reference: rev 0.6 AMS1117-3.3 (1.0 V typ / 1.3 V max dropout)',
           f'slow ramp: VDDA - VDD up to {pm["dmax"] * 1000:.0f} mV; ISO level II crank: {pmc["dmax"] * 1000:.0f} mV, '
           f'+3V3 min {pmc["v33min"]:.2f} V', 'REF', 'what the LDL1117 replaced')

# steady state and supervisor/boot-pin facts
record('Power-up', 'steady state F103 VDDA - VDD (tolerances)',
       f'VDDA 3.294-3.306 V (REF3033) vs VDD {LDO["vmin"]:.3f}-{LDO["vmax"]:.3f} V ({LDO["name"]} over temp): '
       f'{(3.294 - LDO["vmax"]) * 1000:.0f} to {(3.306 - LDO["vmin"]) * 1000:.0f} mV', 'OK')
rfb = 0.1      # BLM18PG221SN1 DC resistance, about 0.1 ohm max (Murata, recalled; assumed)
record('Power-up', 'F407 VDDA vs VDD (FB1 ferrite, DS8626: VDDA connected to VDD)',
       f'{rfb * 0.015 * 1000:.1f} mV at an assumed 15 mA VDDA current; C11/C12 on VDDA charge with VDD', 'OK')
on('R1', 'BOOT0', 'GND'); on('R129', 'WB_BOOT0', 'GND'); on('R72', 'BOOT1', 'GND'); on('R135', 'WB_BOOT1', 'GND')
record('Power-up', 'BOOT0 / BOOT1 pull-downs (R1, R72; R129, R135)',
       f'{1e-6 * val("R1") * 1000:.0f} mV with 1 uA pin leakage (STM32 Ilkg); F103 BOOT0 = R129 10k while the F407 '
       'PD10 floats through its reset: boots from flash', 'OK')

# -- P3: cold crank, ISO 16750-2 starting profile. Levels as recalled from ISO 16750-2:2012 Table 4 (not checked
# against the standard text): tf 5 ms, t6 15 ms at US6, t7 50 ms to US, then t8 at US (shortened here to 0.5 s: the
# rails are in steady state by then), tr 100 ms back to 12 V. I: 8/9.5 V, II: 4.5/6.5 V, III: 3/5 V, IV: 6/6.5 V.
for lvl, us6, us in (('I', 8.0, 9.5), ('II', 4.5, 6.5), ('III', 3.0, 5.0), ('IV', 6.0, 6.5)):
    pwl, tstop, t0 = iso_crank(us6, us)
    rows = []
    for vdo in (LDO['vdo'], LDO['vdo_max']):
        d = spice('pwr_crank', power_net(pwl, tstop, '50u', vdo=vdo), PV)
        rows.append((vdo, d, power_metrics(d, t0)))
    (_, d, pt), (_, dw, pw) = rows
    v12min = float(np.min(d['v(p12f)'][d['time'] >= t0]))
    reset = pt['reset4'] or pw['reset4']
    diffbad = max(pt['dmax'], pw['dmax'])
    window = max(pt['unsafe4'], pw['unsafe4'])
    note = []
    if diffbad > F1_DIFF:
        note.append(f'F103 VDDA - VDD up to {diffbad * 1000:.0f} mV (limit 300)')
    if window > 1e-4:
        note.append(f'F407 runs {window * 1000:.0f} ms with VDD between BOR1 and 2.7 V (above its reset threshold, below '
                    'the 2.7 V its 168 MHz flash setting needs)')
    if pt['v5min'] < 4.5:
        note.append(f'+5V {pt["v5min"]:.2f} V: TC4427 (4.5 V min) and SN74LVC4245A port A (4.5 V min) below their rated supply')
    if reset:
        note.append('board resets (VDD < BOR1) and restarts on recovery')
    verdict = 'FAIL' if diffbad > F1_DIFF else ('CHECK' if window > 1e-4 or pt['v5min'] < 4.5 else 'OK')
    record('Cold crank', f'ISO 16750-2 level {lvl}: {us6:g} V for 15 ms, {us:g} V for 0.5 s',
           f'+12V_F min {v12min:.2f} V, +5V {pt["v5min"]:.2f} V, +3V3 {pt["v33min"]:.2f} V '
           f'({pw["v33min"]:.2f} V with {LDO["vdo_max"]:g} V LDO dropout), VDDA {pt["vddamin"]:.2f} V, V5_SENS {pt["v5smin"]:.2f} V; '
           f'{"reset" if reset else "no reset"}', verdict, '; '.join(note))

record('Cold crank', 'sensor supply in a level II dip (ADC reference stays at 3.3 V)',
       'V5_SENS follows +12V minus the TLS115 dropout, so ratiometric sensors (MAP, TPS, MAF) read low by the same '
       'ratio while it is below 5 V (see the level II row)', 'OK',
       'normal for an ECU whose sensor supply drops out with the battery; the firmware reads CLT-based cranking fuel')

# -- P4: slow brown-out and key-off
d = spice('pwr_brown', power_net('0 0 1m 0 1.1m 12.6 50m 12.6 1.55 2.5 3.05 12.6 3.1 12.6', '3.1', '200u'), PV)
pm = power_metrics(d, 0.05)
record('Brown-out', 'battery 12.6 -> 2.5 -> 12.6 V over 3 s',
       f'F407 resets: {"yes" if pm["reset4"] else "no"}; {pm["unsafe4"] * 1000:.0f} ms running with VDD between BOR1 and '
       f'2.7 V; F103 VDDA - VDD up to {pm["dmax"] * 1000:.0f} mV; recovers: {"yes" if pm["run4_end"] and pm["run1_end"] else "no"}',
       'FAIL' if pm['dmax'] > F1_DIFF else ('CHECK' if pm['unsafe4'] > 1e-3 else 'OK'),
       'with rusEFI BOR level 1 the F407 keeps running (5 flash wait states, rated for 2.7 V+) while +3V3 passes '
       '2.3-2.7 V; BOR level 3 (2.7 V) would reset it cleanly instead' if pm['unsafe4'] > 1e-3 else '')
# Logic supply current against F1's hold rating. Assumed, not measured: 80 mA of 5 V loads besides the 3.3 V rail (CAN
# transceivers, wideband analog, igniter drive, shifters), the buck at 82 % at 2.2 MHz, 0.10 A straight from +12V
# (the two sensor-supply trackers and their sensors), and a polymer fuse holding 55 % of its 25 C rating at 85 C.
_p5 = V5_NOM * (I33 + 0.08)
_iin = {v: _p5 / 0.82 / (v - 0.5) + 0.10 for v in (13.8, 8.0, 6.0)}
_hold85 = 0.55 * F1_HOLD_A
record('Power', f'logic supply current through F1 ({DB["F1"]["value"]}, {F1_HOLD_A:.1f} A hold at 25 C, about {_hold85:.2f} A at 85 C)',
       f'{_iin[13.8]:.2f} A at 13.8 V, {_iin[8.0]:.2f} A at 8 V, {_iin[6.0]:.2f} A at 6 V (cranking), with {I33 * 1000:.0f} mA on +3V3'
       + (' (card writing)' if 'J4' in DB else ''),
       'OK' if _iin[6.0] < _hold85 else 'CHECK',
       f'margin at 6 V and 85 C: {_hold85 / _iin[6.0]:.1f}x; the load figures are estimates'
       + ('' if _iin[6.0] < _hold85 else ': a hot ECU with a weak crank could trip the fuse'))
d = spice('pwr_off', power_net('', '60m', '5u', keyoff=0.03), PV)
pm = power_metrics(d, 0.03)
t = d['time']
m = t > 0.03
t5 = t[m][np.argmax(d['v(v5)'][m] < 4.5)] - 0.03
t33 = t[m][np.argmax(d['v(v33)'][m] < F4_BOR_FALL)] - 0.03
record('Key-off', 'main relay opens (12.6 V removed, VBAT_IN loaded by the motherboard)',
       f'+5V < 4.5 V after {t5 * 1000:.1f} ms, F407 reset (VDD < BOR1) after {t33 * 1000:.1f} ms; F103 VDDA - VDD up to '
       f'{pm["dmax"] * 1000:.0f} mV on the way down', 'FAIL' if pm['dmax'] > F1_DIFF else 'OK',
       'decay is monotonic; D7 blocks back-feed into VBAT_IN. The VDDA lead repeats in reverse at every key-off')

# =================================================================================================================
# O. Outputs per motherboard into car loads
# =================================================================================================================
# Rev 0.8: ST VND7NV04 (OMNIFET II, DPAK; datasheet DocID 7381, as extracted): clamp 40/45/55 V; Rds(on) at VIN 5 V
# 60 mOhm max at 25 C, 120 mOhm max over -40..150 C; current limit 6/9/12 A (VIN 5 V, VDS 13 V); EAS 200 mJ (25 C);
# thermal shutdown 150/175/200 C; RthJC 2.1 C/W; RthJA 65 C/W on a small single-sided pad, about 30-90 C/W over the
# datasheet's copper-area curve. (Rev 0.7: NCV8406A, SOT-223, 240/520 mOhm.) The variable names stay NCV_*.
NCV_RDS25, NCV_RDS150, NCV_ILIM25, NCV_ILIM150, NCV_EAS, NCV_RTH, NCV_TSD = 0.06, 0.12, 6.0, 5.0, 0.200, 65.0, 150.0
NCV_CLAMP_MIN = 40.0
DRV_NAME = DB['Q1']['value']
assert DRV_NAME.startswith('VND7NV04'), DRV_NAME
for i, n in enumerate(design.HS_OUT):
    on(f'Q{1 + i}', n + '_IN', 'OUT_' + n, 'GND')
# Harness and motherboard path (assumed): JD1 socket contact + motherboard trace 30 mOhm, harness wire to the load
# and back 50 mOhm, the car's fuse/relay feed 50 mOhm.
R_MB, R_HARN = 0.03, 0.05


# Board temperature model (board_thermal.py): every copper layer of the routed board, the vias, the losses of all the
# other parts. Run without the header pins as a heat path (the pessimistic variant) at h = 10 W/m2K. The base load is
# sustained 7200 rpm with 20 mH injectors: "seq" sequential, "batch" the 1989-93 wiring, "batch_hog" the same with one
# TVS of each pair taking both injectors' energy. Temperatures are quoted for 60 and 85 C air around the board.
import board_thermal as BT
DB_BOARD = os.environ.get('DB_BOARD') or os.path.join(os.path.dirname(__file__), '../../daughterboard/miata_ecu_daughter.kicad_pcb')
TM = BT.Model(DB_BOARD, h=10.0, pins=False)
_therm = {}


def thermal(ref, case='seq'):
    """(rise at the part's heat pads from everything else on the board in this load case, C; C/W of its own loss,
    junction to air)"""
    if (ref, case) not in _therm:
        others = dict(BT.losses(case))
        others[ref] = 0.0
        _therm[(ref, case)] = (TM.rise(others)[ref][1], TM.rise({ref: 1.0})[ref][2])
    return _therm[(ref, case)]


def ncv_tj(irms, ta=85.0, pextra=0.0, ref='Q1', case='seq', typ=False):
    """Junction temperature with Rds(on) rising linearly from its 25 C to its 150 C value (max; typ=True: 0.7 x max).
    Above 150 C the part is in (or near) thermal shutdown."""
    k = 0.7 if typ else 1.0
    r25, r150 = k * NCV_RDS25, k * NCV_RDS150
    t0, kself = thermal(ref, case)
    tj = ta
    for _ in range(50):
        rds = r25 + (r150 - r25) * max(0.0, min(tj, 200) - 25) / 125
        tj = ta + t0 + kself * (irms ** 2 * rds + pextra)
    return tj


def fmt_tj(t):
    return f'{t:.0f} C' if t < NCV_TSD else '>150 C (shutdown)'


# Up to rev 0.9 each driver was judged on its own from its drain copper and a single-sided copper-area curve
# (rth_board below, still used for the 1989-93 motherboard's D3/D4 with a rev 0.9 daughterboard). The board model above
# replaces that for the daughterboard.
def rth_board(area_mm2):
    if area_mm2 <= 0:
        return NCV_RTH
    return max(30.0, min(90.0, 90.0 - 14.5 * math.log(area_mm2 / 10.0)))


def tvs_copper_area():
    """1989-93 D3/D4 cathode islands (scripts/mb_tvs_copper.py) on the released motherboard: effective mm^2 of the
    smaller one (F.Cu + half of B.Cu), or 0 if the board has none"""
    root = os.path.join(os.path.dirname(__file__), '../..')
    for brd in ('motherboards/1989-93/miata_mb_8993.kicad_pcb', 'mb/release_8993/miata_mb_8993.kicad_pcb'):
        try:
            import pcbnew
            b = pcbnew.LoadBoard(os.path.join(root, brd))
        except Exception:
            continue
        eff = []
        for nn in ('OUT_INJ1', 'OUT_INJ2'):
            a = {pcbnew.F_Cu: 0.0, pcbnew.B_Cu: 0.0}
            for z in b.Zones():
                if z.GetNetname() == nn and z.GetLayer() in a:
                    a[z.GetLayer()] += z.GetFilledArea() / 1e12
            eff.append(a[pcbnew.F_Cu] + 0.5 * a[pcbnew.B_Cu])
        if min(eff) > 0:
            return min(eff)
    return 0.0


A_TVS = tvs_copper_area()
# SMC on its bare pads: 75 C/W (Littelfuse SMCJ); with a cathode island, the same spreading estimate as the drivers
TVS_RTH = 75.0 if A_TVS <= 0 else min(75.0, rth_board(A_TVS))


def tj2(irms, pextra=0.0, ref='Q1', case='seq'):
    """(Tj at 60 C, Tj at 85 C air around the board) from the board model"""
    return ncv_tj(irms, 60, pextra, ref, case), ncv_tj(irms, 85, pextra, ref, case)


def tj_txt(t, ref='Q1', case='seq'):
    t0, kself = thermal(ref, case)
    return (f'Tj {fmt_tj(t[0])} at 60 C / {fmt_tj(t[1])} at 85 C air (board model: +{t0:.0f} C from the rest of the '
            f'board, {kself:.0f} C/W of its own)')


def tvs_tj(case):
    """hottest clamp TVS junction rise (C) and its loss (W) in a load case"""
    res = TM.rise(BT.losses(case))
    ref = max((f'D{46 + i}' for i in range(4)), key=lambda r: res[r][2])
    return res[ref][2], res[ref][0]


def ncv_block(node, gate, bv=NCV_CLAMP_MIN, rds=NCV_RDS25, ilim=NCV_ILIM25, tag=''):
    """Protected low side: current-limited switch, active clamp (a drain-ground breakdown diode at its minimum
    voltage, which puts the most energy into it), body diode."""
    return f"""Vdi{tag} {node} d{tag} 0
Bq{tag} d{tag} 0 I = V({gate}) > 2.5 ? min({ilim}, V(d{tag})/{rds}) : 0
Dcl{tag} 0 cl{tag} dncv{tag}
Vcl{tag} d{tag} cl{tag} 0
.model dncv{tag} d(bv={bv} ibv=2m is=1e-14 rs=0.3)
Dby{tag} 0 d{tag} dss34"""


INJ_R, INJ_L = 12.0, 8e-3    # Miata high-impedance injector: 12-14 ohm (12 = worst current); 8 mH assumed


def injector_single(vb=14.4):
    net = f"""* injector on one low-side driver
Vb vb 0 {vb}
Rh vb a {R_HARN}
Rl a b {INJ_R}
Ll b w {INJ_L}
Rw w out {R_MB}
Vg g 0 PULSE(0 5 0.1m 1u 1u 6m 100m)
{ncv_block('out', 'g')}
{MODELS}
""" + tran_ctl('0.5u', '9m')
    d = spice('inj1', net, ['v(out)', 'i(Vcl)', 'i(Vdi)'])
    t = d['time']
    e = energy(t, d['v(out)'], d['i(Vcl)'])
    ion = pin_avg(t, d['i(Vdi)'], 5.5e-3, 6.0e-3)
    return e, ion, float(np.max(d['v(out)']))


def injector_pair(vb=14.4, skew_us=2.0, tvs='d30max'):
    """1989-93: two injectors on 2U, INJ1 + INJ4 (through R23) in parallel, D3 on the motherboard node (SMCJ30A from
    rev 0.8, at the top of its breakdown range: the corner where the drivers' own clamps take the most)."""
    net = f"""* 1989-93 paired injectors
Vb vb 0 {vb}
Rh vb a {R_HARN}
Rl1 a b1 {INJ_R}
Ll1 b1 w {INJ_L}
Rl2 a b2 {INJ_R}
Ll2 b2 w {INJ_L}
Rw w mb {R_MB}
Dtv 0 tv {tvs}
Vtv mb tv 0
Rs0 mb o0 0.01
Rs1 mb o1 0.02
Vg0 g0 0 PULSE(0 5 0.1m 1u 1u 6m 100m)
Vg1 g1 0 PULSE(0 5 0.1m 1u 1u {6e-3 + skew_us * 1e-6} 100m)
{ncv_block('o0', 'g0', tag='0')}
{ncv_block('o1', 'g1', tag='1')}
{MODELS}
""" + tran_ctl('0.5u', '9m')
    d = spice('injp', net, ['v(mb)', 'i(Vcl0)', 'i(Vcl1)', 'i(Vtv)', 'i(Vdi0)', 'i(Vdi1)'])
    t = d['time']
    return (energy(t, d['v(mb)'], d['i(Vcl0)']) + energy(t, d['v(mb)'], d['i(Vcl1)']),
            energy(t, d['v(mb)'], d['i(Vtv)']), pin_avg(t, d['i(Vdi0)'], 5.5e-3, 6e-3),
            pin_avg(t, d['i(Vdi1)'], 5.5e-3, 6e-3), float(np.max(d['v(mb)'])))


def pwm_coil(r, l, f, duty, vb=14.4, diode=True, rfeed=R_HARN, cycles=None, name='pwm'):
    """PWM coil on a low-side driver, freewheel diode (motherboard D1/D2, SS34) from OUT to the coil's own feed, after
    any feed PTC. Returns driver rms current, clamp power, diode power, feed rms current, mean coil current."""
    T = 1 / f
    tau = l / r
    cycles = cycles or max(12, int(math.ceil(6 * tau / T)) + 4)
    fw = 'Dfw out fwx dss34\nVdf fwx feedx 0' if diode else ''
    net = f"""* PWM coil
Vb vb 0 {vb}
Rf vb feed {rfeed}
Vfi feed feedx 0
Rl feedx b {r}
Ll b w {l}
Rw w out {R_MB}
{fw}
Vg g 0 PULSE(0 5 0 1u 1u {duty * T} {T})
{ncv_block('out', 'g')}
{MODELS}
""" + tran_ctl(T / 400, cycles * T)
    vec = ['v(out)', 'i(Vcl)', 'i(Vdi)', 'i(Vfi)'] + (['i(Vdf)'] if diode else [])
    d = spice(name, net, vec)
    t = d['time']
    m = t >= t[-1] - 3 * T
    tt = t[m]
    span = tt[-1] - tt[0]
    rms = lambda x: math.sqrt(integ(tt, x[m] ** 2) / span)
    pcl = energy(tt, d['v(out)'][m], d['i(Vcl)'][m]) / span
    pd = 0.0
    if diode:
        idf = d['i(Vdf)'][m]
        # SS34 forward drop from the model (n 1.1, Is 5 uA, 30 mOhm)
        vf = np.where(idf > 0, 1.1 * 0.02585 * np.log(np.maximum(idf, 1e-9) / 5e-6 + 1) + 0.03 * idf, 0)
        pd = integ(tt, vf * idf) / span
    icoil = integ(tt, d['i(Vfi)'][m] + (d['i(Vdf)'][m] if diode else 0)) / span
    return rms(d['i(Vdi)']), pcl, pd, rms(d['i(Vfi)']), icoil, float(np.max(d['v(out)']))


# Relay / lamp / tach outputs, rev 0.8: Diodes ZXMS6004FF IntelliFET per channel (SOT-23F; datasheet as extracted):
# Rds(on) at VIN 5 V 350/500 mOhm (25 C typ/max; about x1.6 at 150 C, assumed from the family's curve); current limit
# 1.0/2.2 A min/typ at VIN 5 V; drain clamp 60/65/70 V; EAS 90 mJ (25 C, 0.5 A); thermal shutdown 150-175 C; RthJA
# 150 C/W on a 15 x 15 mm board (83 C/W on 50 x 50 mm). Gates at 5 V from the second SN74LVC4245A (U12).
RLY = ['FP', 'MAINRLY', 'AC', 'FAN', 'CEL', 'TACH', 'LS7']
for i, n in enumerate(RLY):
    q = DB[f'Q{9 + i}']
    assert q['value'] == 'ZXMS6004FFTA' and q['pads'] == {'1': n + '_G', '2': 'GND', '3': 'OUT_' + n}, (n, q)
    if n == 'CEL':      # rev 0.10: gate straight from the processor pin through 1k (3.3 V drive, outside the driver enable)
        on('R160', 'CEL_CTL', 'CEL_G')
        assert DB['U12']['pads'][str(10 - i)] == '' and DB['U12']['pads'][str(14 + i)] == 'GND'
        continue
    assert DB['U12']['pads'][str(10 - i)] == n + '_G' and DB['U12']['pads'][str(14 + i)] == n + '_CTL'
assert 'U5' not in DB and 'D11' not in DB
ZX_R25, ZX_R150, ZX_ILIM_MIN, ZX_ILIM_TYP, ZX_CLMAX, ZX_EAS, ZX_RTH, ZX_TSD = 0.5, 0.8, 1.0, 2.2, 70.0, 0.090, 150.0, 150.0


def zx_tj(i, ta, duty=1.0):
    tj = ta
    for _ in range(50):
        r = ZX_R25 + (ZX_R150 - ZX_R25) * max(0.0, min(tj, 175) - 25) / 125
        tj = ta + ZX_RTH * i * i * r * duty
    return tj


def zx_load(kind, vb=14.4):
    """dict(ion, p, tj60, tj85, peak_i, vpk_off, e_off) for one IntelliFET channel"""
    rload = {'relay': 70.0, 'vics': 35.0, 'lamp': 14.0 ** 2 / 3.4, 'lamp1': 14.0 ** 2 / 1.4, 'tach': 3300.0}[kind]
    lind = {'relay': 0.3, 'vics': 0.05}.get(kind, 0.0)
    ion = vb / (rload + ZX_R150 + R_HARN)
    peak = ion
    if kind.startswith('lamp'):
        peak = min(ZX_ILIM_TYP, vb / (rload / 12))      # cold filament ~1/12 of hot (assumed), held at the limit
    e_off = 0.5 * lind * ion ** 2 * ZX_CLMAX / (ZX_CLMAX - vb) if lind else 0.0
    return dict(ion=ion, p=ion ** 2 * ZX_R150, tj60=zx_tj(ion, 60), tj85=zx_tj(ion, 85), peak_i=peak,
                vpk_off=ZX_CLMAX if lind else vb, e_off=e_off)


zx = {k: zx_load(k) for k in ('relay', 'vics', 'lamp', 'lamp1', 'tach')}


# Ignition outputs, rev 0.8: TC4427 (15 ohm at 5 V, assumed) -> R15-R18 100 ohm (1206) -> B5819W source diode -> OUT,
# ZXMS6004FF from OUT to ground with its gate the inverted control line (74HCT04), and R144-R147 (1206) from OUT to ground.
# Igniter input (Mazda NA igniter / NB coil with built-in igniter): not published; assumed a bipolar input, two Vbe
# (1.2 V) behind 220 ohm (heavy) to 2.2 kohm (light), or a CMOS input (10 kohm), harness 1 nF.
for k, n in enumerate(['IGN1', 'IGN2', 'IGN3', 'IGN4']):
    on(f'R{15 + k}', n + '_DRV', n + '_SRC')
    on(f'D{31 + k}', 'OUT_' + n, n + '_SRC')
    on(f'Q{16 + k}', n + '_SNK', 'GND', 'OUT_' + n)
    on(f'R{144 + k}', 'OUT_' + n, 'GND')
R_IGN = val('R15')
R_IGN_PD = val('R144')


def igniter(rin, v5=5.0, cmos=False):
    """TC4427 -> 100 R -> Schottky -> OUT (R144 pull-down, IntelliFET pull-down 15 us after the falling edge) ->
    igniter. Returns (high level, input current, rise time 10-90 %, fall time to 1.2 V after the control edge)."""
    load = f'Rin hp 0 10k' if cmos else f'Rin hp ib {rin}\nD1 ib x dbe\nD2 x 0 dbe'
    net = f"""* ignition output stage
V5 v5 0 {v5}
Vg g 0 PULSE(0 1 0.1m 10n 10n 3m 10m)
Bo drv 0 V = V(g) > 0.5 ? V(v5) : 0
Ro drv o1 15
R15 o1 src {R_IGN}
Ds src hp dss14
.model dss14 d(is=1e-6 n=1.05 rs=0.08)
Rpd hp 0 {R_IGN_PD}
Ch hp 0 1n
Vgs gs 0 PULSE(1 0 0.1m 10u 10u 3.015m 10m)
Sq hp 0 gs 0 sq
.model sq sw(vt=0.5 ron=0.8 roff=100meg)
{load}
{MODELS}
""" + tran_ctl('0.05u', '3.2m')
    d = spice('ign', net, ['v(hp)', 'i(V5)'])
    t, v = d['time'], d['v(hp)']
    vh = pin_avg(t, v, 2e-3, 3e-3)
    t10 = t[np.argmax(v > 0.1 * vh)]
    t90 = t[np.argmax(v > 0.9 * vh)]
    tf = t[(t > 3.1e-3) & (v < 1.2)]
    fall = (tf[0] - 3.1e-3) if len(tf) else float('inf')
    iin = (vh - 1.2) / rin if not cmos else vh / 10e3
    return vh, iin, t90 - t10, fall


# ---- per-year load assignment (function of each OUT_ net on that year's harness) ---------------------------------
LOADS = {
    '1989-93': {'OUT_INJ1': 'inj_pair', 'OUT_INJ2': 'inj_pair', 'OUT_IACV': 'iacv', 'OUT_VVT': 'purge',
                'OUT_IGN1': 'igniter', 'OUT_IGN2': 'igniter', 'OUT_FP': 'relay', 'OUT_AC': 'relay',
                'OUT_FAN': 'relay', 'OUT_LS7': 'relay', 'OUT_CEL': 'lamp'},      # no tach: 2I is the igniter's output (JP5 open)
    '1994-95': {'OUT_INJ1': 'inj', 'OUT_INJ2': 'inj', 'OUT_INJ3': 'inj', 'OUT_INJ4': 'inj', 'OUT_IACV': 'iacv',
                'OUT_VVT': 'purge', 'OUT_ALT': 'prc', 'OUT_IGN1': 'igniter', 'OUT_IGN2': 'igniter',
                'OUT_FP': 'relay', 'OUT_AC': 'relay', 'OUT_FAN': 'relay', 'OUT_LS7': 'relay', 'OUT_CEL': 'lamp'},
    '1996-97': {'OUT_INJ1': 'inj', 'OUT_INJ2': 'inj', 'OUT_INJ3': 'inj', 'OUT_INJ4': 'inj', 'OUT_IACV': 'iacv',
                'OUT_VVT': 'o2htr', 'OUT_IGN1': 'igniter', 'OUT_IGN2': 'igniter', 'OUT_FP': 'relay',
                'OUT_AC': 'relay', 'OUT_FAN': 'relay', 'OUT_LS7': 'relay', 'OUT_CEL': 'lamp', 'OUT_TACH': 'tach'},
    '1999-2000': {'OUT_INJ1': 'inj', 'OUT_INJ2': 'inj', 'OUT_INJ3': 'inj', 'OUT_INJ4': 'inj', 'OUT_IACV': 'iacv',
                  'OUT_VVT': 'o2htr', 'OUT_ALT': 'field', 'OUT_IGN1': 'igniter', 'OUT_IGN2': 'igniter',
                  'OUT_FP': 'relay', 'OUT_AC': 'relay', 'OUT_FAN': 'relay', 'OUT_LS7': 'relay', 'OUT_CEL': 'lamp',
                  'OUT_TACH': 'tach', 'OUT_MAINRLY': 'vics'},
    '2001-05': {'OUT_INJ1': 'inj', 'OUT_INJ2': 'inj', 'OUT_INJ3': 'inj', 'OUT_INJ4': 'inj', 'OUT_IACV': 'iacv',
                'OUT_VVT': 'ocv', 'OUT_ALT': 'field', 'OUT_IGN1': 'igniter', 'OUT_IGN2': 'igniter',
                'OUT_FP': 'relay', 'OUT_AC': 'relay', 'OUT_FAN': 'relay', 'OUT_LS7': 'relay', 'OUT_CEL': 'lamp',
                'OUT_TACH': 'tach', 'OUT_MAINRLY': 'relay'},
}
for y, _ in YEARS:
    hn = {n for n in harness(y) if n.startswith('OUT_')}
    assert hn == set(LOADS[y]), f'{y}: harness outputs {sorted(hn)} vs simulated {sorted(LOADS[y])}'

# shared simulations (same circuit on several years), computed once
# Rev 0.10: each injector driver has its own clamp on the daughterboard (fast diode to an SMCJ14A that returns to the
# battery input), so the turn-off energy goes into that TVS, not into the driver or a motherboard TVS. The bench is
# sim_inj_clamp.py's. The injector inductance is not known (8 mH was assumed up to rev 0.9, a published fit for a similar
# injector gives 20 mH), so both ends are simulated and the verdicts use 20 mH.
for _i in range(4):
    on(f'D{42 + _i}', f'OUT_INJ{_i + 1}', f'INJ{_i + 1}_CL'); on(f'D{46 + _i}', f'INJ{_i + 1}_CL', 'VBAT_IN')
    assert DB[f'D{46 + _i}']['value'] in IC.PART_KEY and DB[f'R{152 + _i}']['value'] == '220'
TVS_PART = DB['D46']['value']
TVS_KEY = IC.PART_KEY[TVS_PART]
TVS_TJMAX = 185.0 if TVS_PART == 'TPSMC16A' else 150.0
INJ_LS = (8e-3, 20e-3)
inj_seq = {L: IC.bench(f'o_seq_{int(L * 1e3)}', 'BAT', L=L, tvs=TVS_KEY) for L in INJ_LS}
inj_pair = {L: IC.bench(f'o_pair_{int(L * 1e3)}', 'BAT', L=L, n_inj=2, n_drv=2, tvs=TVS_KEY) for L in INJ_LS}
inj_16 = IC.bench('o_seq_16V', 'BAT', L=8e-3, vb=16.0, tvs=TVS_KEY)
inj_open = IC.bench('o_tvs_open', 'BAT', L=20e-3, fault='tvs_open', tvs=TVS_KEY)   # a clamp part open: the driver takes it all
RPM = 7200
i1, i1_16, vpk1 = inj_seq[8e-3]['i0'], inj_16['i0'], inj_seq[20e-3]['vpk']
p_tvs_seq = {L: inj_seq[L]['e_tvs'] * RPM / 120 for L in INJ_LS}           # sequential: one pulse per 720 deg
p_tvs_bat = {L: inj_pair[L]['e_tvs'] / 2 * RPM / 60 for L in INJ_LS}       # batch: each wire once per revolution, two TVSs
p_seq = 0.0                    # clamp power in an injector driver with the clamp parts working
# idle valve (BAC/ISC): 11 ohm / 20 mH (typical published, as circuit_sim.py), 200 Hz (assumed), 60 % duty
iac = {feed: pwm_coil(11, 20e-3, 200, 0.6, rfeed=R_HARN + (0.1 if feed != 'VBAT_IN' else 0), name='iac')
       for feed in ('VBAT_IN', 'IAC_12V')}
ocv = pwm_coil(7.5, 6e-3, 300, 0.6, rfeed=R_HARN + 0.1, name='ocv')      # NB2 OCV 7.5 ohm / 6 mH (as circuit_sim)
purge = pwm_coil(30, 30e-3, 20, 0.5, name='purge')                         # purge solenoid 30 ohm / 30 mH, 20 Hz (assumed)
field = {D: pwm_coil(3.0, 0.2, 300, D, diode=False, cycles=120, name='field') for D in (0.5, 0.9)}   # assumed field
ign = {rin: igniter(rin) for rin in (220, 2200)}
ign_cmos = igniter(0, cmos=True)
ign_crank = igniter(220, v5=3.9)

# PRC solenoid (1994-95 2R on OUT_ALT, no freewheel diode): on/off, single turn-off into the clamp
net = f"""* PRC solenoid turn-off
Vb vb 0 14.4
Rl vb b 30
Ll b out 30m
Vg g 0 PULSE(0 5 0.1m 1u 1u 10m 100m)
{ncv_block('out', 'g')}
{MODELS}
""" + tran_ctl('1u', '13m')
d = spice('prc', net, ['v(out)', 'i(Vcl)'])
e_prc = energy(d['time'], d['v(out)'], d['i(Vcl)'])

# O2 heater on OUT_VVT (1996-97 3M, NB1 1U), DC on: narrowband heater assumed 3 ohm cold / 12 ohm hot (typical
# 12-18 W zirconia sensor heater; not measured on a Mazda sensor)
def o2_heater(rh, vb=14.4):
    i = vb / (rh + NCV_RDS25 + R_HARN + R_MB)
    lim = None
    for ilim, tj in ((NCV_ILIM25, 25), (NCV_ILIM150, 150)):
        if i > ilim:
            lim = (ilim, tj)
            break
    return i, lim


TEMPS = (60.0, 85.0)
for y, _ in YEARS:
    hn = harness(y)
    L = LOADS[y]
    cav = lambda n: '/'.join(hn[n])
    area = 'Out ' + y
    # injectors
    case = 'batch' if 'inj_pair' in L.values() else 'seq'
    tvs_txt = lambda r: f'{60 + r:.0f} / {85 + r:.0f} C at 60 / 85 C air'
    if case == 'batch':
        # 1989-93: jumpers JP1 / JP2 on PAIR put two drivers, each with its own clamp, on each two-injector wire
        on('R_JP2A', 'OUT_INJ1', 'OUT_INJ4', parts=MB[y]); on('R_JP1A', 'OUT_INJ2', 'OUT_INJ3', parts=MB[y])
        assert not MB[y]['D3']['lcsc'] and not MB[y]['D4']['lcsc'], 'motherboard D3/D4 are not fitted with a rev 0.10 daughterboard'
        pr = inj_pair[20e-3]
        tj = tj2(pr['i0'] / 2 * math.sqrt(0.9), case='batch')
        pw = p_tvs_bat[20e-3]
        (r_eq, _), (r_hog, p_hog) = tvs_tj('batch'), tvs_tj('batch_hog')
        record(area, f'injectors {cav("OUT_INJ1")}/{cav("OUT_INJ2")}: 2 x 12 ohm per wire, INJ1+INJ4 / INJ2+INJ3, batch',
               f'{pr["i0"] / 2:.2f} A per driver, peak {pr["vpk"]:.0f} V, nothing in the driver clamps ({pr["e_drv"] * 1e3:.2f} mJ); each '
               f'clamp TVS {p_tvs_bat[8e-3]:.2f} W (8 mH) to {pw:.2f} W (20 mH) at {RPM} rpm; drivers at 90 % duty: {tj_txt(tj, case="batch")}',
               'OK' if pr['vpk'] < 36 and pr['e_drv'] < 1e-4 and tj[1] < NCV_TSD - 15 and 85 + r_hog < TVS_TJMAX else 'CHECK',
               f'clamp TVSs ({TVS_PART}, {TVS_TJMAX:.0f} C rated) at 20 mH, sustained {RPM} rpm: {tvs_txt(r_eq)} if the two on a wire '
               f'share equally; {tvs_txt(r_hog)} if one takes both injectors ({p_hog:.1f} W: its breakdown is the lower one, '
               f'sim_inj_clamp.py section I). The injector inductance is not known')
    else:
        tj = tj2(i1 * math.sqrt(0.9))
        pins = '/'.join(cav(f'OUT_INJ{k}') for k in range(1, 5))
        pw = p_tvs_seq[20e-3]
        r_seq, _ = tvs_tj('seq')
        record(area, f'injectors {pins}: 12 ohm each, sequential',
               f'{i1:.2f} A ({i1_16:.2f} A at 16 V; limit >= {NCV_ILIM150:.1f} A hot), clamp peak {vpk1:.0f} V (driver clamp from '
               f'36 V), each clamp TVS {p_tvs_seq[8e-3]:.2f} W (8 mH) to {pw:.2f} W (20 mH) at {RPM} rpm: Tj {tvs_txt(r_seq)} '
               f'({TVS_PART}, {TVS_TJMAX:.0f} C rated); drivers, conduction only, 90 % duty, max Rds(on): {tj_txt(tj)}',
               'OK' if vpk1 < 36 and tj[1] < NCV_TSD - 15 and i1_16 < NCV_ILIM150 and 85 + r_seq < TVS_TJMAX else 'CHECK',
               f'a clamp part open: the driver takes {inj_open["e_drv"] * 1e3:.1f} mJ per pulse (20 mH) = '
               f'{inj_open["e_drv"] * RPM / 120:.2f} W at {RPM} rpm, {tj_txt(tj2(i1 * math.sqrt(0.9), pextra=inj_open["e_drv"] * RPM / 120))}')
    # idle valve
    feed = MB[y]['D1']['pads']['1']
    on('D1', 'OUT_IACV', parts=MB[y])
    irms, pcl, pd, ifeed, icoil, vpk = iac[feed]
    tj = tj2(irms, pextra=pcl, ref='Q5', case=case)
    fuse = f', feed {feed} through {next(r for r, p in MB[y].items() if r.startswith("F") and feed in p["pads"].values())} (2 A hold): {ifeed:.2f} A rms' \
        if feed != 'VBAT_IN' else ''
    record(area, f'idle valve {cav("OUT_IACV")}: 11 ohm / 20 mH, 200 Hz 60 %, D1 to {feed}',
           f'driver {irms:.2f} A rms, clamp {pcl * 1000:.0f} mW, {tj_txt(tj, "Q5", case)}; D1 {pd:.2f} W{fuse}',
           'OK' if pcl < 0.05 and tj[1] < NCV_TSD and ifeed < 2.0 else 'CHECK')
    # VVT driver: purge / O2 heater / OCV
    kind = L['OUT_VVT']
    if kind == 'purge':
        irms, pcl, pd, ifeed, icoil, vpk = purge
        on('D2', 'OUT_VVT', 'VBAT_IN', parts=MB[y])
        record(area, f'purge solenoid {cav("OUT_VVT")} (VVT driver): 30 ohm / 30 mH, 20 Hz, D2 to VBAT_IN',
               f'{irms:.2f} A rms, clamp {pcl * 1000:.0f} mW, D2 {pd * 1000:.0f} mW', 'OK' if pcl < 0.05 else 'CHECK',
               'not driven by the shipped firmware (no purge strategy assigned); load assumed')
    elif kind == 'o2htr':
        assert 'D2' not in MB[y], 'O2 heater years have no D2'
        icold, lim = o2_heater(3.0)
        ihot, _ = o2_heater(12.0)
        tj = tj2(ihot, ref='Q6', case=case)
        lim_txt = (f'cold inrush {icold:.1f} A exceeds the {lim[0]:.1f} A minimum current limit at Tj {lim[1]} C: '
                   'the driver limits, heats and may cycle through thermal shutdown until the heater warms') if lim else \
            f'cold inrush {icold:.1f} A, under the {NCV_ILIM25:.1f} A minimum limit (25 C)'
        record(area, f'front O2 heater {cav("OUT_VVT")} (VVT driver), DC on: 3 ohm cold / 12 ohm hot (assumed)',
               f'hot {ihot:.2f} A continuous: {tj_txt(tj, "Q6", case)}; {lim_txt}',
               'OK' if tj[1] < NCV_TSD and not lim else 'CHECK',
               'heater resistance not published for the Mazda sensor: measure it' if tj[1] >= NCV_TSD or lim else '')
    else:
        irms, pcl, pd, ifeed, icoil, vpk = ocv
        on('D2', 'OUT_VVT', 'OCV_12V', parts=MB[y])
        tj = tj2(irms, pextra=pcl, ref='Q6', case=case)
        record(area, f'VVT oil control valve {cav("OUT_VVT")}: 7.5 ohm / 6 mH, 300 Hz 60 %, D2 to OCV_12V (F3)',
               f'driver {irms:.2f} A rms, {tj_txt(tj, "Q6", case)}, clamp {pcl * 1000:.0f} mW; D2 {pd:.2f} W; F3 {ifeed:.2f} A rms (2 A hold)',
               'OK' if tj[1] < NCV_TSD and pcl < 0.05 and ifeed < 2 else 'CHECK')
    # ALT driver
    if L.get('OUT_ALT') == 'prc':
        record(area, f'pressure regulator solenoid {cav("OUT_ALT")} (ALT driver): 30 ohm / 30 mH on/off, no diode',
               f'{e_prc * 1000:.1f} mJ per turn-off into the clamp (EAS 110 mJ)', 'OK' if e_prc < NCV_EAS / 4 else 'CHECK',
               'not assigned by the shipped firmware; load assumed')
    elif L.get('OUT_ALT') == 'field':
        f5, f9 = field[0.5], field[0.9]
        record(area, f'alternator field {cav("OUT_ALT")} (ALT driver, no freewheel): 3 ohm / 0.2 H assumed, 300 Hz',
               f'50 % duty: field {f5[4]:.2f} A, clamp {f5[1]:.1f} W; 90 % duty: field {f9[4]:.2f} A, clamp {f9[1]:.1f} W '
               f'(the board model allows this driver ~{(NCV_TSD - 85 - thermal("Q8", case)[0]) / thermal("Q8", case)[1]:.1f} W at 85 C air)',
               'CHECK' if max(f5[1], f9[1]) > 0.5 else 'OK',
               'if the PCM drives the field coil directly, without a freewheel diode every PWM turn-off dumps the field '
               'current into the 40-55 V clamp: the field current collapses below ~80 % duty and the driver overheats. '
               'Firmware ships alternator control off (VERIFICATION M5); fit a freewheel diode to the field supply and '
               'a larger driver before enabling it')
    # ignition
    record(area, f'igniter inputs {cav("OUT_IGN1")}/{cav("OUT_IGN2")}: TC4427 + 100 ohm + B5819W, ZXMS6004 + {DB["R144"]["value"]} pull-down',
           f'{ign[220][0]:.2f} V / {ign[220][1] * 1000:.1f} mA into 220 ohm + 2 Vbe, {ign[2200][0]:.2f} V into 2.2k, '
           f'{ign_cmos[0]:.2f} V into a 10k CMOS input; rise {ign[220][2] * 1e6:.1f} us; fall to 1.2 V '
           f'{ign[2200][3] * 1e6:.1f} us (2.2k input) / {ign_cmos[3] * 1e6:.1f} us (CMOS); at +5V = 3.9 V (crank) {ign_crank[0]:.2f} V',
           'OK' if ign_crank[0] > 2.0 and max(ign[2200][3], ign_cmos[3]) < 5e-6 else 'CHECK',
           'igniter input impedance assumed (not published). The fall time is the spark edge: '
           f'{max(ign[2200][3], ign_cmos[3]) * 1e6:.1f} us is {max(ign[2200][3], ign_cmos[3]) * 7200 * 6:.2f} deg at 7200 rpm')
    # relay / lamp / tach channels (one IntelliFET each)
    names = {'OUT_FP': 'fuel pump relay', 'OUT_AC': 'A/C relay', 'OUT_FAN': 'fan relay', 'OUT_LS7': 'fan 2 relay',
             'OUT_MAINRLY': 'main relay' if L.get('OUT_MAINRLY') == 'relay' else 'VICS solenoid',
             'OUT_CEL': 'CEL lamp', 'OUT_TACH': 'tach'}
    chans = [n for n in ('OUT_FP', 'OUT_AC', 'OUT_FAN', 'OUT_LS7', 'OUT_MAINRLY', 'OUT_CEL', 'OUT_TACH') if n in L]
    kinds = {n: L[n] for n in chans}
    hot = max(chans, key=lambda n: zx[kinds[n]]['tj85'])
    record(area, 'relay / lamp / tach switches (ZXMS6004FF each), every one on at 14.4 V: '
           + ', '.join(f'{names[n]} {cav(n)}' for n in chans),
           f'hottest {names[hot]}: {zx[kinds[hot]]["ion"] * 1000:.0f} mA, {zx[kinds[hot]]["p"] * 1000:.0f} mW, Tj '
           f'{zx[kinds[hot]]["tj60"]:.0f} C at 60 C / {zx[kinds[hot]]["tj85"]:.0f} C at 85 C ambient ({ZX_RTH:.0f} C/W)',
           'OK' if zx[kinds[hot]]['tj85'] < ZX_TSD - 15 else 'CHECK')
    if L.get('OUT_MAINRLY') == 'vics':
        u = zx['vics']
        record(area, f'VICS solenoid {cav("OUT_MAINRLY")} on a ZXMS6004FF: 35 ohm (assumed)',
               f'{u["ion"] * 1000:.0f} mA, {u["p"] * 1000:.0f} mW, Tj {u["tj85"]:.0f} C at 85 C ambient; turn-off '
               f'{u["e_off"] * 1000:.1f} mJ into the {ZX_CLMAX:.0f} V clamp (EAS {ZX_EAS * 1000:.0f} mJ)',
               'OK' if u['tj85'] < ZX_TSD - 15 and u['e_off'] < ZX_EAS / 4 else 'CHECK')

# year-independent relay-switch rows
u = zx['relay']
record('Out relays', 'relay coil 70 ohm / 0.3 H at 14.4 V on a ZXMS6004FF', f'{u["ion"] * 1000:.0f} mA, '
       f'{u["p"] * 1000:.0f} mW; turn-off {u["e_off"] * 1000:.1f} mJ into the {ZX_CLMAX:.0f} V max clamp (EAS '
       f'{ZX_EAS * 1000:.0f} mJ, 60 V continuous rating)', 'OK' if u['e_off'] < ZX_EAS / 4 else 'CHECK')
for k, w in (('lamp1', 1.4), ('lamp', 3.4)):
    u = zx[k]
    record('Out relays', f'CEL bulb {w} W (cold filament 1/12 of hot, assumed)',
           f'inrush held at the current limit ({u["peak_i"]:.2f} A typical, {ZX_ILIM_MIN:.1f} A minimum) for tens of ms, '
           f'then {u["ion"] * 1000:.0f} mA', 'OK',
           'the current limit and thermal shutdown take the cold filament; the ULN2003 had neither')
u = zx['tach']
record('Out relays', 'tach to the cluster (3.3k pull-up to 14.4 V, assumed)', f'{u["ion"] * 1000:.1f} mA, low '
       f'{u["ion"] * ZX_R150 * 1000:.0f} mV', 'OK',
       'cluster input not published; on 1989-95 check cavity 2I is not fed by the igniter (VERIFICATION pinout 6)')
record('Out relays', 'any relay / lamp / tach output shorted to battery while on',
       f'held at the current limit ({ZX_ILIM_MIN:.1f}-{ZX_ILIM_TYP:.1f} A) until thermal shutdown (150-175 C), then cycles; '
       f'no back-feed path into the board (no clamp diodes to a common rail)', 'OK')
record('Out ignition', 'ignition output shorted to battery (driver high or low)',
       'high: the B5819W blocks (no current into the TC4427 or +5V, none in the 100 R); low: the ZXMS6004FF limits '
       f'({ZX_ILIM_MIN:.1f}-{ZX_ILIM_TYP:.1f} A) and shuts down; R144-R147 {DB["R144"]["value"]}: {14.4 ** 2 / R_IGN_PD * 1000:.0f} mW at 14.4 V, '
       f'{24.0 ** 2 / R_IGN_PD * 1000:.0f} mW at 24 V (1206, 250 mW)', 'OK' if 24.0 ** 2 / R_IGN_PD < 0.25 * 1.1 else 'CHECK',
       '' if 24.0 ** 2 / R_IGN_PD < 0.25 * 1.1 else 'only in a 24 V jump start with the wire shorted')
record('Out ignition', 'ignition output shorted to ground while high',
       f'{5.0 / (15 + R_IGN) * 1000:.0f} mA from the TC4427, {(5.0 / (15 + R_IGN)) ** 2 * R_IGN * 1000:.0f} mW in the 1206 100 R '
       f'(250 mW)', 'OK' if (5.0 / (15 + R_IGN)) ** 2 * R_IGN < 0.25 else 'CHECK')

# =================================================================================================================
# I. Inputs per motherboard with real sensors
# =================================================================================================================
AN = ['TPS', 'MAP', 'CLT', 'IAT', 'AFR', 'AUX1', 'AUX2', 'AUX3']
DIV = {}
for n in AN:
    rs, rg = between('IN_' + n, 'AN_' + n), between('AN_' + n, 'GND')
    cf = between('AN_' + n, 'GND', 'C')
    DIV[n] = (sv(rs['value']), sv(rg['value']), sv(cf['value']))
V5_BIAS = 'V5_EXT' if any(set(p['pads'].values()) == {'V5_EXT', 'IN_CLT'} for p in DB.values()) else 'V5_SENS'
RPU_T = sv(between(V5_BIAS, 'IN_CLT')['value'])
assert sv(between(V5_BIAS, 'IN_IAT')['value']) == RPU_T
# F407 pins (DS8626 pin table, recalled): PA4/PA5 (TPS, MAP) TTa, the rest FT; all in analog mode -> VDDA + 0.3 V.
PIN = {'TPS': 'PA4', 'MAP': 'PA5', 'CLT': 'PA6', 'IAT': 'PA7', 'AFR': 'PC4', 'AUX1': 'PC5', 'AUX2': 'PB0', 'AUX3': 'PB1'}


def adc_net(copies):
    """copies: list of (name, source lines driving node in_<name>, divider key). Returns an .op netlist."""
    body = []
    for name, src, key in copies:
        rs, rg, cf = DIV[key]
        body.append(src.replace('@N@', name))
        body.append(f'Rs_{name} in_{name} an_{name} {rs}\nRg_{name} an_{name} 0 {rg}\nIlk_{name} an_{name} 0 1u')
    return '* analog inputs\nV5s v5s 0 5.0\n' + '\n'.join(body) + f'\n{MODELS}\n.op\n.control\nrun\n@PRINT@\n.endc\n.end\n'


def sh_coeffs(pts):
    (t1, r1), (t2, r2), (t3, r3) = pts
    L1, L2, L3 = math.log(r1), math.log(r2), math.log(r3)
    Y1, Y2, Y3 = 1 / (t1 + 273.15), 1 / (t2 + 273.15), 1 / (t3 + 273.15)
    U2, U3 = (Y2 - Y1) / (L2 - L1), (Y3 - Y1) / (L3 - L1)
    C = (U3 - U2) / (L3 - L2) / (L1 + L2 + L3)
    B = U2 - C * (L1 * L1 + L1 * L2 + L2 * L2)
    A = Y1 - (B + L1 * L1 * C) * L1
    return A, B, C


def r_of_t(coef, tc):
    A, B, C = coef
    lo, hi = math.log(10), math.log(1e7)
    for _ in range(80):
        mid = (lo + hi) / 2
        t = 1 / (A + B * mid + C * mid ** 3) - 273.15
        lo, hi = (mid, hi) if t > tc else (lo, mid)
    return math.exp((lo + hi) / 2)


# Mazda NA/NB coolant/air NTC as rusEFI's Miata presets (-20/40/80 C = 16150/1150/330 ohm); J3 "M12x1.5" sensor
# assumed GM-type (published GM table: -20 C 28680, 40 C 1459, 100 C 177 ohm).
NTC = {'Mazda (stock)': sh_coeffs([(-20, 16150), (40, 1150), (80, 330)])}
TEMPS_C = [-40, -20, 0, 20, 40, 60, 80, 90, 100, 110, 120, 130]
therm = {}
for sname, coef in NTC.items():
    copies = []
    for k, tc in enumerate(TEMPS_C):
        for dt in (0, 1):
            r = r_of_t(coef, tc + dt)
            copies.append((f't{k}_{dt}', f'Rpu_@N@ v5s in_@N@ {RPU_T}\nRth_@N@ in_@N@ 0 {r}', 'CLT'))
    res = spice_op('therm', adc_net(copies), [f'v(an_{c[0]})' for c in copies])
    therm[sname] = [(tc, res[f'v(an_t{k}_0)'], res[f'v(an_t{k}_0)'] - res[f'v(an_t{k}_1)'])
                    for k, tc in enumerate(TEMPS_C)]
LSB = 3.3 / 4096
open_v = 5.0 * DIV['IAT'][1] / (RPU_T + DIV['IAT'][0] + DIV['IAT'][1])
for sname, rows in therm.items():
    rng = (rows[0][1], rows[-1][1])
    res_c = {tc: LSB / dv for tc, v, dv in rows if dv > 0}
    worst = max(res_c[tc] for tc in (-20, 0, 20, 40, 60, 80, 90, 100, 110))
    record('In sensors', f'CLT/IAT, {sname}, -40..130 C',
           f'ADC {rng[0]:.2f} .. {rng[1]:.2f} V (open {open_v:.2f} V, short 0 V); resolution '
           f'{res_c[-20]:.2f} / {res_c[20]:.2f} / {res_c[90]:.2f} / {res_c[110]:.2f} C per LSB at -20/20/90/110 C',
           'OK' if worst < 0.5 and rng[0] < open_v - 0.1 and rng[1] > 0.05 else 'CHECK',
           ('GM-type needs its own coefficients in TunerStudio (the year presets assume the Mazda sensor); ' if 'GM' in sname
            else '') + (f'-40 C reads within {(open_v - rng[0]) * 1000:.0f} mV of an open circuit' if rng[0] > open_v - 0.1 else ''))
record('In sensors', 'air temperature sensor unplugged', f'IN_IAT open: reads {open_v:.2f} V = open-circuit sensor (about -50 C)',
       'OK', 'rusEFI flags it as a sensor fault rather than a plausible temperature')

# TPS: potentiometer, 5 kohm (assumed; Miata TPS track not published here), fed from V5_SENS
copies = [(f'x{k}', f'Rt1_@N@ v5s in_@N@ {5000 * (1 - x) + 1e-3}\nRt2_@N@ in_@N@ 0 {5000 * x + 1e-3}', 'TPS')
          for k, x in enumerate(np.linspace(0.1, 0.9, 9))]
res = spice_op('tps', adc_net(copies), [f'v(an_{c[0]})' for c in copies])
vv = [res[f'v(an_x{k})'] for k in range(9)]
lin = [vv[0] + (vv[-1] - vv[0]) * k / 8 for k in range(9)]
err = max(abs(a - b) for a, b in zip(vv, lin)) / (vv[-1] - vv[0]) * 100
record('In sensors', 'TPS 5 kohm potentiometer, 10-90 % travel (loaded by 15.6 kohm)',
       f'ADC {vv[0]:.2f} .. {vv[-1]:.2f} V; worst deviation from a straight line between the end points {err:.1f} % of travel',
       'OK' if err < 5 else 'CHECK', 'rusEFI maps TPS linearly between the calibrated end points, so mid-travel '
       'reads a little low (bowed); a lower-resistance TPS reduces this' if err >= 1 else '')

# MAP: MPX5700AP, Vout = Vs (0.0012858 P + 0.04) (NXP datasheet; as miata_board.cpp), sensor on V5_SENS
mapv = lambda p, vs=5.0: vs * (0.0012858 * p + 0.04)
copies = [(f'p{p}', f'Vm_@N@ in_@N@ 0 {mapv(p)}', 'MAP') for p in (20, 101, 250, 700)]
res = spice_op('map', adc_net(copies), [f'v(an_{c[0]})' for c in copies] + [f'i(vm_p{p})' for p in (20, 101, 250, 700)])
kpa_lsb = LSB / (5.0 * 0.0012858 * DIV['MAP'][1] / (DIV['MAP'][0] + DIV['MAP'][1]))
i700 = -res['i(vm_p700)']
record('In sensors', 'MAP MPX5700AP (on board), 20 / 101 / 250 / 700 kPa',
       f'ADC {res["v(an_p20)"]:.3f} / {res["v(an_p101)"]:.3f} / {res["v(an_p250)"]:.3f} / {res["v(an_p700)"]:.3f} V; '
       f'{kpa_lsb:.2f} kPa per LSB; sensor sources {i700 * 1000:.2f} mA at 700 kPa',
       'OK' if res['v(an_p700)'] < 3.3 else 'CHECK',
       'NA engines use 20-105 kPa: about 13 % of the ADC range. The divider load at full scale is above the '
       '0.1 mA the VERIFICATION notes quote; only relevant with boost')

# narrowband O2 (AUX2 front, AUX1 rear on 1996-2005): zirconia cell 0.1-0.9 V, internal resistance about 1 kohm hot,
# 100 kohm and more cold (assumed typical)
copies = [(f'o{k}', f'Vo_@N@ e_@N@ 0 {e}\nRo_@N@ e_@N@ in_@N@ {ri}', 'AUX2')
          for k, (e, ri) in enumerate([(0.9, 1e3), (0.45, 1e3), (0.1, 1e3), (0.45, 100e3)])]
res = spice_op('o2', adc_net(copies), [f'v(an_{c[0]})' for c in copies])
g = DIV['AUX2'][1] / (DIV['AUX2'][0] + DIV['AUX2'][1])
rd = [res[f'v(an_o{k})'] / g for k in range(4)]
record('In sensors', 'narrowband O2 (AUX2/AUX1), hot sensor 1 kohm: 0.9 / 0.45 / 0.1 V',
       f'firmware reads {rd[0]:.3f} / {rd[1]:.3f} / {rd[2]:.3f} V (x1.56); cold sensor (100 kohm) at 0.45 V reads {rd[3]:.2f} V',
       'OK' if abs(rd[1] - 0.45) < 0.05 else 'CHECK',
       'the 15.6 kohm load pulls a cold (unheated) sensor to ~0 V, i.e. "lean", not to a neutral bias: closed loop '
       'must wait for the heater (rusEFI waits for warm-up)')
# MAF (NB) is a buffered 0-5 V output; vane AFM (1989-95) a potentiometer: both inside 0-5 V like TPS/MAP.
record('In sensors', 'MAF (NB, 0-5 V buffered) / vane AFM (NA, potentiometer) on AUX3',
       f'5.0 V reads {5.0 * DIV["AUX3"][1] / (DIV["AUX3"][0] + DIV["AUX3"][1]):.2f} V at the ADC', 'OK')

# 1989-93 MT idle switch (2L) and 1994-95 electrical-load signal (2L) on IN_AUX1: an analog input with no pull-up
copies = [('open', 'Rsw_@N@ in_@N@ 0 1e9', 'AUX1'), ('closed', 'Rsw_@N@ in_@N@ 0 1', 'AUX1'),
          ('b12', 'Vsw_@N@ in_@N@ 0 14.4', 'AUX1')]
_r27 = MB['1989-93'].get('R27')
if _r27:
    on('R27', 'V5_EXT', 'IN_AUX1', parts=MB['1989-93'])
    pu = f"Vpu_@N@ pu_@N@ 0 5.0\nRpu_@N@ pu_@N@ in_@N@ {sv(_r27['value'])}\n"
    copies += [('puopen', pu + 'Rsw_@N@ in_@N@ 0 1e9', 'AUX1'), ('puclosed', pu + 'Rsw_@N@ in_@N@ 0 1', 'AUX1')]
res = spice_op('aux1', adc_net(copies), [f'v(an_{c[0]})' for c in copies])
if _r27:
    record('In 1989-93', 'MT idle switch 2L on IN_AUX1 (ground-switching contact)',
           f'as built (R27 not fitted): open {res["v(an_open)"]:.2f} V, closed {res["v(an_closed)"]:.2f} V, indistinguishable; '
           f'with R27 ({_r27["value"]} to the harness 5 V) fitted: open {res["v(an_puopen)"]:.2f} V, closed '
           f'{res["v(an_puclosed)"]:.2f} V at PC5', 'OK',
           'fit R27 if the tune uses the idle switch; the firmware reads TPS on 2M by default')
else:
    record('In 1989-93', 'MT idle switch 2L on IN_AUX1 (ground-switching contact)',
           f'switch open {res["v(an_open)"]:.2f} V, closed {res["v(an_closed)"]:.2f} V: indistinguishable', 'CHECK',
           'IN_AUX1 has no pull-up; reading a ground-switching idle switch needs one (e.g. 4.7-10k to V5_SENS on the '
           'motherboard). Only matters if the tune uses the idle switch (the firmware reads TPS on 2M)')
_cl1 = next((r for r, p in DB.items() if r.startswith('D') and set(p['pads'].values()) == {'+3V3', 'AN_AUX1'}), None)
record('In 1994-95', 'electrical-load signal 2L on IN_AUX1, if it is a +B signal (not verified)',
       (f'14.4 V gives {res["v(an_b12)"]:.2f} V at PC5 without a clamp; {_cl1} holds it near 3.55 V (In shorts), so it '
        f'reads full scale: usable as on/off, harmless' if _cl1 else
        f'14.4 V gives {res["v(an_b12)"]:.2f} V at PC5 unclamped (analog-mode max {AN_MAX:.1f} V)'),
       'OK' if _cl1 else 'CHECK', 'check the signal level on a car before wiring it: if it switches to battery voltage it over-drives the '
       'ADC pin every time the defroster is on (then it needs the switch-input divider or a clamp)')

# sensor wire shorted to battery: every analog harness input. Rev 0.7 puts a Schottky clamp (BAT54WS) from each AN_
# node to +3V3; the run uses whatever design.py has (clamp or none) and checks the pin, the current into the MCU's own
# protection diode, and the series resistor's power against its package rating.
P_RATING = {'0402': 0.0625, '0603': 0.1, '0805': 0.125, '1206': 0.25}


def pkg(ref):
    fp = DB[ref]['fp']
    return next(k for k in P_RATING if k in fp)


def clamp_of(node):
    return next((r for r, p in DB.items() if r.startswith('D') and set(p['pads'].values()) == {'+3V3', node}), None)


short = []
for n in ('TPS', 'CLT', 'IAT', 'AFR', 'AUX1', 'AUX2', 'AUX3'):
    rs, rg, _ = DIV[n]
    cl = clamp_of('AN_' + n)
    rser = between('IN_' + n, 'AN_' + n)['ref']
    for vsh in (14.4, 24.0):
        vth = vsh * rg / (rs + rg)
        clamp = f'Dcl an v33 {"dbat54" if DB[cl]["value"].startswith("BAT54") else "d4148"}\nV33 v33 0 3.3' if cl else ''
        net = f"""* {n} shorted to {vsh} V, ADC pin in analog mode (the MCU's protection diode to VDDA)
Vsh in 0 {vsh}
Rs in an {rs}
Rg an 0 {rg}
Vdda vdda 0 3.3
Dinj an vdda desd
{clamp}
{MODELS}
.op
.control
run
@PRINT@
.endc
.end
"""
        r = spice_op('short', net, ['v(an)', 'i(vdda)'])
        prs = (vsh - r['v(an)']) ** 2 / rs
        short.append(dict(n=n, vsh=vsh, vth=vth, van=r['v(an)'], iinj=abs(r['i(vdda)']), clamp=cl, prs=prs,
                          rser=rser, rating=P_RATING[pkg(rser)]))
for vsh, label in ((14.4, 'shorted to 14.4 V'), (24.0, 'same, 24 V jump start')):
    w = [x for x in short if x['vsh'] == vsh]
    if all(x['clamp'] for x in w):
        hot = max(w, key=lambda x: x['prs'] / x['rating'])
        ok_pin = max(x['van'] for x in w) <= AN_MAX + 0.05 and max(x['iinj'] for x in w) < 1e-6
        ok_r = all(x['prs'] <= x['rating'] for x in w)
        record('In shorts', f'analog sensor wire (TPS, CLT, IAT, O2, MAF, AFR) {label}, with the rev 0.7 clamps',
               f'pin {max(x["van"] for x in w):.2f} V (VDDA + {max(x["van"] for x in w) - 3.3:.2f} V), '
               f'{max(x["iinj"] for x in w) * 1e9:.1f} nA into the MCU, {(vsh - 3.55) / DIV["TPS"][0] * 1000:.1f} mA into '
               f'+3V3 per input; series resistor up to {hot["prs"] * 1000:.0f} mW ({hot["rser"]}, '
               f'{pkg(hot["rser"])} rated {hot["rating"] * 1000:.0f} mW)',
               'OK' if ok_pin and ok_r else ('CHECK' if ok_pin else 'FAIL'),
               '' if ok_r else 'the series resistor runs over its rating for the length of the short')
    else:
        record('In shorts', f'analog sensor wire (TPS, CLT, IAT, O2, MAF, AFR) {label}',
               f'pin {max(x["vth"] for x in w):.1f} V unclamped, or {max(x["van"] for x in w):.2f} V with '
               f'{max(x["iinj"] for x in w) * 1000:.1f} mA injected into VDDA per pin (analog-mode max {AN_MAX:.1f} V; FT '
               'pins allow no positive injection)', 'FAIL',
               'no clamp on the AN_ inputs. Fix: a Schottky to +3V3 at each AN_ node (rev 0.7)')

# Clamp leakage into the analog nodes (rev 0.7). A Schottky clamp leaks from +3V3 into the AN_ node, worst when the
# node is low (about 3.3 V across it) and the board is hot. BAT54WS: 2 uA max at 25 V, 25 C (datasheet). Assumed:
# leakage ~ sqrt(VR), doubling every 10 C, typical a tenth of max. The error at the sensor is I x Rseries.
cl_an = clamp_of('AN_TPS')
if cl_an and DB[cl_an]['value'].startswith('BAT54'):
    rs_an, rg_an, _ = DIV['TPS']
    i_max25 = 2e-6 * math.sqrt(3.3 / 25.0)
    rows = []
    for t in (25, 60, 85):
        imx = i_max25 * 2 ** ((t - 25) / 10)
        rows.append(f'{t} C: {imx * 0.1 * 1e6:.1f} / {imx * 1e6:.1f} uA, {imx * 0.1 * rs_an * 1e3:.0f} / '
                    f'{imx * rs_an * 1e3:.0f} mV at the sensor')
    imx85 = i_max25 * 2 ** 6
    record('In sensors', f'clamp leakage ({DB[cl_an]["value"]}, typical / max, AN_ node near 0 V)', '; '.join(rows),
           'CHECK' if imx85 * rs_an > 0.05 else 'OK',
           'reads high at the low end of a sensor (closed throttle, hot coolant): about 0.5 % of a 5 V span at 85 C '
           'typical, up to 5 % with a max-leakage part (assumed scaling: the datasheet gives 25 C only). The ECU sits '
           'in the cabin (60 C: 0.1 % typical, 1 % max). Check a TPS and CLT reading against a meter on a hot day; a '
           'low-leakage clamp (1N4148WS, nA) would put more of a short\'s current into the MCU instead')

# 12 V switch inputs (33k/10k, 10 nF) in a 35 V load dump with the switch closed; FT digital pins: VDD + 4 V.
# Rev 0.7: 1N4148WS from each switch node to +3V3, as on the hall inputs.
rs_sw, rg_sw = sv(between('IN_SW1', 'SW1')['value']), sv(between('SW1', 'GND')['value'])
cl_sw = clamp_of('SW1')
for vsw in (24.0, 35.0):
    vp = vsw * rg_sw / (rs_sw + rg_sw)
    if cl_sw:
        isw = (vsw - 3.3 - 0.6) / rs_sw
        vcl = 3.3 + 1.75 * 0.02585 * math.log(isw / 2.5e-9) + isw * 0.6
        vp = min(vp, vcl)
    record('In shorts', f'12 V switch input (VSS/A-C/clutch) at {vsw:.0f} V ({"jump start" if vsw < 30 else "suppressed load dump"})',
           f'{vp:.2f} V at the FT pin (abs max {FT_MAX:.1f} V){", clamped by " + cl_sw if cl_sw else ""}',
           'OK' if vp < FT_MAX else 'CHECK',
           'only while a battery-fed switch is closed during a 35 V load dump; a 1N4148WS to +3V3 (as the hall inputs) '
           'would clamp it' if vp >= FT_MAX else '')

# battery / ignition sense (33k/6.8k into PA1/PA2, analog mode)
rb1, rb2 = val('R11'), val('R12')
# rev 0.10: R11 hangs on the battery input itself (up to rev 0.9 on +12V, after D7 and F1, 0.35 V or more below it)
on('R11', 'VBAT_IN', 'AN_VBATT'); on('R13', 'VIGN_IN', 'AN_VIGN')
VB_DROP = 0.0
vb_at = lambda vb: vb * rb2 / (rb1 + rb2)
vmax_meas = AN_MAX * (rb1 + rb2) / rb2
record('In supply', 'battery sense AN_VBATT (straight from the battery input) and AN_VIGN, 9-16 V',
       f'{vb_at(9 - VB_DROP):.2f} .. {vb_at(16 - VB_DROP):.2f} V at PA1 ({vb_at(16):.2f} V on PA2 at 16 V); full scale '
       f'{3.3 * (rb1 + rb2) / rb2:.1f} V', 'OK')
# the battery input can sit at D6's clamp voltage in a load dump (SMCJ30A: up to 48.4 V at its rated pulse current) and
# about -1 V with the battery reversed (D6 conducts forward)
_i48 = (48.4 * rb2 / (rb1 + rb2) - AN_MAX) / (rb1 * rb2 / (rb1 + rb2))
record('In supply', 'AN_VBATT with the battery input at 48.4 V (D6 at its maximum clamp voltage) and at -1 V (reversed)',
       f'{_i48 * 1e3:.2f} mA into the clamp D38 through R11 ({(48.4 - AN_MAX) ** 2 / rb1 * 1e3:.0f} mW in R11, 0402: 62 mW rated); '
       f'{1.0 / rb1 * 1e6:.0f} uA out of PA1 at -1 V (limit 5 mA)',
       'OK' if clamp_of('AN_VBATT') and (48.4 - AN_MAX) ** 2 / rb1 < 0.062 else 'CHECK')
if clamp_of('AN_VBATT') and clamp_of('AN_VIGN'):
    # rev 0.8: BAT54WS from each node to +3V3 (D38/D39): solve the clamped node (Schottky model of dbat54)
    def vb_cl(vb):
        rth = rb1 * rb2 / (rb1 + rb2); vth = vb * rb2 / (rb1 + rb2)
        v = min(vth, 3.3)
        for _ in range(200):
            i = max(0.0, (vth - v) / rth)
            vn = 3.3 + 1.05 * 0.02585 * math.log(i / 2e-7 + 1) + 2.5 * i if i > 0 else vth
            v = 0.5 * v + 0.5 * min(vth, vn)
        return v, max(0.0, (vth - v) / rth)
    (v24, i24), (v34, i34) = vb_cl(24 - VB_DROP), vb_cl(34.2)
    record('In supply', 'AN_VBATT / AN_VIGN in a 24 V jump start and a 34 V load dump, with the rev 0.8 clamps',
           f'{v24:.2f} V / {v34:.2f} V at PA1/PA2 (analog-mode max {AN_MAX:.1f} V), {i24 * 1e6:.0f} / {i34 * 1e6:.0f} uA '
           f'into +3V3 through {clamp_of("AN_VBATT")}/{clamp_of("AN_VIGN")}; reads full scale ({vmax_meas:.1f} V) while it lasts',
           'OK' if max(v24, v34) <= AN_MAX + 0.02 else 'CHECK')
else:
    record('In supply', 'AN_VBATT / AN_VIGN in a 24 V jump start and a 34 V load dump',
           f'{vb_at(24 - 0.35):.2f} V / {vb_at(34.2):.2f} V at PA1 (analog-mode max {AN_MAX:.1f} V, reached at '
           f'{vmax_meas:.1f} V); injection {(vb_at(24) - AN_MAX - 0.0) / (rb1 * rb2 / (rb1 + rb2)) * 1e6:.0f} / '
           f'{(vb_at(34.2) - AN_MAX) / (rb1 * rb2 / (rb1 + rb2)) * 1e6:.0f} uA', 'CHECK',
           f'out of the analog-mode rating above {vmax_meas:.0f} V, but only ~0.1-0.5 mA through 5.6 kohm; a 47k top '
           'resistor (full scale 26 V) or a clamp would keep it inside')
ip1_ = (150 - 0.6) / rb1
record('In supply', 'AN_VIGN in ISO 7637-2 pulse 1 (-150 V, 10 ohm, on the ignition line)',
       f'{ip1_ * 1000:.1f} mA out of PA2 through R13 (FT negative injection limit -5 mA)', 'OK' if ip1_ < 5e-3 else 'CHECK')

# crank/cam inputs per sensor type. Sensor: open collector, Vce(sat) ~0.3 V at 5 mA (ron 60 ohm, assumed);
# 1k pull-up (R62) to V5_SENS, 4.7k (R61), 1 nF (C51), 1N4148WS to +3V3 (D13). Harness 2 nF (pessimistic).
# rev 0.8: the pull-up hangs off one cathode of D35 (BAT54A, anode V5_EXT)
on('R61', 'IN_HALL1', 'HALL1'); on('R62', 'V5_H1', 'IN_HALL1'); on('C51', 'HALL1', 'GND'); on('D13', '+3V3', 'HALL1')
on('D35', 'V5_H1', 'V5_H2', 'V5_EXT')


def hall(width_us, period_us, v5s=5.0, vdd=3.3, charn=2e-9):
    net = f"""* hall/optical input
V5 vs0 0 {v5s}
Dpu vs0 vs dbat54
Rpu vs in {val('R62')}
Charn in 0 {charn}
Vg g 0 PULSE(0 5 {3 * period_us}u 1n 1n {width_us}u {period_us}u)
Sw in 0 g 0 swmod
.model swmod sw(vt=2.5 ron=60 roff=10meg)
Rs in mcu {val('R61')}
Cf mcu 0 {val('C51')}
V33 v33 0 {vdd}
Dcl mcu v33 d4148
{MODELS}
""" + tran_ctl(f'{min(width_us, period_us) / 200}u', f'{5 * period_us}u')
    d = spice('hall', net, ['v(mcu)'])
    t, v = d['time'], d['v(mcu)']
    t0 = 3 * period_us * 1e-6
    mlow = (t > t0) & (t < t0 + width_us * 1e-6)
    vmin = float(np.min(v[mlow]))
    vmax = float(np.max(v[t < t0]))
    tc = t[(t > t0) & (v < 0.3 * vdd)]
    delay = (tc[0] - t0) * 1e6 if len(tc) else float('inf')
    return vmin, vmax, delay


SIG = {'NA CAS (1989-97, optical)': (0.5 * 180, 180), 'NB crank (1999-2005, hall)': (3.5, 70)}
for sname, (wdeg, pdeg) in SIG.items():
    out = []
    for rpm, v5s, vdd in ((150, 5.0, 3.3), (150, 3.9, 2.9), (7200, 5.0, 3.3)):
        us = 1e6 / (rpm * 6)
        out.append((rpm, v5s, vdd, wdeg * us, hall(wdeg * us, pdeg * us, v5s, vdd)))
    ok = all(v[0] < 0.3 * vdd and v[1] > 0.7 * vdd and v[2] < w / 2 for rpm, v5s, vdd, w, v in out)
    record('In crank/cam', sname,
           '; '.join(f'{rpm} rpm{" (crank dip: V5_SENS 3.9 V, VDD 2.9 V)" if v5s < 5 else ""}: {v[0]:.2f}/{v[1]:.2f} V, '
                     f'delay {v[2]:.1f} us of {w:.0f} us' for rpm, v5s, vdd, w, v in out), 'OK' if ok else 'CHECK')

# VSS at 200 km/h: NB 4 pulses per sensor turn, 1.12 sensor turns per wheel turn (miata_board.cpp), 1.85 m tyre
# (assumed) -> about 134 Hz. 12 V push-pull and ground-switching with the R20 4.7k pull-up option.
f_vss = 200 / 3.6 / 1.85 * (3.909 * 6 / 21) * 4
for label, src in (('12 V push-pull', f'Vs in 0 PULSE(0 12 0.5m 5u 5u {0.5 / f_vss} {1 / f_vss})'),
                   ('ground-switching + R20 4.7k to 12 V', f'Vb vb 0 12\nRpu vb in 4.7k\nCh in 0 2n\n'
                                                           f'Vg g 0 PULSE(5 0 0.5m 1n 1n {0.5 / f_vss} {1 / f_vss})\n'
                                                           'Sw in 0 g 0 swmod\n.model swmod sw(vt=2.5 ron=50 roff=10meg)')):
    net = f"""* VSS into a switch input
{src}
R1 in sw {rs_sw}
R2 sw 0 {rg_sw}
C1 sw 0 {sv(between('SW1', 'GND', 'C')['value'])}
""" + tran_ctl('5u', f'{4 / f_vss + 0.5e-3}')
    d = spice('vss', net, ['v(sw)'])
    v = d['v(sw)'][d['time'] > 0.5e-3 + 1 / f_vss]
    record('In switches', f'VSS {f_vss:.0f} Hz (200 km/h), {label}', f'swings {np.min(v):.2f} .. {np.max(v):.2f} V at the MCU',
           'OK' if np.min(v) < VIL and np.max(v) > VIH else 'CHECK',
           '1989-95 VSS is a reed switch to ground: fit R20' if 'ground' in label else '')

# knock (NB1 2F, NB2 4M): piezo sensor, sensitivity ~26 mV/g (Bosch KS-4 class, assumed), source capacitance 1 nF
# (assumed) + 2 m shielded cable 200 pF; C44 100 nF, R45 100k to KN_BIAS (R46/R47 100k, C45 1 uF), LMV321 gain
# 1 + R48/R49, R50 330 + C46 10 nF into PA3. BP knock frequency 900/(pi*bore/2) = 6.9 kHz (rusEFI's formula, bore 83 mm).
# rev 0.7: R138 (2.2k) between IN_KNOCK and C44 (net KN_IN); earlier revisions had C44 straight on IN_KNOCK
KN_A = 'KN_IN' if any('KN_IN' in p['pads'].values() for p in DB.values()) else 'IN_KNOCK'
R_KIN = val(between('IN_KNOCK', 'KN_IN')['ref']) if KN_A == 'KN_IN' else 1e-3
for ref, nets_ in (('C44', (KN_A, 'KN_P')), ('R45', ('KN_P', 'KN_BIAS')), ('R48', ('KN_OUT', 'KN_N')),
                   ('R49', ('KN_N', 'KN_BIAS')), ('R50', ('KN_OUT', 'AN_KNOCK')), ('C46', ('AN_KNOCK', 'GND'))):
    on(ref, *nets_)
f_knock = 900 / (math.pi * 0.083 / 2)
gain_k = 1 + val('R48') / val('R49')
net = f"""* knock input AC
Vk e 0 AC 1
Cs e in 1n
Cc in 0 200p
Rkin in kin {R_KIN}
C44 kin kp {val('C44')}
R45 kp kb {val('R45')}
Vkb kb 0 1.65
Eo ko 0 kp kn 1e5
R48 ko kn {val('R48')}
R49 kn kb {val('R49')}
R50 ko an {val('R50')}
C46 an 0 {val('C46')}
.ac dec 50 10 100k
.control
run
let g = mag(v(an))
wrdata @DAT@ g
.endc
.end
"""
d = spice('knock_ac', net.replace('@VEC@', 'g'), [])
fr, gm = np.loadtxt(os.path.join(OUT, 'knock_ac.dat'))[:, 0], np.loadtxt(os.path.join(OUT, 'knock_ac.dat'))[:, 1]
gk = float(np.interp(f_knock, fr, gm))
f_lo = float(fr[np.argmax(gm > gk / math.sqrt(2))])
clip_g = (1.65 - 0.03) / gk / 0.026
record('In knock (NB)', f'piezo 1 nF + cable into {"R138 " if KN_A == "KN_IN" else ""}C44/R45, gain {gain_k:.1f}; '
       f'knock band {f_knock / 1000:.1f} kHz',
       f'gain {gk:.2f} at {f_knock / 1000:.1f} kHz, -3 dB below {f_lo:.0f} Hz; 1 g (26 mV) -> {gk * 26:.0f} mV at PA3; '
       f'clips above {clip_g:.0f} g', 'OK' if f_lo < f_knock / 3 else 'CHECK',
       'the sensor capacitance with R45 sets the low corner (not C44)')
# knock wire shorted to battery: the 14.4 V step reaches the LMV321 input through C44 with no series resistance
net = f"""* knock wire shorted to battery
Vs in 0 PWL(0 0 10u 0 11u 14.4)
Rh in in2 {0.1 + R_KIN}
C44 in2 kp {val('C44')}
R45 kp kb {val('R45')}
Vkb kb 0 1.65
Dhi kp v33 desd2
Dlo 0 kp desd2
Vdd v33 0 3.3
.model desd2 d(is=1e-14 n=1 rs=5)
""" + tran_ctl('10n', '200u')
d = spice('knock_short', net, ['i(Vdd)'])
ipk = float(np.max(np.abs(d['i(Vdd)'])))
record('In knock (NB)', 'knock wire shorted to battery (14.4 V step)',
       f'{ipk * 1000:.1f} mA peak into the LMV321 input ESD diode (5 ohm assumed)'
       + (f' through R138 {R_KIN / 1000:.1f}k' if KN_A == 'KN_IN' else ''),
       'OK' if ipk < 10e-3 else 'CHECK',
       '' if ipk < 10e-3 else 'C44 couples the step straight onto the op-amp input (LMV321 input current abs max about '
       '10 mA, recalled): add 1-10 kohm in series before or after C44')

# filter corners vs signal frequencies
fc_an = 1 / (2 * math.pi * (DIV['TPS'][0] * DIV['TPS'][1] / (DIV['TPS'][0] + DIV['TPS'][1])) * DIV['TPS'][2])
fc_hall = 1 / (2 * math.pi * val('R61') * val('C51'))
c_sw = sv(between('SW1', 'GND', 'C')['value'])
fc_sw = 1 / (2 * math.pi * (rs_sw * rg_sw / (rs_sw + rg_sw)) * c_sw)
fc_kn = 1 / (2 * math.pi * val('R50') * val('C46'))
f_notch = 1 / (2 * 3.5 / (7200 * 6))
record('In filters', 'RC corners vs the signals they carry',
       f'analog 5.6k||10k + 10 nF: {fc_an / 1000:.1f} kHz (sensor signals < 100 Hz; MAP pulsation at 7200 rpm 240 Hz); '
       f'hall 4.7k + 1 nF: {fc_hall / 1000:.0f} kHz (NB 3.5 deg notch at 7200 rpm ~ {f_notch / 1000:.1f} kHz); '
       f'switch 33k||10k + 10 nF: {fc_sw / 1000:.1f} kHz (VSS {f_vss:.0f} Hz); knock 330 + 10 nF: {fc_kn / 1000:.0f} kHz '
       f'(band {f_knock / 1000:.1f} kHz)', 'OK' if fc_an > 240 * 3 and fc_hall > f_notch and fc_sw > 3 * f_vss
       and fc_kn > 3 * f_knock else 'CHECK')

# wideband battery sense: R120/R121 from VBAT_IN (before D7, only D6 on it) into F103 PB0 (standard I/O, VDD + 0.3 V,
# +-5 mA injection)
r120, r121 = val('R120'), val('R121')
vb_wb = lambda v: v * r121 / (r120 + r121)
inj_wb = (48.4 - 3.6) / r120
record('In supply', 'wideband VBAT sense R120/R121 into F103 PB0 (non-FT)',
       f'16 V -> {vb_wb(16):.2f} V; at the SMCJ30A clamp (48.4 V at 31 A, Littelfuse) {vb_wb(48.4):.2f} V, '
       f'{inj_wb * 1000:.2f} mA injected (limit 5 mA); reverse battery: D6 holds VBAT_IN near -1 V', 'OK'
       if inj_wb < 5e-3 else 'CHECK')

# per-year input map: harness cavity -> daughterboard input -> the sensor model and check above
IN_FUNC = {
    '1989-93': {'IN_CLT': 'CLT', 'IN_IAT': 'IAT (in the airflow meter)', 'IN_TPS': 'TPS (AT/VTPS)', 'IN_AUX1': 'MT idle switch',
                'IN_AUX2': 'front O2', 'IN_AUX3': 'AFM flap', 'IN_HALL1': 'CAS SGT', 'IN_HALL2': 'CAS SGC',
                'IN_SW1': 'VSS (reed)', 'IN_SW2': 'A/C switch', 'IN_SW3': 'clutch', 'VIGN_IN': 'ignition sense'},
    '1994-95': {'IN_CLT': 'CLT', 'IN_IAT': 'IAT (in the airflow meter)', 'IN_TPS': 'TPS', 'IN_AUX1': 'electrical load',
                'IN_AUX2': 'front O2', 'IN_AUX3': 'AFM flap', 'IN_HALL1': 'CAS SGT', 'IN_HALL2': 'CAS SGC',
                'IN_SW1': 'VSS (reed)', 'IN_SW2': 'A/C switch', 'IN_SW3': 'clutch', 'VIGN_IN': 'ignition sense'},
    '1996-97': {'IN_CLT': 'CLT', 'IN_IAT': 'IAT', 'IN_TPS': 'TPS', 'IN_AUX1': 'rear O2',
                'IN_AUX2': 'front O2', 'IN_AUX3': 'MAF', 'IN_HALL1': 'CAS SGT', 'IN_HALL2': 'CAS SGC',
                'IN_SW1': 'VSS', 'IN_SW2': 'A/C switch', 'IN_SW3': 'clutch'},
    '1999-2000': {'IN_CLT': 'CLT', 'IN_IAT': 'IAT', 'IN_TPS': 'TPS', 'IN_AUX1': 'rear O2',
                  'IN_AUX2': 'front O2', 'IN_AUX3': 'MAF', 'IN_HALL1': 'crank (hall)', 'IN_HALL2': 'cam (hall)',
                  'IN_SW1': 'VSS', 'IN_SW2': 'A/C switch', 'IN_SW3': 'clutch', 'IN_KNOCK': 'knock'},
    '2001-05': {'IN_CLT': 'CLT', 'IN_IAT': 'IAT', 'IN_TPS': 'TPS', 'IN_AUX1': 'rear O2',
                'IN_AUX2': 'front O2', 'IN_AUX3': 'MAF', 'IN_HALL1': 'crank (hall)', 'IN_HALL2': 'cam (hall)',
                'IN_SW1': 'VSS', 'IN_SW2': 'A/C pressure switch', 'IN_SW3': 'clutch', 'IN_KNOCK': 'knock',
                'VIGN_IN': 'IG1 sense (2003-05)'},
}
for y, _ in YEARS:
    hn = harness(y)
    have = {n for n in hn if n.startswith('IN_') or n in ('VIGN_IN',)}
    assert have == set(IN_FUNC[y]), f'{y}: harness inputs {sorted(have)} vs mapped {sorted(IN_FUNC[y])}'
    flags = []
    if y == '1989-93':
        flags.append('2L idle switch readable once R27 (not fitted) is fitted' if 'R27' in MB[y] else
                     '2L idle switch unreadable (no pull-up)')
    if y == '1994-95':
        flags.append('2L load signal level unverified')
    if y in ('1989-93', '1994-95'):
        flags.append('reed-switch VSS needs R20')
    record('In ' + y, 'harness inputs: ' + ', '.join(f'{IN_FUNC[y][n]} {"/".join(hn[n])}' for n in sorted(IN_FUNC[y])),
           'each on a circuit simulated above with its sensor model'
           + (f'; {"; ".join(flags)}' if flags else '')
           + ('; a sensor wire shorted to battery is clamped (In shorts)' if clamp_of('AN_TPS')
              else '; a sensor wire shorted to battery overdrives its ADC pin (In shorts)'),
           'CHECK' if flags else 'OK')

# =================================================================================================================
# W. Wideband: LSU 4.9 on the FOME/rusEFI front end
# =================================================================================================================
VMS = 'WB_VMS' if 'F2' in DB else 'LSU_VM'      # rev 0.8: board side of the VM wire's PTC
RF2 = 1.6 if 'F2' in DB else 0.0
for ref, nets_ in (('R101', ('WB_VDDA', 'WB_VM_REF')), ('R102', ('WB_VM_REF', 'GND')), ('R109', (VMS, 'WB_VM')),
                   ('R108', ('LSU_RT', 'WB_PUMP')), ('R110', ('LSU_RT', 'LSU_IP')), ('R131', ('WB_IP_DAC', 'WB_PUMP_N')),
                   ('R133', ('WB_PUMP', 'WB_PUMP_N')), ('R132', ('WB_PUMP_P', 'WB_VM')), ('R134', ('LSU_RT', 'WB_PUMP_P')),
                   ('R112', ('WB_IS_P', 'LSU_IP')), ('R115', ('WB_IS_P', 'WB_VM')), ('R111', ('WB_IS_N', 'LSU_RT')),
                   ('R117', ('WB_IS_OUT', 'WB_IS_N')), ('R124', ('WB_IS_OUT', 'WB_IP_SENSE')), ('R114', ('+3V3', 'LSU_UN')),
                   ('R104', ('WB_UN_BUF', 'WB_UN_P')), ('R105', ('WB_UN_P', 'GND')), ('R103', (VMS, 'WB_UN_N')),
                   ('R107', ('WB_UN_N', 'WB_UN_SENSE')), ('R106', ('WB_ESR', 'WB_ESR_49')), ('C102', ('LSU_UN', 'WB_ESR')),
                   ('C103', ('WB_PUMP', 'WB_PUMP_N')), ('C104', (VMS, 'GND')), ('C111', ('WB_IP_SENSE', 'GND')),
                   ('Q101', ('WB_HTR_G', 'LSU_HTR_N', 'HTR_GND')), ('R125', ('WB_HTR_G', 'WB_HTR_PWM')),
                   ('R126', ('GND', 'WB_HTR_PWM')), ('R120', ('VBAT_IN', 'WB_VBAT_DIV')), ('R121', ('WB_VBAT_DIV', 'GND'))):
    on(ref, *nets_)
u1 = DB['U101']['pads']
assert (u1['1'], u1['2'], u1['3']) == ('WB_PUMP', 'WB_PUMP_N', 'WB_PUMP_P')
assert (u1['7'], u1['6'], u1['5']) == ('WB_UN_SENSE', 'WB_UN_N', 'WB_UN_P')
# pin 10 (Nernst buffer input) is LSU_UN, or since rev 0.7 WB_UN_IN through R137 (10k into a CMOS input: the same
# voltage at DC and at the ESR frequency, so the models below use the LSU_UN node for it)
assert (u1['8'], u1['9']) == ('WB_UN_BUF', 'WB_UN_BUF') and u1['10'] in ('LSU_UN', 'WB_UN_IN')
if u1['10'] == 'WB_UN_IN':
    on(between('LSU_UN', 'WB_UN_IN')['ref'], 'LSU_UN', 'WB_UN_IN')
assert (u1['14'], u1['13'], u1['12']) == ('WB_VM', 'WB_VM', 'WB_VM_REF') and u1['4'] == '+3V3'
u5 = DB['U105']['pads']
assert (u5['1'], u5['3'], u5['4'], u5['5']) == ('WB_IS_OUT', 'WB_IS_P', 'WB_IS_N', '+3V3')
# Bosch LSU 4.9 data sheet 69034379 (Bosch Motorsport): Ip [mA] vs lambda; Nernst cell 300 ohm nominal, max current
# load 250 uA; heater 7.5 V nominal, 7.5 W steady state. Free air is beyond the table (2.25 mA at lambda 10.1);
# 2.55 mA assumed for air.
LSU_IP = [(0.650, -2.000), (0.700, -1.602), (0.800, -0.927), (0.900, -0.405), (1.003, 0.0), (1.100, 0.193),
          (1.429, 0.671), (1.701, 0.938), (2.434, 1.385), (5.391, 2.000), (10.119, 2.250), (99, 2.55)]


def fw_lambda(ip_ma):
    """rusEFI wideband lambda_conversion.cpp, GetPhiLsu49 (phi = 1/lambda)."""
    if ip_ma > 1.11:
        return 2.0
    if ip_ma < -3.5:
        return 0.5
    g = -0.28299 if ip_ma < 0 else -0.44817
    return 1 / (g * ip_ma + 0.99559)


# op-amps: MCP6004 rail-to-rail output within 25 mV of the rails at 10 kohm (Microchip DS21733, recalled); modelled
# with 50 mV headroom and 20 ohm output resistance (assumed, conservative for the 2.5 mA pump current). AD8628
# rail-to-rail, 20 mV headroom (assumed). Both on +3V3; VDDA (REF3033) 3.300 V.
OPAMP = """.subckt mcp p n out
* transconductance into 160 pF: 1 MHz gain-bandwidth (MCP6004: 1 MHz), DC gain 1e5; output clipped 50 mV from the rails
Bg 0 y I = 1e-3*(V(p)-V(n))
Cy y 0 160p
Ry y vm 1e8
Vm vm 0 1.65
Vh vh 0 3.3
Dh y vh dcl
Dl 0 y dcl
.model dcl d(is=1e-14 n=1)
Bo x 0 V = max(0.05, min(3.25, V(y)))
Ro x out 20
.ends
.subckt ad86 p n out
Bg 0 y I = 1e-3*(V(p)-V(n))
Cy y 0 160p
Ry y vm 1e8
Vm vm 0 1.65
Vh vh 0 3.3
Dh y vh dcl
Dl 0 y dcl
.model dcl d(is=1e-14 n=1)
Bo x 0 V = max(0.02, min(3.28, V(y)))
Ro x out 5
.ends
"""


def wb_front(rp, ri, esr_drive=None, dac=None):
    """Wideband analog front end. dac: line(s) defining node 'dac'. esr_drive: source on WB_ESR_49 (else floating)."""
    esr = (f'R106 esr49 esr {val("R106")}\nC102 lsuun esr {val("C102")}\n{esr_drive}') if esr_drive else \
        f'C102 lsuun esr {val("C102")}\nR106 esr 0 1e12'
    return f"""* wideband front end + LSU 4.9 equivalent
V33 v33 0 3.3
Vdda vdda 0 3.3
R101 vdda vmref {val('R101')}
R102 vmref 0 {val('R102')}
C101 vmref 0 {val('C101')}
XVM vmref wbvm wbvm mcp
R109 lsuvm wbvm {val('R109')}
C104 lsuvm 0 {val('C104')}
{dac}
R131 dac pumpn {val('R131')}
R133 pump pumpn {val('R133')}
C103 pump pumpn {val('C103')}
R132 pumpp wbvm {val('R132')}
R134 lsurt pumpp {val('R134')}
XPU pumpp pumpn pump mcp
R108 lsurt pump {val('R108')}
R110 lsurt lsuip {val('R110')}
* pump cell: IP -> VM, resistance rp (assumed), current monitor Vpc
Rpc lsuip pcx {rp}
Vpc pcx lsuvmw 0
RF2 lsuvmw lsuvm {max(RF2, 1e-3)}
R112 lsuip isp {val('R112')}
R115 isp wbvm {val('R115')}
R111 lsurt isn {val('R111')}
R117 isout isn {val('R117')}
XIS isp isn isout ad86
R124 isout ipsense {val('R124')}
C111 ipsense 0 {val('C111')}
* Nernst cell held at 450 mV by the loop; internal resistance ri; R114 reference pump current from +3V3
R114 v33 lsuun {val('R114')}
Rn lsuun nx {ri}
Vnern nx lsuvmw 0.45
XBF lsuun unbuf unbuf mcp
R104 unbuf unp {val('R104')}
R105 unp 0 {val('R105')}
R103 lsuvm unn {val('R103')}
R107 unn unsense {val('R107')}
XUN unp unn unsense mcp
{esr}
{OPAMP}
"""


# W1: DC operating point at each lambda. The firmware's pump loop holds the Nernst cell at 450 mV; at steady state
# that means the pump current equals Bosch's Ip(lambda). Modelled with the firmware's own feed-forward
# (pump_dac.cpp: V = 1.65 - 0.000321162 * uA) plus a high-gain servo standing in for its PI loop; DAC = PWM of VDD,
# 0-3.3 V.
wrows = []
for rp in (100.0, 300.0):
    for lam, ip in LSU_IP:
        it = ip * 1e-3
        # feed-forward + integrating servo (stands in for the firmware's PI loop), settled in a 30 ms transient
        dac = (f'Bdac dac 0 V = max(0, min(3.3, 1.65 - 321.162*{it} + V(ci)))\n'
               f'Bci 0 ci I = 2e-3*(i(Vpc) - ({it}))/1e-3\nCci ci 0 1u\nRci ci 0 1e9')
        vec = ['v(dac)', 'v(pump)', 'v(isout)', 'v(ipsense)', 'v(wbvm)', 'v(lsuvm)', 'v(unsense)', 'i(Vpc)']
        net = wb_front(rp, 300.0, dac=dac) + '.tran 10u 30m uic\n.control\nrun\nwrdata @DAT@ @VEC@\n.endc\n.end\n'
        dd = spice('wb_dc', net, vec)
        r = {k: float(np.mean(dd[k][dd['time'] > 27e-3])) for k in vec}
        ip_fw = (r['v(ipsense)'] - r['v(wbvm)']) * (-1000 / (10 * 61.9))
        wrows.append(dict(rp=rp, lam=lam, ip=ip, r=r, ip_fw=ip_fw, lam_fw=fw_lambda(ip_fw)))
ok_rows = [w for w in wrows if w['rp'] == 300.0]
pump_lo = min(w['r']['v(pump)'] for w in ok_rows)
pump_hi = max(w['r']['v(pump)'] for w in ok_rows)
is_lo = min(w['r']['v(isout)'] for w in ok_rows)
is_hi = max(w['r']['v(isout)'] for w in ok_rows)
dac_lo = min(w['r']['v(dac)'] for w in ok_rows)
dac_hi = max(w['r']['v(dac)'] for w in ok_rows)
ierr = max(abs(w['r']['i(Vpc)'] * 1000 - w['ip']) for w in ok_rows)
sat = [w for w in wrows if not (0.06 < w['r']['v(pump)'] < 3.24) or abs(w['r']['i(Vpc)'] * 1000 - w['ip']) > 0.02]
record('Wideband', 'pump current lambda 0.65 .. air (-2.00 .. +2.55 mA), pump cell 300 ohm (assumed)',
       f'pump driver out {pump_lo:.2f} .. {pump_hi:.2f} V, DAC {dac_lo:.2f} .. {dac_hi:.2f} V, AD8628 out '
       f'{is_lo:.3f} .. {is_hi:.3f} V (ADC 0-3.3 V); pump current error {ierr * 1000:.1f} uA',
       'OK' if is_lo > 0.03 and is_hi < 3.27 and not [w for w in sat if w['rp'] == 300.0] else 'CHECK',
       'Howland source: (Vm - DAC) / 319.6 ohm, +-5.2 mA available')
w100 = [w for w in wrows if w['rp'] == 100.0]
air = [w for w in ok_rows if w['lam'] == 99][0]
rich = [w for w in ok_rows if w['lam'] == 0.65][0]
vm = air['r']['v(lsuvm)']
head_lean = (3.25 - vm) / (2.55e-3) - val('R108') - val('R110')
head_rich = (vm - 0.05) / (2.0e-3) - val('R108') - val('R110')
record('Wideband', 'pump driver headroom (MCP6004 50 mV from the rails)',
       f'works up to a pump-cell resistance (incl. its back-EMF) of {head_lean:.0f} ohm in air and {head_rich:.0f} ohm '
       f'at lambda 0.65', 'OK' if min(head_lean, head_rich) > 300 else 'CHECK',
       'LSU 4.9 pump-cell impedance is not in the Bosch sheet; FOME/rusEFI run the same values')
lam_err = max(abs(w['lam_fw'] - w['lam']) / w['lam'] for w in ok_rows if 0.65 <= w['lam'] <= 1.7)
record('Wideband', 'firmware lambda from the simulated ADC readings, lambda 0.65-1.70',
       f'worst {lam_err * 100:.1f} % (R110 62 ohm vs the firmware 61.9; includes the firmware fit vs Bosch table); '
       f'Ip at air reads {air["ip_fw"]:.2f} mA (firmware caps lambda at 2 above 1.11 mA)',
       'OK' if lam_err < 0.05 else 'CHECK', 'most of it is rusEFI\'s linear fit at the rich end (lambda 0.65: fit '
       f'gives {fw_lambda(-2.0):.3f})')
record('Wideband', 'virtual ground and Nernst sense',
       f'WB_VM {air["r"]["v(wbvm)"]:.3f} V, LSU_VM {rich["r"]["v(lsuvm)"]:.3f} .. {air["r"]["v(lsuvm)"]:.3f} V '
       f'(R109 drop); Un_sense {air["r"]["v(unsense)"]:.3f} V = {air["r"]["v(unsense)"] / 2.7 * 1000:.0f} mV x 2.7 '
       f'(450 mV + {(3.3 - air["r"]["v(lsuvm)"] - 0.45) / val("R114") * 300 * 1000:.1f} mV from the R114 reference current)',
       'OK')

# W2: ESR injection: 0/3.3 V square on WB_ESR_49 (PB7) through R106 22k and C102 100 nF; the firmware toggles it after
# every ADC sample (sampling_thread: 1 ms sleep + conversion, assumed 1.2 ms half period) and computes
# ESR = 22k / (3.3 / AC - 1) - 10 from the AC amplitude of Un.
HALF = 1.2e-3
esr_rows = []
for ri in (300.0, 1000.0, 3000.0):
    drive = f'Vesr esr49 0 PULSE(0 3.3 0 1u 1u {HALF - 2e-6} {2 * HALF})'
    dac = 'Vdac dac 0 1.65'
    net = wb_front(300.0, ri, esr_drive=drive, dac=dac) + tran_ctl('5u', f'{40 * HALF} uic', '5u').replace(
        f'{40 * HALF} uic 0 5u', f'{40 * HALF} 0 5u uic')
    d = spice('wb_esr', net, ['v(unsense)', 'i(Vnern)'])
    t, v = d['time'], d['v(unsense)'] / 2.7
    samples = []
    for k in range(20, 39):
        te = (k + 1) * HALF - 5e-6
        samples.append(pin_avg(t, v, te - 0.16e-3, te))
    acs = [abs((samples[j - 1] + samples[j + 1]) / 2 - samples[j]) for j in range(1, len(samples) - 1)]
    ac = float(np.mean(acs))
    esr_fw = val('R106') / (3.3 / ac - 1) - (val('R109') + RF2)      # firmware: VM_RESISTOR_VALUE = R109 + F2
    inern = float(np.max(np.abs(d['i(Vnern)'][t > 10 * HALF])))
    esr_rows.append((ri, ac, esr_fw, inern))
r300 = esr_rows[0]
# true ESR at which the firmware reads 300 ohm (linear interpolation of the bias)
bias = r300[2] / r300[0]
LSU49_T = ([80, 100, 150, 200, 250, 300, 350, 400, 450, 550, 650, 800, 1000, 1200, 2500, 4500],
           [1030, 972, 888, 840, 806, 780, 761, 744, 729, 703, 686, 665, 642, 628, 567, 500])
t_true = float(np.interp(300 / bias, *LSU49_T))
record('Wideband', 'ESR injection (22k, 3.3 V square, 1.2 ms half period) into a 300 ohm Nernst cell',
       f'AC {r300[1] * 1000:.1f} mV at the cell = {r300[1] * 2.7 / LSB:.0f} LSB at PA0; firmware ESR {r300[2]:.0f} ohm '
       f'(cold 1k / 3k: {esr_rows[1][2]:.0f} / {esr_rows[2][2]:.0f} ohm); cell current {r300[3] * 1e6:.0f} uA peak (Bosch max 250 uA)',
       'OK' if r300[1] * 2.7 / LSB > 20 and r300[3] < 250e-6 and abs(bias - 1) < 0.1 else 'CHECK',
       f'readable. C102 (100 nF, tau {val("R106") * val("C102") * 1000:.1f} ms) droops within each half period, so the '
       f'firmware under-reads ESR by {(1 - bias) * 100:.0f} %: its 300 ohm target is a true ~{300 / bias:.0f} ohm, '
       f'i.e. the sensor runs at ~{t_true:.0f} C instead of 780 C (inherited from the FOME module; cell capacitance '
       'not modelled)' if abs(bias - 1) >= 0.1 else 'readable')

# W3: heater. Q101 VND14NV04 (ST datasheet): clamp 40/45/55 V, Rds(on) 35/70 mOhm at VIN 5 V, current limit 12/18/24 A
# at VIN 5 V, input threshold 0.5-2.5 V, input current 100 uA, RthJA 65 C/W (DPAK, 0.5 cm2). Here VIN = F103 VOH
# (3.0-3.3 V with R126 1k + the LED on the pin) through R125 1k: Rds(on)/limit at that input not specified (assumed
# 2 x 35 mOhm). Heater (assumed): Bosch 7.5 W at 7.5 V -> 7.5 ohm hot; cold 2.5 / 3.2 / 4.0 ohm, R linear in
# temperature; thermal model C = 0.1 J/K, Rth = 760 K / 7.5 W (free air). Supply: VBAT_IN -> motherboard F1 (2 A hold
# PTC, ~0.1 ohm assumed) -> harness 0.1 ohm. Firmware (heater_control.cpp): 2 V for 5 s (preheat), then ramp from 7 V
# at 0.4 V/s up to 12 V until the sensor is within 30 C of 780 C; PWM 390 Hz; duty = (Veff / Vbatt)^2.
on('F1', 'VBAT_IN', 'HTR_PWR', parts=MB['2001-05'])
RDS_H = 0.07
for vb in (9.0, 16.0):
    net = f"""* heater inrush, cold heater
Vb vb 0 {vb}
Rf1 vb hp 0.1
Rh hp h1 0.1
Lh h1 h2 1u
Rht h2 hn 2.5
Vg g 0 PULSE(0 5 10u 1u 1u 500u 2.56m)
Vdi hn d 0
Bq d 0 I = V(g) > 2.5 ? min(12, V(d)/{RDS_H}) : 0
Dcl 0 d dvnd
.model dvnd d(bv=40 ibv=1m is=1e-14 rs=0.1)
""" + tran_ctl('0.1u', '1m')
    dd = spice('htr', net, ['i(Vdi)'])
    ipk = float(np.max(dd['i(Vdi)']))
    record('Wideband heater', f'cold heater (2.5 ohm assumed) switched on at {vb:.0f} V',
           f'{ipk:.1f} A peak through Q101 (VND14NV04 limit >= 12 A at VIN 5 V)', 'OK' if ipk < 12 else 'CHECK')


def heater_profile(rcold, vb, ta=25.0):
    C, Rth = 0.1, 760 / 7.5
    alpha = (7.5 / rcold - 1) / 760
    T, t, dt = ta, 0.0, 0.01
    veff = 2.0
    ramp = 7.0
    worst_rms, worst_t, pq = 0.0, 0.0, 0.0
    while t < 60:
        rh = rcold * (1 + alpha * (T - 20))
        if t < 5:
            veff = 2.0
        elif T < 750:
            ramp = min(12.0, ramp + 0.4 * dt)
            veff = ramp
        else:
            veff = 7.5
        rtot = rh + 0.2 + RDS_H
        duty = min(1.0, (veff / vb) ** 2)
        ipk = vb / rtot
        irms = ipk * math.sqrt(duty)
        p = irms ** 2 * rh
        T += (p - (T - ta) / Rth) / C * dt
        if irms > worst_rms:
            worst_rms, worst_t = irms, t
        pq = max(pq, irms ** 2 * RDS_H + 0.5 * vb * ipk * 10e-6 * 390)   # + switching, 5 us edges at 1k (assumed)
        t += dt
        if T >= 750 and t > 5 + 1:
            break
    return worst_rms, worst_t, t, pq


hp = {(rc, vb): heater_profile(rc, vb) for rc in (2.5, 3.2, 4.0) for vb in (12.0, 14.4)}
worst = max(hp.values(), key=lambda x: x[0])
# PTC hold current from the motherboard part (value 'N A hold'); PPTC hold current derates about 20 % by 60 C
F1_HOLD = float(MB['2001-05']['F1']['value'].split('A')[0])
F1_HOLD60 = 0.8 * F1_HOLD
record('Wideband heater', f'warm-up (firmware profile) RMS current vs motherboard F1 ({F1_HOLD:g} A hold PTC, '
       f'~{F1_HOLD60:.1f} A at 60 C)',
       '; '.join(f'cold {rc:g} ohm: {hp[(rc, 14.4)][0]:.2f} A rms (at {hp[(rc, 14.4)][1]:.0f} s), hot in {hp[(rc, 14.4)][2]:.0f} s'
                 for rc in (2.5, 3.2, 4.0)),
       'OK' if worst[0] < F1_HOLD60 else 'CHECK',
       f'{worst[0] / F1_HOLD60 * 100:.0f} % of the derated hold current at worst' if worst[0] < F1_HOLD60 else
       f'at the start of the 7 V ramp a cold heater draws more than the {F1_HOLD:g} A hold current (hold derates further '
       'when warm): the PTC may trip during warm-up and the controller then times out. Measure the sensor\'s cold heater '
       'resistance; a higher-hold part or starting the ramp lower would avoid it')
record('Wideband heater', 'Q101 dissipation during warm-up and steady PWM',
       f'{worst[3]:.2f} W worst (warm-up, 70 mOhm assumed at the 3.1 V input), about '
       f'{(7.5 / 7.5) ** 2 * RDS_H + 0.5 * 14.4 * 1.9 * 10e-6 * 390:.2f} W steady (1 A rms): Tj rise '
       f'{worst[3] * 65:.0f} C at 65 C/W', 'OK' if worst[3] * 65 + 85 < 150 else 'CHECK',
       'VND14NV04 Rds(on) and current limit are specified at VIN = 5 V only; the F103 drives ~3.1 V (as on the FOME module)')
# LSU signal wire shorted to the heater supply. Rev 0.7: the Nernst buffer input (U101 pin 10) through R137 10k, and
# F103 PA1 no longer on LSU_VM. The pump and virtual-ground drive paths (R108/R110 to U101A, R109 to U101D) carry
# the pump current and can't take series resistance without changing the analog design.
un_r = between('LSU_UN', 'WB_UN_IN')['ref'] if DB['U101']['pads']['10'] == 'WB_UN_IN' else None
pa1 = DB['U102']['pads'].get('11', '')
un_txt = (f'LSU_UN: {(14.4 - 3.6) / val(un_r) * 1000:.1f} mA into the MCP6004 input through {un_r} (2 mA max)' if un_r
          else 'LSU_UN: 14.4 V directly on the MCP6004 input (abs max VDD + 1 V, recalled)')
pa1_txt = 'F103 PA1 not connected' if not pa1 else f'F103 PA1 on {pa1} (through nothing)'
record('Wideband', 'LSU signal wire shorted to the 12 V heater feed: sense inputs',
       f'{un_txt}; LSU_IP and LSU_RT: {(14.4 - 3.6) / val("R112") * 1000:.1f} / {(14.4 - 3.6) / val("R111") * 1000:.1f} mA into '
       f'the AD8628 inputs through R112 / R111; {pa1_txt}',
       'OK' if un_r and not pa1 else 'CHECK')
# Rev 0.8: drive clamps D40/D41 (B5819W) from the op-amp outputs to +3V3, the +3V3 shunt clamp (TL431 + BCP53), F2
# (nSMD010 PTC: 0.1 A hold, 0.25 A trip, 1.6 ohm, 1 s max to trip) in the VM wire, R108/R109/R110 in 1206 (0.25 W).
def shunt_clamp(i_inj, t_on=5e-3):
    """+3V3 rail with the LDO (sources only), 150 mA of load, ~35 uF of decoupling and the TL431/BCP53 shunt, hit by an
    injected fault current. TL431 modelled as a transconductance (7 A/V at REF, 1.8 kHz pole, 0-150 mA), BCP53 as a
    PNP (hFE 60). C63 + C68 (rev 0.8: 2 x 100 uF X5R 1206 bulk on the rail, no compensation cap) count at half their
    value (DC bias at 3.3 V). Returns (rail peak V, rail at the end of the pulse, ringing p-p)."""
    net = f"""* +3V3 shunt clamp
Bldo 0 r I = max(0, min(1.2, (3.30 - V(r)) / 0.01))
Rload r 0 22
Cbulk r 0 35u
Resr r cb 0.05
Ccer cb 0 1u
Iinj 0 r PULSE(0 {i_inj} 1m 1u 1u {t_on} 100)
R141 r k {val('R141')}
Qp 0 k r bcp53
.model bcp53 pnp(is=1e-13 bf=60 vaf=100 rb=5 re=0.05 rc=0.1 cje=60p cjc=25p tf=2n)
R142 r ref {val('R142')}
R143 ref 0 {val('R143')}
C63 r 0 {0.5 * sum(sv(DB[c]['value']) for c in ('C63', 'C68') if c in DB):.4g}
Be e 0 V = 562 * (V(ref) - 2.495)
Re e ef 1k
Ce ef 0 {1 / (2 * math.pi * 1.8e3 * 1e3):.4g}
Bk k 0 I = max(0, min(0.15, V(ef) / 562 * 7))
{MODELS}
""" + tran_ctl('0.5u', f'{1e-3 + t_on + 2e-3}')
    d = spice('shunt', net, ['v(r)', 'i(Vq)'] if False else ['v(r)'])
    t, v = d['time'], d['v(r)']
    m = (t > 1e-3) & (t < 1e-3 + t_on)
    late = (t > 1e-3 + t_on * 0.6) & (t < 1e-3 + t_on)
    return float(np.max(v)), float(v[m][-1]), float(np.max(v[late]) - np.min(v[late]))


if 'U15' in DB and DB['U15']['value'].startswith('TL431'):
    on('U15', 'SH_K', 'SH_REF', 'GND'); on('Q20', 'SH_K', 'GND', '+3V3'); on('C63', '+3V3', 'GND')
    if 'C68' in DB:
        on('C68', '+3V3', 'GND')
    th = 2.495 * (1 + val('R142') / val('R143'))
    rows = []
    worst = 0.0
    for iinj in (0.1, 0.5, 1.0):
        pk, end, rip = shunt_clamp(iinj)
        worst = max(worst, pk)
        rows.append(f'{iinj:.1f} A: peak {pk:.2f} V, holds {end:.2f} V, ripple {rip * 1000:.0f} mV p-p')
    record('Power', f'+3V3 shunt clamp (TL431 at {th:.2f} V + BCP53), fault current injected into +3V3',
           '; '.join(rows) + f'; threshold above the LDO maximum 3.37 V', 'OK' if worst < 3.9 and th > 3.40 else 'CHECK',
           'MCU absolute maximum 4.0 V')
VB_S = 14.4
v_cl = 3.6 + 0.35            # rail held by the shunt + B5819W drop at ~0.1-1 A
i_rt = (VB_S - v_cl) / val('R108')
i_ip = (VB_S - v_cl) / (val('R110') + val('R108'))
i_vm = (VB_S - v_cl) / (val('R109') + (1.6 if 'F2' in DB else 0))
clamped = 'D40' in DB and 'D41' in DB
if clamped:
    record('Wideband', 'LSU signal wire shorted to the 12 V heater feed: pump and virtual-ground drive (rev 0.8)',
           f'RT: {i_rt * 1000:.0f} mA through R108 ({i_rt ** 2 * val("R108"):.1f} W) into D40; IP: {i_ip * 1000:.0f} mA '
           f'through R110 + R108 ({i_ip ** 2 * val("R110"):.2f} / {i_ip ** 2 * val("R108"):.2f} W); VM: {i_vm:.2f} A through '
           f'F2 + R109 ({i_vm ** 2 * val("R109"):.1f} W) into D41 until F2 trips (under 1 s); U101 and both MCUs protected: '
           'the clamps hold the op-amp outputs at the +3V3 rail plus a Schottky drop, and the shunt clamp holds the rail',
           'CHECK', 'the 1206 resistors are overloaded while the short lasts: R108 opens in an RT short (a fuse, ~1 cent to '
           'replace) and R110/R108 run hot in an IP short; check or replace them after such a fault. The ICs survive')
else:
    record('Wideband', 'LSU signal wire shorted to the 12 V heater feed: pump and virtual-ground drive',
           f'IP or RT: {(14.4 - 3.3) / (val("R110") + val("R108")) * 1000:.0f} mA through R110/R108 into U101A\'s output; VM: '
           f'{(14.4 - 1.65) / val("R109"):.1f} A through R109 into U101D\'s output',
           'CHECK', 'inherited from the FOME module: these paths carry the pump current, so a short of IP, RT or VM to battery '
           'still damages U101 and R108-R110. Protecting them needs a different front end (a CJ125-class interface IC)')

# =================================================================================================================
# N. rev 0.10: flex-fuel and nitrous inputs, microSD socket
# =================================================================================================================
# Flex-fuel sensor (GM/Continental type; a reproduction of GM's service text, read 2026-11-13): 12 V supply, the ECU
# pulls the signal line up to 5 V, the sensor pulls it to ground; 50 Hz = 0 % ethanol, 150 Hz = 100 %, low pulse 1-5 ms
# with fuel temperature. Here: R35 4.7k to V5_EXT on every motherboard, then R139 10k, C72 1 nF and the BAT54S clamp
# D36 at PC6. Sensor output assumed 50 ohm when on; harness 2 nF (pessimistic).
on('R139', 'FLEX_M', 'IN_FLEX'); on('D36', 'GND', '+3V3', 'FLEX_M'); on('C72', 'FLEX_M', 'GND')
on('R140', 'N2O_ARM_M', 'IN_N2O'); on('D37', 'GND', '+3V3', 'N2O_ARM_M'); on('C73', 'N2O_ARM_M', 'GND')
assert DB['U1']['pads']['63'] == 'FLEX_M' and DB['U1']['pads']['64'] == 'N2O_ARM_M'      # PC6 (EXTI 6), PC7
for _y, _ in YEARS:
    on('R35', 'V5_EXT', 'IN_FLEX', parts=MB[_y]); on('R36', 'IN_N2O', 'GND', parts=MB[_y])
R_FLEX_PU, R_N2O_PD = val('R35', MB['2001-05']), val('R36', MB['2001-05'])


def flex_in(freq, tlow, vsrc=None):
    """Flex input at the pin. vsrc: the wire shorted to that voltage instead of the sensor. Returns pin high and low
    levels, the delay from the sensor's edges to the pin crossing VIL (falling) and VIH (rising), and the pin's period."""
    per = 1.0 / freq
    drive = (f'Vf in 0 {vsrc}' if vsrc is not None else
             f'Rp v5 in {R_FLEX_PU}\nCh in 0 2n\nSs in 0 g 0 ssw\n.model ssw sw(vt=0.5 ron=50 roff=100meg)\n'
             f'Vg g 0 PULSE(0 1 0.2m 1u 1u {tlow} {per})')
    net = f"""* flex-fuel input
V5 v5 0 5
V33 v33 0 3.3
{drive}
Rs in m {val('R139')}
Cm m 0 {val('C72') + 5e-12}
Dh m v33 dbat54
Dl 0 m dbat54
Vi33 v33 v33x 0
Rl33 v33x 0 22
{MODELS}
""" + tran_ctl('0.5u', f'{2 * per + 0.6e-3}')
    d = spice('flex', net, ['v(m)', 'v(in)', 'i(Vi33)'])
    t, m = d['time'], d['v(m)']
    out = dict(hi=float(np.max(m[t > per])), lo=float(np.min(m[t > 0.3e-3])), iclamp=float(-np.min(d['i(Vi33)'])) if vsrc else 0.0)
    if vsrc is None:
        falls = [float(t[k]) for k in range(1, len(t)) if m[k - 1] >= VIL > m[k]]
        rises = [float(t[k]) for k in range(1, len(t)) if m[k - 1] <= VIH < m[k]]
        out.update(tfall=falls[0] - 0.2e-3, trise=rises[0] - (0.2e-3 + tlow), period=falls[1] - falls[0],
                   low=rises[0] - falls[0])
    return out


for _f, _tl in ((50.0, 5e-3), (150.0, 1e-3)):
    _r = flex_in(_f, _tl)
    record('In flex', f'flex-fuel sensor at {_f:.0f} Hz, {_tl * 1e3:.0f} ms low pulse',
           f'pin {_r["lo"]:.2f} V low / {_r["hi"]:.2f} V high (thresholds {VIL:.2f} / {VIH:.2f} V); edges reach the pin '
           f'{_r["tfall"] * 1e6:.0f} us (falling) and {_r["trise"] * 1e6:.0f} us (rising) late; period {_r["period"] * 1e3:.3f} ms '
           f'(sensor {1e3 / _f:.3f}), low pulse {_r["low"] * 1e3:.3f} ms (sensor {_tl * 1e3:.3f})',
           'OK' if _r['lo'] < VIL - 0.3 and _r['hi'] > VIH + 0.3 and abs(_r['period'] * _f - 1) < 0.002 else 'CHECK',
           'the frequency (ethanol) is exact; the low pulse (fuel temperature) reads '
           f'{(_r["low"] - _tl) * 1e6:+.0f} us off, under 1 C on the sensor\'s 4 ms / 165 C scale')
for _v in (14.4, 24.0):
    _r = flex_in(100.0, 2e-3, vsrc=_v)
    _p = (_v - _r['hi']) ** 2 / val('R139')
    record('In flex', f'flex or nitrous wire shorted to {_v:.1f} V',
           f'{_r["hi"]:.2f} V at the pin (5 V tolerant: {FT_MAX:.1f} V allowed), {(_v - _r["hi"]) / val("R139") * 1e3:.2f} mA into +3V3 '
           f'through the clamp, {_p * 1e3:.0f} mW in the 10k (0603: 100 mW)',
           'OK' if _r['hi'] < FT_MAX and _p < 0.1 else 'CHECK')
# nitrous arming switch: battery through the switch to IN_N2O, R36 10k to ground on the motherboard, R140 10k, C73 10 nF
_tau = val('R140') * val('C73')
record('In flex', 'nitrous arming switch (to battery; 10k pull-down on the motherboard)',
       f'open: 0 V (pulled down through {R_N2O_PD / 1e3:.0f}k + {val("R140") / 1e3:.0f}k); closed: clamped at about 3.5 V from any battery '
       f'voltage above {VIH:.1f} V, so it reads armed down to a {VIH:.1f} V supply; filter {_tau * 1e6:.0f} us',
       'OK', f'the switch carries {14.4 / R_N2O_PD * 1e3:.1f} mA at 14.4 V')

# microSD socket J4 on +3V3: a card pushed in while the board runs. Assumed: an uncharged 5 uF inside the card (the
# SD limit as recalled), 50 mOhm / 10 nH of contact; C70 (10 uF, about 6 uF at 3.3 V) and C69 at the socket; the two
# 100 uF bulk capacitors C63/C68 (about 45 uF each at 3.3 V bias, assumed) 10 mm away through the plane (10 mOhm, 5 nH).
# The regulator is a slow source (0.2 ohm, 1 uH: it supplies the running load and does nothing within microseconds).
on('J4', '+3V3', 'GND', 'SD_SCK', 'SD_MISO', 'SD_MOSI', 'SD_CS'); on('C70', '+3V3', 'GND'); on('C63', '+3V3', 'GND'); on('C68', '+3V3', 'GND')
for _n in ('SD_CS', 'SD_MISO', 'SD_MOSI', 'SD_DAT1', 'SD_DAT2'):
    assert any(p['value'] == '47k' and set(p['pads'].values()) == {'+3V3', _n} for p in design.parts), f'no pull-up on {_n}'
net = f"""* microSD hot insertion
Cb bulk 0 {2 * 45e-6 + C33_EFF} ic=3.3
Rb bulk b1 0.01
Lb b1 sock 5n
Cs sock s1 6.1u ic=3.3
Rse s1 0 0.005
Sw sock c1 g 0 sins
.model sins sw(vt=0.5 ron=0.05 roff=100meg)
Vg g 0 PULSE(0 1 0.1m 100n 100n 10m 20m)
Lc c1 c2 10n
Cc c2 0 5u ic=0
Il bulk 0 {I33 - 0.10}
Vreg r0 0 {3.3 + (I33 - 0.10) * 0.2}
Rreg r0 r1 0.2
Lreg r1 bulk 1u ic={I33 - 0.10}
.tran 20n 0.6m 0 20n uic
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
d = spice('sd_insert', net, ['v(bulk)', 'v(sock)'])
_vb, _vs = float(np.min(d['v(bulk)'])), float(np.min(d['v(sock)']))
record('Power', 'microSD card pushed in while running (5 uF uncharged in the card, assumed)',
       f'+3V3 dips to {_vb:.2f} V at the bulk capacitors (the processors) and {_vs:.2f} V at the socket',
       'OK' if _vb > F4_VMIN_168 else 'CHECK',
       f'above the {F4_VMIN_168:.1f} V the F407 needs at 168 MHz and its {F4_BOR_FALL:.1f} V brown-out reset')

# A card's supply current is 100 mA at most averaged over a second in default speed, with peaks of "several hundred
# mA" for up to about 1 ms while its controller and flash work (Swissbit AN2111, read 2026-11-13). Case: 0.4 A for 1 ms
# on top of the running load, with the same slow regulator model as above (its real load-step response is not modelled).
net = f"""* microSD write peak
Cb bulk 0 {2 * 45e-6 + C33_EFF} ic=3.3
Rb bulk b1 0.01
Lb b1 sock 5n
Cs sock s1 6.1u ic=3.3
Rse s1 0 0.005
Ipk sock 0 PULSE(0 0.4 0.1m 1u 1u 1m 20m)
Il bulk 0 {I33 - 0.10}
Vreg r0 0 {3.3 + (I33 - 0.10) * 0.2}
Rreg r0 r1 0.2
Lreg r1 bulk 1u ic={I33 - 0.10}
.tran 0.2u 1.6m 0 0.2u uic
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
d = spice('sd_peak', net, ['v(bulk)', 'v(sock)'])
_vb, _vs = float(np.min(d['v(bulk)'])), float(np.min(d['v(sock)']))
record('Power', 'microSD write peak: 0.4 A for 1 ms at the socket (Swissbit: "several hundred mA", up to 1 ms)',
       f'+3V3 dips to {_vb:.2f} V at the processors and {_vs:.2f} V at the socket',
       'OK' if _vb > F4_VMIN_168 and _vs > 2.7 else 'CHECK',
       'above 2.7 V, the minimum for a card; the regulator is modelled as 0.2 ohm behind 1 uH, its own load-step '
       'response is not')

# ---- report -----------------------------------------------------------------------------------------------------
w = max(len(r[1]) for r in results)
for area, check, value, verdict, note in results:
    print(f'[{verdict:5s}] {area:16s} {check:<{w}s}  {value}')
    if note:
        print(' ' * 26 + note)
cnt = {k: sum(1 for r in results if r[3] == k) for k in ('OK', 'CHECK', 'REF', 'FAIL')}
print(f'\n{cnt["OK"]} OK / {cnt["CHECK"]} CHECK / {cnt["REF"]} REF / {cnt["FAIL"]} FAIL in {time.time() - T0:.0f} s')
if cnt['FAIL']:
    sys.exit(1)
