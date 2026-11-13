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

ROLE = {'VBAT_IN': 'ECU power (main relay)', 'VIGN_IN': 'switched 12 V sense (wakes the logic supply)', 'GND': 'ground',
        'V5_SENS': 'sensor 5 V reference (out)', 'V5_EXT': 'sensor 5 V reference (out; protected, short-to-battery proof)', 'IN_IAT': 'air temperature (stock sensor)'}
ROLE.update({'HARN_1N': 'option links R28', 'HARN_2L': 'option links R29 / R30', 'HARN_1R': 'jumper JP3', 'HARN_2S': 'jumper JP3',
             'HARN_2I': 'jumper JP5', 'HARN_2O': 'jumper JP6', 'HARN_2R': 'jumper JP4', 'HARN_2Y': 'jumper JP1', 'HARN_2Z': 'jumper JP2'})
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
o.append('- the year-independent I/O: the wideband sensor connector (AEM X-Series harness), USB-C, the MAP sensor and the add-on header (flex fuel, nitrous, CAN, boost);')
o.append('- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).\n')
if getattr(M, 'CHANGES', None):
    o.append('## Changes in this revision')
    o += [f'- {c}' for c in M.CHANGES]
    o.append('')
P = M.NAME
F = 'fab/' + C.fab_prefix(sys.argv[1], os.environ.get('MBREV', '0.0'))     # fab file names carry year and rev
o.append('## Files')
o.append('| Path | What |\n|---|---|')
o.append(f'| `{P}.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |')
o.append(f'| `{P}_schematic.pdf` | Schematic PDF |')
o.append(f'| `{F}jlcpcb_gerbers.zip`, `{F}jlcpcb_bom.csv`, `{F}jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm). The JLC BOM is the SMD parts and USB-C only |')
o.append(f'| `{F}self_order_bom.csv` | Everything you order and fit yourself: harness header, through-hole connectors, MAP sensor, shunt, standoffs and screws, plus the not-fitted options. Its columns load into LCSC\'s BOM tool |')
o.append(f'| `{F}parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |')
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
o.append('| J2 | Wideband sensor (Molex Micro-Fit 3.0, 2×4, right angle) | For the **AEM X-Series sensor harness 30-3427** and a Bosch LSU 4.9. Pin 1 trim (LSU RT), 2 heater −, 3 common (VM), 5 pump current (IP), 6 sense (UN), 8 heater +; 4 and 7 empty. The pin functions are from AEM\'s manual; **that the harness plug is a Micro-Fit 2×4 is an assumption: check it against the harness before ordering.** Heater fed from the main relay through F1 (3 A hold, 30 V, 2920). The controller is on the daughterboard |')
o.append('| J4 | USB-C | USB 2.0 device: tuning, logging, DFU |')
o.append('| U2 | MPX5700AP | Absolute MAP sensor (15-700 kPa, case 867B). Lies flat on 2 × M3, marking side up, leads bent 90° down, the single barb toward the board centre |\n')
o.append('**Air temperature:** the stock sensor\'s harness wire goes straight to the air temperature input (inside the airflow meter on '
         '1989-97, in the air filter box on 1999-2005). The separate IAT connector and its jumper are gone. The pull-up is 2.7 kΩ.\n')
o.append('**CAN:** R1 + R6 terminate the bus at the ECU end; remove R6 if the bus is terminated elsewhere. The bus is on the add-on header '
         '(J5-19 CAN H, J5-20 CAN L) for a dash or gauges; it is the bus the on-board wideband controller reports on, at 500 kbit/s.\n')
