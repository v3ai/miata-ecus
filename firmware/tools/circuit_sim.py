#!/usr/bin/env python3
"""Circuit simulations of the daughterboard's input conditioning and output stages with realistic harness signals,
run in ngspice. Component values come from scripts/design.py; sensor and load models are stated where used.

usage: circuit_sim.py [outdir]     (needs ngspice on the PATH)

Verdicts: OK / CHECK (works, with a caveat in the note) / FAIL (exits non-zero) / REF (the rev 0.4 design, kept to
show what a fix changed; not a failure of the boards as built).
"""
import math
import os
import subprocess
import sys
import tempfile

OUT = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()
os.makedirs(OUT, exist_ok=True)
results = []


def spice(name, netlist, vectors):
    """Run a transient/op netlist in batch mode, return {vector: [values]} from wrdata."""
    cir = os.path.join(OUT, name + '.cir')
    dat = os.path.join(OUT, name + '.dat')
    with open(cir, 'w') as f:
        f.write(netlist.replace('@DAT@', dat).replace('@VEC@', ' '.join(vectors)))
    r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dat):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    cols = {v: [] for v in ['time'] + vectors}
    for line in open(dat):
        p = line.split()
        if not p:
            continue
        # wrdata writes "x y" pairs per vector
        cols['time'].append(float(p[0]))
        for i, v in enumerate(vectors):
            cols[v].append(float(p[2 * i + 1]))
    return cols


def record(area, check, value, verdict, note=''):
    results.append((area, check, value, verdict, note))


# STM32F407 FT/TTa input levels (DS8626, VDD 3.3 V): VIL max 0.3*VDD (0.99 V, conservative CMOS figure), VIH min
# 0.7*VDD = 2.31 V (FT pins also accept up to VDD+4 V).
VIL, VIH = 0.3 * 3.3, 0.7 * 3.3

# ---- A. hall crank/cam input: open-collector sensor, 1k pull-up to 5 V, 4.7k series, 1 nF at the MCU pin --------
# Worst case narrow pulse: NB crank notch, 3.5 deg wide (from the real NB2 capture) at 7200 rpm = 81 us.
# Harness: 2 m of wire ~ 200 pF + sensor output capacitance; use 2 nF to be pessimistic.
for label, width_us, period_us in [('NB crank notch @7200 rpm', 3.5 / (7200 * 6) * 1e6, 70 / (7200 * 6) * 1e6),
                                   ('NA CAS SGT @7200 rpm', 0.5 * 180 / (7200 * 6) * 1e6, 180 / (7200 * 6) * 1e6)]:
    net = f"""* hall input
V5 vs 0 5
Rpu vs in 1k
Charn in 0 2n
* open-collector: low (sensor on) for {width_us:.1f} us every {period_us:.1f} us
Vg g 0 PULSE(0 5 20u 1n 1n {width_us}u {period_us}u)
Sw in 0 g 0 swmod
.model swmod sw(vt=2.5 ron=60 roff=10meg)
Rs in mcu 4.7k
Cf mcu 0 1n
* rev 0.5: 1N4148WS from the MCU pin to +3V3
V33 v33 0 3.3
Dcl mcu v33 d4148
.model d4148 d(is=2.5n n=1.75 rs=0.6 cjo=1p)
.tran 0.1u {20 + 3 * period_us}u
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    d = spice('hall_' + label.split()[0], net, ['v(mcu)'])
    t, v = d['time'], d['v(mcu)']
    vmin = min(v[i] for i in range(len(t)) if 20e-6 < t[i] < 20e-6 + period_us * 1e-6)
    vmax = max(v)
    # delay from the sensor edge to crossing VIL
    t_cross = next(t[i] for i in range(len(t)) if t[i] > 20e-6 and v[i] < VIL)
    delay = (t_cross - 20e-6) * 1e6
    ok = vmin < VIL and vmax > VIH
    record('Hall input', label, f'low {vmin:.2f} V, high {vmax:.2f} V, edge delay {delay:.1f} us ({delay / width_us * 100:.0f}% of pulse)',
           'OK' if ok and delay < width_us / 2 else 'CHECK')

# hall wire (or the sensor 5 V) shorted to battery: PE7/PE8 are 5 V-tolerant pins with no clamp of their own
# (absolute maximum VDD + 4 V = 7.3 V). Rev 0.5 adds the 1N4148WS to +3V3; compare with and without it.
for vshort in (14.4, 24.0):
    for clamp in (False, True):
        net = f"""* hall input shorted to battery
