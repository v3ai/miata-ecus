"""README for one year's motherboard release, generated from its year module so the pin table
always matches the board.  usage: mb_readme.py <year module> <out README.md>

Year modules may define: HEADER_DESC, CASE_NOTE (provisional outline / where the numbers come
from), CHANGES (list of str), VERIFY (list of str), and comments on their HARNESS lines."""
import sys, re, importlib, inspect, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
M = importlib.import_module(sys.argv[1])
import mb_common as C
M.build_parts()

# pin comments from the module source (and its base modules)
comments = {}
mods = [M] + [importlib.import_module(n) for n in getattr(M, 'BASES', [])]
for mod in reversed(mods):
    for line in inspect.getsource(mod).splitlines():
        for m in re.finditer(r"'(\d[A-Z])':\s*'([^']*)',?\s*(?:#\s*(.*))?$", line.strip()):
            if m.group(3):
                comments[m.group(1)] = m.group(3).strip()
H = M.HARNESS
used = [(p, n) for p, n in H.items() if n]
unused = [p for p, n in H.items() if not n]

ROLE = {'VBAT_IN': 'ECU power (main relay)', 'VIGN_IN': 'ignition switch sense', 'GND': 'ground',
        'V5_SENS': 'sensor 5 V reference (out)', 'HARN_IAT': 'stock air-temp sensor (JP1 on STOCK)'}
for n in ('INJ1', 'INJ2', 'INJ3', 'INJ4'):
    ROLE['OUT_' + n] = f'injector {n[-1]}'
ROLE.update({'OUT_IGN1': 'ignition 1 (5 V logic)', 'OUT_IGN2': 'ignition 2 (5 V logic)', 'OUT_IACV': 'idle air valve',
             'OUT_FP': 'fuel pump relay', 'OUT_CEL': 'check engine lamp', 'OUT_TACH': 'tach out', 'OUT_AC': 'A/C relay',
             'OUT_FAN': 'fan relay', 'OUT_LS7': 'spare low side', 'OUT_VVT': 'PWM low side (VVT driver)',
             'OUT_ALT': 'PWM low side (alternator driver)', 'OUT_BOOST': 'PWM low side (boost driver)',
             'OUT_MAINRLY': 'main relay control', 'IN_TPS': 'TPS', 'IN_CLT': 'coolant temp',
             'IN_AUX1': 'spare analog 1', 'IN_AUX2': 'spare analog 2', 'IN_AUX3': 'spare analog 3',
             'IN_SW1': '12 V switch input 1', 'IN_SW2': '12 V switch input 2', 'IN_SW3': '12 V switch input 3',
             'IN_HALL1': 'hall input 1 (crank)', 'IN_HALL2': 'hall input 2 (cam)',
             'HARN_CRANK': 'crank sensor (hall/VR select)', 'HARN_CRANK_RTN': 'crank sensor return (VR)',
             'HARN_CAM': 'cam sensor (hall/VR select)', 'HARN_CAM_RTN': 'cam sensor return (VR)'})

W, Hh = M.W, M.H
holes = M.CASE_HOLES
o = []
o.append(f'# {M.TITLE}, rev {os.environ.get("MBREV", "0.3")}\n')
o.append('The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:\n')
o.append('- the stock harness header;')
o.append('- the year-independent I/O: the LSU 4.9 wideband sensor connector, IAT, USB-C and the MAP sensor;')
o.append('- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).\n')
if getattr(M, 'CHANGES', None):
    o.append('## Changes in this revision')
    o += [f'- {c}' for c in M.CHANGES]
    o.append('')
P = M.NAME
o.append('## Files')
o.append('| Path | What |\n|---|---|')
o.append(f'| `{P}.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |')
o.append(f'| `{P}_schematic.pdf` | Schematic PDF |')
o.append('| `fab/jlcpcb_gerbers.zip`, `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm) |')
o.append('| `fab/parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |')
o.append('| `fab/drc_report.txt` | KiCad DRC |')
o.append('| `ecu_mb.pretty/`, `fp-lib-table` | Project footprints (harness header, MAP sensor lying flat, USB-C, M4 case hole) |')
o.append('| `renders/` | Top and bottom copper |')
o.append('| `scripts/` | The design source; `mb_make.sh` rebuilds the whole board |\n')
o.append('## Case fit')
o.append(getattr(M, 'CASE_NOTE', '') + '\n')
o.append(f'Board: **{W:.1f} × {Hh:.1f} mm**, 1.6 mm. The origin is the top-left corner and y points down, toward the bottom edge.\n')
o.append('| Hole | x, y (mm) |\n|---|---|')
o += [f'| {k} | {x:.1f}, {y:.1f} |' for k, (x, y) in holes.items()]
o.append(f'\nAll holes are 4.5 mm plated with a 7 mm pad, tied to GND, for M4 screws. '
         f'Harness header terminal 1A sits at ({M.HDR_1A[0]:.2f}, {M.HDR_1A[1]:.2f}) mm (lower pin row).\n')