AUXROLE = {'OUT_IGN3': 'ignition 3 (5 V logic), coil-on-plug', 'OUT_IGN4': 'ignition 4 (5 V logic), coil-on-plug',
           'OUT_BOOST': 'boost valve, low side (freewheel diode D5 to pin 15 on the board)', 'OUT_ALT': 'alternator driver, low side',
           'OUT_MAINRLY': 'main relay driver, low side', 'IN_KNOCK': 'knock sensor', 'VR1_P': 'VR input 1 +', 'VR1_N': 'VR input 1 −',
           'VR2_P': 'VR input 2 +', 'VR2_N': 'VR input 2 −', 'IN_AFR': 'external 0-5 V wideband',
           'IN_FLEX': 'flex-fuel sensor signal (4.7 kΩ pull-up to 5 V on the board, R35)',
           'IN_N2O': 'nitrous arming switch: 12 V = armed (10 kΩ pull-down on the board, R36)',
           'V5_EXT': 'sensor 5 V (protected)', 'AUX_VBAT': '+12 V from the main relay through F4 (1.1 A hold)', 'GND': 'ground',
           'CAN_H': 'CAN high', 'CAN_L': 'CAN low'}
o.append('**Add-on header (J5, 2×10 box header, 2.54 mm; a 20-way ribbon cable fits):** what the stock harness has no pins for.\n')
o.append('| Pin | Net | Use |\n|---|---|---|')
o += [f'| {k} | `{C.AUX[k]}` | {AUXROLE.get(C.AUX[k], "")} |' for k in sorted(C.AUX)]
o.append('\n**Flex fuel** (GM / Continental type sensor): signal to J5-12, sensor +12 V from J5-15, ground to J5-16. In TunerStudio set the '
         'flex sensor input to "Flex input (J2-24)". **Nitrous:** arming switch from +12 V to J5-13; in TunerStudio enable nitrous control, '
         'set the trigger to "Nitrous arm (J2-25)" and pick a spare output (boost on J5-3, or the second fan output) for the solenoid relay. '
         '**Boost valve:** between J5-15 (+12 V) and J5-3. All of these need a rev 0.10 daughterboard.\n')
if any(p['ref'] in ('R7', 'R10') for p in C.parts):
    o.append('**Crank / cam sensor type:** each trigger has three 0R links. Fit the hall link for a hall / open-collector sensor, '
             'or the two VR links for a 2-wire magnetic sensor. The default for this car is assembled; see the parts list.\n')
if getattr(M, 'JUMPERS', None):
    o.append('**Jumpers (2.54 mm headers with shunts, in the margins beside the daughterboard):** this one board covers 1989-93 and 1994-95; '
             'the pins that differ are on jumpers. Set them for the car before the first start.\n')
    o.append('| Jumper | Marked | 1989-93 | 1994-95 | What it does |\n|---|---|---|---|---|')
    for ref, n, pads, name, labels, desc in M.JUMPERS:
        def pos(year):
            sh = M.SHUNTS[year].get(ref)
            if sh is None:
                return 'open'
            if n == 2:
                return 'fitted'
            return labels.get(sh[0] if sh[0] != 2 else sh[1], f'{sh[0]}-{sh[1]}')
        o.append(f'| {ref} | {name} | {pos("1989-93")} | {pos("1994-95")} | {desc} |')
    o.append('')
o.append('**Protection:** D1 (and D2 where the VVT driver runs a coil) freewheel the PWM valve coils into their own +12 V feed, '
         'and D5 does the same for a boost valve on the add-on header, so the drivers don\'t absorb the turn-off energy. F4 fuses the '
         'add-on header\'s +12 V pin (1.1 A hold: a boost valve draws about 0.5 A).\n')
o.append('**Switch inputs (R20-R22, not fitted):** the VSS, A/C and clutch inputs read signals that are driven to 12 V. If '
         'your car\'s signal only switches to ground (or is open collector), fit the 4.7 kΩ pull-up for that input. Never fit '
         'it for a switch that drives 12 V: the input would always read on.\n')