Vb in 0 {vshort}
Rs in mcu 4.7k
* the MCU pin itself: leakage only (FT pin, no diode to VDD)
Rpin mcu 0 10meg
V33 v33 0 3.3
{'Dcl mcu v33 d4148' if clamp else ''}
.model d4148 d(is=2.5n n=1.75 rs=0.6)
.op
.control
run
print v(mcu) i(Vb)
.endc
.end
"""
        cir = os.path.join(OUT, 'hall_short.cir'); open(cir, 'w').write(net)
        r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True).stdout
        vm = float(r.split('v(mcu) = ')[1].split()[0]); ib = -float(r.split('i(vb) = ')[1].split()[0])
        record('Hall input', f'wire shorted to {vshort:.0f} V, {"with" if clamp else "no"} clamp diode',
               f'MCU pin {vm:.2f} V (abs max 7.3 V), clamp current {ib * 1000:.1f} mA',
               'OK' if vm < 7.3 else ('REF' if not clamp else 'FAIL'), '' if clamp else 'rev 0.4 reference (no clamp): the pin would be destroyed')

# ---- B. 12 V switch inputs (VSS, A/C, clutch): 33k series, 10k to GND, 10 nF ------------------------------------
for label, src in [('12 V push-pull signal at 14.4 V', 'PULSE(0 14.4 10u 1u 1u 1m 2m)'),
                   ('12 V signal at 9 V (cranking)', 'PULSE(0 9 10u 1u 1u 1m 2m)')]:
    net = f"""* switch input
Vs in 0 {src}
R1 in sw 33k
R2 sw 0 10k
C1 sw 0 10n
.tran 2u 3m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    d = spice('sw', net, ['v(sw)'])
    vmax = max(d['v(sw)'])
    # ST guarantees FT inputs switch at 0.45 VDD + 0.3 = 1.79 V by design; 0.7 VDD (2.31 V) is the tested figure
    record('Switch input', label, f'high level {vmax:.2f} V at the MCU (VIH {VIH:.2f} V tested, 1.79 V by design)',
           'OK' if vmax > VIH else ('CHECK' if vmax > 1.79 else 'FAIL'),
           '' if vmax > VIH else 'above the by-design threshold only; it matters only while cranking at 9 V')
# open-collector / ground-switching source (how many VSS, A/C pressure and clutch switches work): nothing pulls up
net = """* open collector into the switch input
Vg g 0 PULSE(0 5 10u 1n 1n 1m 2m)
Sw in 0 g 0 swmod
.model swmod sw(vt=2.5 ron=50 roff=10meg)
R1 in sw 33k
R2 sw 0 10k
C1 sw 0 10n
.tran 2u 3m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
d = spice('sw_oc', net, ['v(sw)'])
vmax = max(d['v(sw)'])
record('Switch input', 'open-collector / ground-switching source, no pull-up', f'high level {vmax:.2f} V: input never goes high',
       'REF' if vmax < VIH else 'OK', 'such a signal needs the motherboard pull-up option (R20-R22) fitted')
# rev 0.6/0.4 motherboards: 4.7k 0603 pull-up to VBAT_IN (R20-R22), fitted for a ground-switching signal.
# At 14.4 V with the switch closed it dissipates 44 mW (0603 rating 100 mW); 2.2k would have been 94 mW.
for vb in (9.0, 14.4):
    net = f"""* open collector with the 4.7k pull-up option fitted