o.append('## Harness header')
o.append(getattr(M, 'HEADER_DESC', '') + '\n')
o.append('| Pin | Net | Use | Stock function / note |\n|---|---|---|---|')
for p, n in sorted(used, key=lambda t: (t[0][0], t[0][1])):
    o.append(f'| {p} | `{n}` | {ROLE.get(n, "")} | {comments.get(p, "")} |')
o.append(f'\nNot connected: {", ".join(sorted(unused))}.\n')
o.append('## Bottom edge, left to right')
o.append('| Ref | What | Notes |\n|---|---|---|')
o.append('| J2 | LSU 4.9 (Molex Micro-Fit 2×3, right angle) | Pin n = LSU pin n: 1 IP, 2 VM, 3 H−, 4 H+, 5 RT, 6 UN. Heater fed from the main relay through F1 (2 A hold, 30 V). The controller is on the daughterboard |')
o.append('| J3 | IAT (Micro-Fit 1×2) | M12×1.5 open-element thermistor, used when the IAT jumper JP1 is on EXT |')
o.append('| JP1 | IAT source jumper (1×3, 2.54 mm) | Shunt on **2-3 (EXT, default)**: the IAT connector J3. Shunt on **1-2 (STOCK)**: the stock air-temp sensor through the harness (inside the AFM on 1989-97, the MAF on 1999-2005). Set the matching sensor curve in TunerStudio; the pull-up is 2.7 kΩ |')
o.append('| J4 | USB-C | USB 2.0 device: tuning, logging, DFU |')
o.append('| U2 | MPX5700AP | Absolute MAP sensor (15-700 kPa, case 867B). Lies flat on 2 × M3, marking side up, leads bent 90° down, the single barb toward the board centre |\n')
o.append('**CAN:** R1 + R6 terminate the bus at the ECU end; remove R6 if the bus is terminated elsewhere.\n')
o.append('**AUX (J5, 2×8 box header):** what the stock harness has no pins for: COP 3/4, boost, alternator and main-relay outputs, '
         'knock input, VR crank/cam inputs, external AFR input, UART, 5 V sensor supply, +12 V and GND.\n')
if any(p['ref'] in ('R7', 'R10') for p in C.parts):
    o.append('**Crank / cam sensor type:** each trigger has three 0R links. Fit the hall link for a hall / open-collector sensor, '
             'or the two VR links for a 2-wire magnetic sensor. The default for this car is assembled; see the parts list.\n')
o.append('**Protection (motherboard rev 0.4 / 0.6):** D1 (and D2 where the VVT driver runs a coil) freewheel the PWM '
         'valve coils into their own +12 V feed, so the drivers don\'t absorb the turn-off energy. F4 fuses the AUX +12 V '
         'pin (0.5 A hold).\n')
o.append('**Switch inputs (R20-R22, not fitted):** the VSS, A/C and clutch inputs read signals that are driven to 12 V. If '
         'your car\'s signal only switches to ground (or is open collector), fit the 4.7 kΩ pull-up for that input. Never fit '
         'it for a switch that drives 12 V: the input would always read on.\n')
if any(p['ref'] == 'R23' for p in C.parts):
    o.append('**Injectors (1989-93):** the stock harness has two injectors on each of 2U and 2V (about 1.8 A per wire). '
             'Two daughterboard drivers share each wire through R23 (INJ1 + INJ4 on 2U) and R24 (INJ2 + INJ3 on 2V); '
             'rusEFI\'s batch mode fires each pair together. D3/D4 clamp each wire at about 45-50 V, so the drivers\' '
             'own clamps never take the turn-off energy. For a sequential conversion (new wires to 2Y/2Z), remove R23/R24, '
             'fit R25/R26 and switch the firmware to sequential. **Never fit R26 on an automatic: 2Z goes to the A/T '
             'control unit.**\n')
o.append('## Assembly')
o.append('- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.')
o.append('- Fitted by hand: the harness header (salvage from a stock ECU or use a clone), the IAT jumper shunt on JP1 (LCSC C5305; EXT or STOCK), and any not-fitted option links.')
o.append('- The case needs cut-outs in its bottom edge for the LSU, IAT, USB-C and MAP hose.\n')
o.append('## Still to verify')
o += [f'- {v}' for v in getattr(M, 'VERIFY', ['The case geometry, against a stock case with calipers.'])]
open(sys.argv[2], 'w').write('\n'.join(o) + '\n')
print('wrote', sys.argv[2], len(used), 'pins used')