if any(p['ref'] == 'R28' for p in C.parts):
    o.append('**Throttle position sensor (manual cars):** the 1989-93 manual cars have no throttle position sensor, only '
             'a two-contact switch. The ECU calculates fuel from the MAP sensor, so the car runs without one, but rusEFI '
             'then flags the throttle sensor as failed and drops closed-loop idle, throttle-based acceleration fuel and '
             'overrun fuel cut. A 0-5 V sensor fits on the stock wiring, as on rusEFI\'s Hellen NA6 and MRE boards: the '
             'switch plug has three wires, the idle contact (1N), ground (2D) and the full-throttle contact (2L), and a '
             'sensor needs 5 V, ground and a signal. **Board links:** fit R28 (0R 0805) to put the protected 5 V on 1N, '
             'and move the 0R from R29 to R30 so that 2L goes to the TPS input instead of AUX1. Until R28 is fitted, 1N '
             'is open: with the stock switch fitted, 5 V on 1N would be shorted to ground at every idle. '
             '**Sensor:** a Kia sensor with the same 3-pin Mazda plug (0K01118911 and the others in the self-order BOM) '
             'plugs into the stock plug, on a printed mount (Thingiverse 3414132, print in ASA); or Flyin\' Miata\'s TPS '
             'upgrade kit. **Before fitting R28,** unplug the switch and check on your car which plug wire reaches 1N, '
             '2L and 2D, and on the sensor which pins are the ends of its track (constant resistance between them at any '
             'throttle): those must meet 1N and 2D, and the third (the wiper) 2L. In TunerStudio, calibrate the throttle '
             'closed and wide open (a reversed sensor calibrates the same way). **Automatics** already have a sensor on 2M '
             '(with its 5 V on 2K): leave R28 and R30 off. Every part is in the self-order BOM.\n')
if any(p['ref'] == 'R27' for p in C.parts):
    o.append('**Throttle switch contact (R27, not fitted):** on the manual cars 2L is one of the throttle switch\'s '
             'contacts, which closes to ground. Fit the 4.7 kΩ pull-up to the protected 5 V only if you keep the stock '
             'switch and want the ECU to read it (on AUX1, through R29); never with a sensor on 2L.\n')
o.append('**Sensor 5 V:** the harness\'s 5 V reference and the AUX header pin J5-14 come from the daughterboard\'s '
         'protected 5 V regulator (V5_EXT; it survives a short to the battery or to ground). The MAP sensor has its own '
         'supply (V5_SENS), so a damaged sensor wire doesn\'t take the MAP reading with it.\n')
if getattr(M, 'JUMPERS', None):
    o.append('**Injectors (1989-93):** the stock harness has two injectors on each of 2U and 2V (about 1.8 A per wire). With JP1 and JP2 '
             'on PAIR two daughterboard drivers share each wire (INJ1 + INJ4 on 2U, INJ2 + INJ3 on 2V) and rusEFI\'s batch mode fires each '
             'pair together. A rev 0.10 daughterboard clamps each driver itself, so D3/D4 are not fitted; **fit them (SMCJ30A) only to run '
             'this board with a rev 0.9 daughterboard on a 1989-93 car.** For a sequential conversion (new wires to 2Y/2Z) move JP1 and JP2 '
             'to SEQ and switch the firmware to sequential. **Never put JP2 on SEQ on a 1989-93 automatic: 2Z goes to the A/T control unit.**\n')
    o.append('**Tachometer (1989-95):** cavity 2I is the igniter\'s signal into the ECU; the igniter drives the tachometer itself. JP5 '
             'is left open and the firmware has no tach output on these years. Only after a coil-on-plug conversion with the igniter '
             'removed: fit JP5, set the tach output in TunerStudio, and join the two tach wires at the old igniter plug (R37 is the 12 V '
             'pull-up the tachometer then needs).\n')
TPSJ = ''
o.append('## Assembly')
o.append('- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.')
o.append(f'- Fitted by hand (all in `{F}self_order_bom.csv`): the harness header (salvage from a stock ECU or use a clone), the daughterboard sockets JD1/JD2, the wideband sensor connector{TPSJ}, the add-on header, any jumper headers and their shunts, the MAP sensor, the standoffs, and any not-fitted option links. JLCPCB fits only the SMD parts and USB-C. USB-C has through-hole shell pegs: check in JLC\'s quote whether that needs Standard PCBA.')
o.append('- The case needs cut-outs in its bottom edge for the wideband connector, USB-C and the MAP hose, and a way out for the add-on ribbon cable.\n')
o.append('## Still to verify')
o += [f'- {v}' for v in getattr(M, 'VERIFY', ['The case geometry, against a stock case with calipers.'])]
open(sys.argv[2], 'w').write('\n'.join(o) + '\n')
print('wrote', sys.argv[2], len(used), 'pins used')