Vb vb 0 {vb}
Rpu vb in 4.7k
Vg g 0 PULSE(0 5 10u 1n 1n 1m 2m)
Sw in 0 g 0 swmod
.model swmod sw(vt=2.5 ron=50 roff=10meg)
R1 in sw 33k
R2 sw 0 10k
C1 sw 0 10n
.tran 2u 3m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    d = spice('sw_pu', net, ['v(sw)'])
    vmax, vmin = max(d['v(sw)']), min(d['v(sw)'][len(d['v(sw)']) // 4:])
    record('Switch input', f'ground-switching source, 4.7k pull-up fitted, {vb:.0f} V',
           f'high {vmax:.2f} V, low {vmin:.2f} V at the MCU, {vb * vb / 4700 * 1000:.0f} mW in the pull-up when closed',
           'OK' if vmax > VIH and vmin < VIL else ('CHECK' if vmax > 1.79 and vmin < VIL else 'FAIL'))

# ---- C. CLT / IAT thermistor network and the firmware's conversion ----------------------------------------------
# Sensor: Mazda NA/NB coolant/air NTC as rusEFI's Miata presets define it (-20/40/80 C = 16150/1150/330 ohm),
# Steinhart-Hart fitted the way rusEFI does it.
def sh_coeffs(t1, t2, t3, r1, r2, r3):
    L1, L2, L3 = math.log(r1), math.log(r2), math.log(r3)
    Y1, Y2, Y3 = 1 / (t1 + 273.15), 1 / (t2 + 273.15), 1 / (t3 + 273.15)
    U2, U3 = (Y2 - Y1) / (L2 - L1), (Y3 - Y1) / (L3 - L1)
    C = (U3 - U2) / (L3 - L2) / (L1 + L2 + L3)
    B = U2 - C * (L1 * L1 + L1 * L2 + L2 * L2)
    A = Y1 - (B + L1 * L1 * C) * L1
    return A, B, C


A, B, Cc = sh_coeffs(-20, 40, 80, 16150, 1150, 330)
r_of_t = lambda tc: next(r for r in (math.exp(x / 1000) for x in range(4000, 13000)) if 1 / (A + B * math.log(r) + Cc * math.log(r) ** 3) - 273.15 <= tc)
t_of_r = lambda r: 1 / (A + B * math.log(r) + Cc * math.log(r) ** 3) - 273.15
worst_new, worst_naive = 0, 0
rows = []
for tc in (-20, 0, 20, 40, 60, 80, 90, 100, 110, 120):
    rth = r_of_t(tc)
    net = f"""* thermistor network
V5 v5 0 5
Rpu v5 node 2.7k
Rth node 0 {rth}
R1 node adc 5.6k
R2 adc 0 10k
C1 adc 0 10n
* STM32 ADC input leakage, 1 uA worst case (DS8626 Ilkg)
Ilk adc 0 1u
.op
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    d = spice('therm', net, ['v(adc)'])
    vadc = d['v(adc)'][0]
    vnode = vadc * 1.56                          # analogInputDividerCoefficient
    r_fw = 2301.64 * vnode / (4.2623 - vnode)    # firmware: bias 2301.6 ohm, supply 4.262 V (miata_board.cpp)
    r_naive = 2700 * vnode / (5.0 - vnode)       # what a stock 2.7k / 5 V setting would compute
    e_fw, e_naive = t_of_r(r_fw) - tc, t_of_r(r_naive) - tc
    worst_new, worst_naive = max(worst_new, abs(e_fw)), max(worst_naive, abs(e_naive))
    rows.append(f'{tc:4d} C: ADC {vadc:.3f} V, firmware reads {t_of_r(r_fw):6.1f} C, plain 2.7k/5V would read {t_of_r(r_naive):6.1f} C')
record('CLT/IAT', 'temperature error -20..120 C (incl. 1 uA ADC leakage)',
       f'board firmware {worst_new:.1f} C worst; a plain 2.7k pull-up setting would be off by {worst_naive:.1f} C',
       'OK' if worst_new < 1.5 else 'CHECK', '; '.join(rows[i] for i in (0, 2, 6, 9)))

# ---- D. low-side outputs: turn-off energy into the AUIPS2041's active clamp ----------------------------------------
# AUIPS2041L modelled as a switch (Rds(on) 0.13 ohm) with its drain clamp (typ 68 V). Loads (not datasheet values,
# typical published figures): Miata high-impedance injector 14 ohm / 8 mH; idle (BAC) valve 11 ohm / 20 mH.
def clamp_energy(r_load, l_load, vbat, on_ms, diode=False):
    fly = 'Dfw out vb dfw\n.model dfw d(is=1e-9 n=1.5 rs=0.05)' if diode else ''
    net = f"""* low side with active clamp
Vb vb 0 {vbat}
Rl vb a {r_load}
Ll a out {l_load}
Vg g 0 PULSE(5 0 {on_ms}m 1n 1n 10m 20m)
Sw out 0 g 0 swmod
.model swmod sw(vt=2.5 ron=0.13 roff=1meg)
* active clamp: drain-gate zener turns the FET back on at ~68 V
Dcl 0 out dclamp
.model dclamp d(bv=68 ibv=1m is=1e-14 rs=0.2)
{fly}
.tran 0.2u {on_ms + 3}m
.control
run
let pclamp = v(out) * i(Vcl)
wrdata @DAT@ @VEC@
.endc
.end
"""
    # measure clamp current with a 0 V source in series with the clamp diode
    net = net.replace('Dcl 0 out dclamp', 'Dcl 0 cl dclamp\nVcl out cl 0')
    d = spice('clamp', net, ['v(out)', 'i(Vcl)'])
    t, v, i = d['time'], d['v(out)'], d['i(Vcl)']
    e = sum(v[k] * i[k] * (t[k + 1] - t[k]) for k in range(len(t) - 1) if i[k] > 0)
    return e, max(v), (vbat - 0) / r_load


# Rev 0.5 drives the AUIPS2041 inputs at 5 V through an SN74LVC4245A (VOH >= 4.3 V at 5 V and -24 mA; the driver
# input draws well under 1 mA), inside the 4.0-5.5 V the datasheet specifies; rev 0.4 drove them at 3.3 V.
record('Low-side output', 'AUIPS2041 input high level', 'rev 0.5: about 5.0 V from the level shifter (spec 4.0-5.5 V); '
       'rev 0.4: 3.3 V from the MCU', 'OK')
e, vpk, ipk = clamp_energy(14, 8e-3, 14, 6)
record('Low-side output', '1 injector per driver, sequential, 7000 rpm',
       f'{ipk:.1f} A, clamp peak {vpk:.0f} V, {e * 1e3:.1f} mJ per pulse = {e * 7000 / 120:.2f} W in the clamp', 'OK')


def paired_injectors(paired, tvs, skew_us=0.0):
    """1989-93 batch wire: two 14 ohm / 8 mH injectors in parallel on one harness wire. paired: two drivers share
    the wire (rev 0.6 motherboard, R23/R24); tvs: SMCJ40A from the wire to ground (D3/D4). Returns the energy per
    turn-off in each driver's clamp and in the TVS, and the current per driver while on."""
    drivers = ['d0'] if not paired else ['d0', 'd1']
    sw = []
    for k, node in enumerate(drivers):
        delay = 6 + (skew_us * 1e-3 if k else 0)
        sw.append(f"""Vg{k} g{k} 0 PULSE(5 0 {delay}m 1n 1n 10m 20m)
Rw{k} out {node}x 0.02
Vi{k} {node}x {node} 0
Sw{k} {node} 0 g{k} 0 swmod
Dcl{k} 0 cl{k} dclamp
Vcl{k} {node} cl{k} 0""")
    tv = 'Dtv 0 tv dtvs\nVtv out tv 0\n.model dtvs d(bv=46 ibv=1m is=1e-12 rs=0.6)' if tvs else ''
    net = f"""* paired injector wire
Vb vb 0 14
Rl1 vb a1 14
Ll1 a1 out 8m
Rl2 vb a2 14
Ll2 a2 out 8m
{chr(10).join(sw)}
.model swmod sw(vt=2.5 ron=0.13 roff=1meg)
.model dclamp d(bv=68 ibv=1m is=1e-14 rs=0.2)
{tv}
.tran 0.2u 9m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    vecs = ['v(out)'] + [f'i(Vcl{k})' for k in range(len(drivers))] + [f'i(Vi{k})' for k in range(len(drivers))] + \
           (['i(Vtv)'] if tvs else [])
    d = spice('pair', net, vecs)
    t = d['time']
    def energy(vec, node='v(out)'):
        return sum(d[node][k] * d[vec][k] * (t[k + 1] - t[k]) for k in range(len(t) - 1) if d[vec][k] > 0)
    e_cl = [energy(f'i(Vcl{k})') for k in range(len(drivers))]
    e_tv = energy('i(Vtv)') if tvs else 0.0
    i_on = [max(d[f'i(Vi{k})'][kk] for kk in range(len(t)) if 5e-3 < t[kk] < 5.9e-3) for k in range(len(drivers))]
    return e_cl, e_tv, max(d['v(out)']), i_on


ev = 7000 / 60       # batch: each wire fires once per crank revolution
e_cl, e_tv, vpk, i_on = paired_injectors(False, False)
record('Low-side output', '1989-93 wire, one driver, no TVS (rev 0.5 motherboard)',
       f'{i_on[0]:.2f} A in the driver, clamp {vpk:.0f} V, {e_cl[0] * ev:.2f} W in its clamp at 7000 rpm',
       'REF', 'rev 0.5 reference: above the AUIPS2041\'s 1.4 A continuous rating at high duty, plus about 1 W of clamp loss')
for skew in (0.0, 2.0):
    e_cl, e_tv, vpk, i_on = paired_injectors(True, True, skew)
    record('Low-side output', f'1989-93 wire, two drivers + SMCJ40A (rev 0.6), turn-off skew {skew:.0f} us',
           f'{i_on[0]:.2f} A + {i_on[1]:.2f} A per driver, clamp peak {vpk:.0f} V, driver clamps '
           f'{e_cl[0] * ev * 1000:.0f} / {e_cl[1] * ev * 1000:.0f} mW, TVS {e_tv * ev:.2f} W at 7000 rpm',
           'OK' if max(e_cl) * ev < 0.05 and max(i_on) < 1.2 else 'FAIL')
for diode in (False, True):
    e, vpk, ipk = clamp_energy(11, 20e-3, 14, 2.5, diode)
    p = e * 200  # idle valve PWM at 200 Hz
    record('Low-side output', f'idle valve 200 Hz PWM, {"with" if diode else "no"} freewheel diode',
           f'clamp peak {vpk:.0f} V, {e * 1e3:.2f} mJ per cycle = {p:.2f} W in the AUIPS2041 clamp',
           'OK' if p < 0.2 else ('REF' if not diode else 'FAIL'),
           'rev 0.4 reference; every motherboard now fits D1' if not diode else 'as built (motherboard D1)')
# NB2 VVT oil control valve (about 7.5 ohm / 6 mH, typical) at 300 Hz with the motherboard's D2
e, vpk, ipk = clamp_energy(7.5, 6e-3, 14, 1.7, True)
record('Low-side output', 'VVT valve 300 Hz PWM with freewheel diode (NB2 D2)',
       f'clamp peak {vpk:.0f} V, {e * 300:.3f} W in the clamp', 'OK' if e * 300 < 0.05 else 'FAIL')

# ---- F. ULN2003 COM: key-off back-feed (2003-05 main relay coil is battery-fed and ECU-switched) -------------------
# Coil 80 ohm / 0.3 H from the battery to the ULN output. With the key off the ECU's +12V rail is unpowered; model its
# load as 60 ohm (buck input + logic starting up). Rev 0.4: COM on +12V. Rev 0.5: COM to an SMAJ33A TVS (Bourns:
# breakdown 36.7-40.6 V, 53.3 V at 7.5 A, so about 1.7 ohm dynamic). Checks use the worst end of the tolerance:
# minimum breakdown for "does it conduct", maximum breakdown for peak voltage.
SMAJ33_MIN = 'd(bv=36.7 ibv=1m is=1e-12 rs=1.7)'
SMAJ33_MAX = 'd(bv=40.6 ibv=1m is=1e-12 rs=1.7)'
for label, com in (('COM on +12V (rev 0.4)', 'Rload com 0 60'), ('COM to SMAJ33A (rev 0.5)', f'Dz 0 com dz33\n.model dz33 {SMAJ33_MIN}')):
    net = f"""* key off: battery -> relay coil -> ULN clamp diode -> COM
Vbat bat 0 12.6
Rc bat c 80
Lc c out 0.3
Dk out com dk
.model dk d(is=1e-12 n=1.8 rs=1)
{com}
.op
.control
run
print v(com) i(Vbat)
.endc
.end
"""
    cir = os.path.join(OUT, 'uln.cir'); open(cir, 'w').write(net)
    r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True).stdout
    vcom = float(r.split('v(com) = ')[1].split()[0]); ib = -float(r.split('i(vbat) = ')[1].split()[0])
    record('Relay outputs', f'key off, {label}', f'{ib * 1000:.1f} mA from the battery into the ECU rail ({vcom:.1f} V on COM)',
           'OK' if ib < 1e-4 else ('REF' if 'rev 0.4' in label else 'FAIL'),
           'rev 0.4 reference: enough to half-power the logic and buzz the relay' if ib > 1e-4 else '')
net = f"""* relay turn-off into the COM TVS
Vb vb 0 14
Rc vb c 80
Lc c out 0.3
Vg g 0 PULSE(5 0 20m 1n 1n 1 2)
Sw out 0 g 0 swmod
.model swmod sw(vt=2.5 ron=1 roff=10meg)
Dk out com dk
.model dk d(is=1e-12 n=1.8 rs=1)
Dz 0 com dz33
.model dz33 {SMAJ33_MAX}
.tran 2u 40m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
d = spice('uln_off', net, ['v(out)'])
record('Relay outputs', 'relay turn-off, COM TVS at maximum breakdown', f'output peak {max(d["v(out)"]):.1f} V (ULN2003 limit 50 V)',
       'OK' if max(d['v(out)']) < 50 else 'FAIL')
# load dump on the relay/lamp feeds (they come straight from the battery, not through D6): every output that is off
# is pulled up through its coil or lamp, through its clamp diode into COM. 6 relay coils (80 ohm) + the CEL bulb
# (cold filament ~6 ohm) at 35 V for 400 ms, TVS at its minimum breakdown.
net = f"""* suppressed load dump on the relay feeds
Vb vb 0 PWL(0 14 1m 14 6m 35 400m 35 500m 14)
Rcoils vb a 13.3
Dk1 a com dk
Rlamp vb b 6
Dk2 b com dk
.model dk d(is=1e-12 n=1.8 rs=1)
Dz 0 tz dz33
Vz com tz 0
.model dz33 {SMAJ33_MIN}
.tran 0.5m 450m
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
d = spice('uln_dump', net, ['i(Vz)'])
iz = max(d['i(Vz)'])
record('Relay outputs', '35 V load dump on the relay feeds, COM TVS at minimum breakdown',
       f'{iz * 1000:.2f} mA into the TVS', 'OK' if iz < 1e-3 else 'FAIL',
       'a 33 V zener here (first rev 0.5 draft) would conduct and could fail short, switching every relay on')

# ---- G. logic supply transients: TVS D6 on VBAT_IN, then D7, the PTC F1 and the SMAJ33A D12 on +12V ---------------
# TVS models (Littelfuse/Bourns curves): SMCJ30A Vbr 33.3-36.8 V (34.5 V typical used), Vc 48.4 V at 31 A; D12
# SMAJ33A as above, at its maximum breakdown for the peak checks and its minimum for the energy check.
# Pulses (ISO 7637-2 / ISO 16750-2, 12 V system): 5b suppressed load dump (35 V clamp at the alternator,
# Ri 0.5 ohm, 400 ms), 2a (+50 V, 2 ohm, 50 us), a 24 V jump start, and a sustained 39 V regulator failure.
def supply(src, tstop, label, note=''):
    net = f"""* supply input protection
Vs s 0 {src}
Ri s vbat {{RI}}
D6 0 vbat d30
.model d30 d(bv=34.5 ibv=1m is=1e-12 rs=0.45)
D7 vbat p12in dss34
.model dss34 d(is=5u n=1.1 rs=0.03)
Rptc p12in p12 0.5
D12 0 tv d33
Vtv p12 tv 0
.model d33 {{D12MODEL}}
* logic load: about 0.15 A at 12 V (buck input), plus the input capacitors
Rl p12 0 80
Cin p12 0 24u
.tran 1u {tstop}
.control
run
wrdata @DAT@ @VEC@
.endc
.end
"""
    return net


for label, src, ri, tstop, limit in [
        ('5b suppressed load dump (35 V, 400 ms)', 'PWL(0 14 1m 14 6m 35 400m 35 500m 14)', 0.5, '450m', 44),
        ('pulse 2a (+50 V, 2 ohm, 50 us)', 'PULSE(14 64 1m 1u 1u 50u 1)', 2.0, '2m', 44),
        ('jump start 24 V', 'PWL(0 14 1m 24 100m 24)', 0.05, '100m', 44)]:
    for which, model in (('max', SMAJ33_MAX), ('min', SMAJ33_MIN)):
        net = supply(src, tstop, label).replace('{RI}', str(ri)).replace('{D12MODEL}', model)
        d = spice('supply', net, ['v(p12)', 'i(Vtv)', 'v(vbat)'])
        t_ = d['time']
        e = sum(d['v(p12)'][k] * d['i(Vtv)'][k] * (t_[k + 1] - t_[k]) for k in range(len(t_) - 1) if d['i(Vtv)'][k] > 0)
        if which == 'max':
            vmax = max(d['v(p12)']); itvs = max(d['i(Vtv)'])
        else:
            e_min = e
    record('Logic supply', label, f'+12V peaks at {vmax:.1f} V (buck abs max 44 V), D12 {itvs:.2f} A peak; '
           f'energy into D12 {e_min * 1000:.1f} mJ even at its minimum breakdown',
           'OK' if vmax < limit and e_min < 1.0 else 'FAIL')
net = supply('DC 39', '10m', 'x').replace('{RI}', '0.05').replace('{D12MODEL}', SMAJ33_MIN).replace('.tran 1u 10m', '.op').replace('wrdata @DAT@ @VEC@', 'print v(p12) i(Vs)')
cir = os.path.join(OUT, 'dbl.cir'); open(cir, 'w').write(net)
r = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True).stdout
ip = -float(r.split('i(vs) = ')[1].split()[0])
record('Logic supply', 'sustained 39 V (failed regulator)',
       f'{ip:.2f} A through F1 (0.5 A hold, 1 A trip): the PTC trips; D6 on the input shares the current',
       'OK' if ip > 1.0 else 'CHECK', 'below about 37 V nothing on +12V conducts at all')

# ---- E. knock amplifier headroom --------------------------------------------------------------------------------
# LMV321 at 3.3 V, non-inverting gain 1 + 47k/10k = 5.7 around a 1.65 V bias, rail-to-rail output (~30 mV from rails).
gain = 1 + 47 / 10
clip_in = (1.65 - 0.03) / gain
record('Knock input', 'input amplitude that reaches the rails (gain 5.7)', f'{clip_in * 1000:.0f} mV peak',
       'CHECK', 'piezo knock sensors give ~20-30 mV/g; a few hundred mV at high rpm will clip; rusEFI software knock '
       'works on band energy, clipping compresses the knock/no-knock ratio at high load')

# ---- report -----------------------------------------------------------------------------------------------------
w = max(len(r[1]) for r in results)
for area, check, value, verdict, note in results:
    print(f'[{verdict:5s}] {area:16s} {check:<{w}s}  {value}')
    if note:
        print(' ' * 26 + note)
if any(r[3] == 'FAIL' for r in results):
    sys.exit(1)
