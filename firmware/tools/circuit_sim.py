#!/usr/bin/env python3
"""Circuit simulations of the daughterboard's input conditioning and output stages with realistic harness signals,
run in ngspice. Component values come from scripts/design.py; sensor and load models are stated where used.

usage: circuit_sim.py [outdir]     (needs ngspice on the PATH)
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
    record('Switch input', label, f'high level {vmax:.2f} V at the MCU (VIH {VIH:.2f} V)', 'OK' if vmax > VIH else 'FAIL')
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
record('Switch input', 'open-collector / ground-switching source', f'high level {vmax:.2f} V: input never goes high',
       'FAIL' if vmax < VIH else 'OK', 'needs a pull-up (to 5 V or 12 V) on the motherboard for such signals')

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


for label, r, l, n_par, events_per_s in [
        ('1 injector, sequential, 7000 rpm', 14, 8e-3, 1, 7000 / 120),
        ('2 injectors on one output (1989-93 batch), 7000 rpm', 7, 4e-3, 2, 7000 / 60)]:
    e, vpk, ipk = clamp_energy(r, l, 14, 6)
    p = e * events_per_s
    record('Low-side output', label, f'{ipk:.1f} A, clamp peak {vpk:.0f} V, {e * 1e3:.1f} mJ per pulse = {p:.2f} W in the clamp',
           'OK' if p < 0.3 else 'CHECK')
for diode in (False, True):
    e, vpk, ipk = clamp_energy(11, 20e-3, 14, 2.5, diode)
    p = e * 200  # idle valve PWM at 200 Hz
    record('Low-side output', f'idle valve 200 Hz PWM, {"with" if diode else "no"} freewheel diode',
           f'clamp peak {vpk:.0f} V, {e * 1e3:.2f} mJ per cycle = {p:.2f} W in the AUIPS2041 clamp',
           'OK' if p < 0.2 else 'FAIL', 'board has no freewheel diode on IACV/VVT/BOOST/ALT' if not diode else '')

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
