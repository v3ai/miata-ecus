#!/usr/bin/env python3
"""End-to-end check: rusEFI function -> STM32 pin -> daughterboard driver/input -> J1/J2 -> motherboard -> harness
cavity, for every model year, compared with the cavity that independent references say carries that function.

Input: the output of the board's simulation tests (firmware/board/tests/test_miata_ecu.cpp), i.e. the "MIATA|"
lines rusEFI's unit-test binary prints. The firmware side comes from the tune the real board code builds; the
hardware side comes from scripts/design.py and scripts/mb_*.py.

usage: sim_report.py <test output file>
"""
import importlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
cwd = os.getcwd()
os.chdir(os.path.join(ROOT, 'scripts'))
import design  # noqa: E402
MB = {y: importlib.import_module(m).HARNESS for y, m in
      [('1989-93', 'mb_na6'), ('1994-95', 'mb_na8'), ('1996-97', 'mb_na96'), ('1999-2000', 'mb_nb1'), ('2001-02', 'mb_nb2'),
       ('2003-05', 'mb_nb2')]}
os.chdir(cwd)

PINS = {int(n): name for n, name in (l.split(':') for l in open(os.path.join(ROOT, 'scripts', 'stm32f407v_lqfp100_pins.txt')).read().split())}
PORT_NET = {PINS[int(p)]: net for p, net in design.mcu.items()}

# Harness cavity for each function, from sources independent of this design:
#  - 1990/1994: rusEFI wiki "Mazda-Miata-1990" / "Mazda-Miata-1994" pinout tables and the Hellen NA6 board nets.
#    The 26-pin plug is called 3x on the 1990 page and 2x on the 1994 page; our boards use 2x.
#  - 1996-2005: rusEFI Hellen NA96 / NB1 / NB2 board connector yaml and PCB nets (Hellen NA96 numbers OEM plug 3
#    as 2 and plug 4 as 3), plus research/pinouts_9605.md (2005 FSM for NB2).
# A function missing from a year's dict must not be wired to the harness at all for that year.
# ignKey is the ignition-switch sense input: rusEFI cuts fuel and spark while it reads "off", so it must be configured
# exactly on the years whose harness has the wire (1C on 1989-95, 4S on 2003-05) and nowhere else.
EXPECTED = {
    '1989-93': {'ign1&4': '1G', 'ign2&3': '1H', 'inj1': '2U', 'inj2': '2V', 'fuelPump': '2T', 'fan': '1L',
                'fan2': '1R', 'acRelay': '1J', 'cel': '1E', 'tach': '2I', 'idle': '2W', 'vss': '1M',
                'acSwitch': '1Q', 'clutch': '1V', 'crank(SGT)': '2E', 'cam(SGC)': '2G', 'ignKey': '1C'},
    '1994-95': {'ign1&4': '1G', 'ign2&3': '1H', 'inj1': '2U', 'inj2': '2V', 'inj3': '2Y', 'inj4': '2Z',
                'fuelPump': '2T', 'fan': '1L', 'fan2': '2S', 'acRelay': '1J', 'cel': '1E', 'tach': '2I',
                'idle': '2W', 'vss': '1M', 'acSwitch': '1Q', 'clutch': '1V', 'crank(SGT)': '2E', 'cam(SGC)': '2G',
                'ignKey': '1C'},
    '1996-97': {'ign1&4': '4N', 'ign2&3': '4R', 'inj1': '4U', 'inj2': '4V', 'inj3': '4W', 'inj4': '4X',
                'fuelPump': '1U', 'fan': '1A', 'fan2': '1B', 'acRelay': '1G', 'cel': '1E', 'tach': '4L',
                'idle': '4Q', 'vss': '1M', 'acSwitch': '1K', 'clutch': '1L', 'crank(SGT)': '4F', 'cam(SGC)': '4G',
                'o2heater': '3M'},
    '1999-2000': {'ign1&4': '3G', 'ign2&3': '3H', 'inj1': '3W', 'inj2': '3X', 'inj3': '3Y', 'inj4': '3Z',
                  'fuelPump': '3N', 'fan': '1R', 'fan2': '1I', 'acRelay': '1S', 'cel': '1E', 'tach': '2K',
                  'idle': '3M', 'vss': '2D', 'acSwitch': '1P', 'clutch': '3I', 'crank': '2J', 'cam': '2H',
                  'o2heater': '1U', 'alternator': '1O'},
    # 2001-02: the car's own main relay powers the ECU and there is no ignition-sense wire (4S, 3H unused)
    '2001-02': {'ign1&4': '3F', 'ign2&3': '3I', 'inj1': '2A', 'inj2': '2D', 'inj3': '2G', 'inj4': '2J',
                'fuelPump': '2M', 'fan': '2B', 'fan2': '2C', 'acRelay': '2K', 'cel': '2R', 'tach': '3O',
                'idle': '2Q', 'vss': '3T', 'acSwitch': '4F', 'clutch': '4I', 'crank': '3Y', 'cam': '3V',
                'vvt': '4R', 'alternator': '3M'},
}
EXPECTED['2003-05'] = dict(EXPECTED['2001-02'], mainRelay='3H', ignKey='4S')


def ign_sense_cavity(year):
    """rusEFI's ignKeyAdcChannel (PA2) -> AN_VIGN divider -> VIGN_IN -> harness cavity."""
    if PORT_NET.get('PA2') != 'AN_VIGN' or 3 not in design.J1 or design.J1[3] != 'VIGN_IN':
        return 'PA2 is not the ignition-sense divider'
    hits = [k for k, v in MB[year].items() if v == 'VIGN_IN']
    return hits[0] if len(hits) == 1 else (hits or None)


def harness_pin(year, port):
    """STM32 port -> harness cavity on that year's motherboard (None if not on the harness)."""
    net = PORT_NET.get(port)
    if net is None:
        return None
    if net.endswith('_CTL'):
        header = 'OUT_' + net[:-4]
    elif net in ('HALL1', 'HALL2', 'SW1', 'SW2', 'SW3'):
        header = 'IN_' + net
    else:
        header = net
    hits = [k for k, v in MB[year].items() if v == header]
    return hits[0] if len(hits) == 1 else (hits or None)


def main(path):
    configs = {}
    for line in open(path):
        if line.startswith('MIATA|') and '|config|' in line:
            parts = line.strip().split('|')
            year = parts[1]
            kv = dict(p.split('=', 1) for p in parts[5:] if '=' in p)
            configs[year] = kv
    errors, rows = [], []
    for year, kv in configs.items():
        ign = kv['ign'].split(',')
        inj = kv['inj'].split(',')
        trig = kv['trigger'].split(',')
        fw = {'ign1&4': ign[0], 'ign2&3': ign[2], 'inj1': inj[0], 'inj2': inj[1], 'inj3': inj[2], 'inj4': inj[3]}
        if trig[1] != '-':      # NA: primary SGC on trigger 1, secondary SGT on trigger 2
            fw['cam(SGC)'], fw['crank(SGT)'] = trig[0], trig[1]
        else:                   # NB: crank on trigger 1, cam on the VVT input
            fw['crank'], fw['cam'] = trig[0], kv['cam']
        for k in ('fuelPump', 'fan', 'fan2', 'acRelay', 'cel', 'tach', 'idle', 'mainRelay', 'alternator',
                  'o2heater', 'vvt', 'vss', 'acSwitch', 'clutch'):
            fw[k] = kv[k]
        fw['ignKey'] = 'PA2' if kv['ignKey'] == 'VIGN' else '-'
        exp = EXPECTED[year]
        for func, port in fw.items():
            if port == '-':
                if func in exp:
                    errors.append(f'{year}: {func} is not assigned in the firmware but the harness has it on {exp[func]}')
                continue
            if func == 'ignKey' and func not in exp:
                errors.append(f'{year}: ignition sense is configured but this harness has no ignition-sense wire, '
                              'so rusEFI would read the key as off and cut fuel and spark')
                continue
            got = ign_sense_cavity(year) if func == 'ignKey' else harness_pin(year, port)
            want = exp.get(func)
            ok = got == want
            if not ok:
                errors.append(f'{year}: {func} -> {port} -> harness {got}, expected {want}')
            rows.append((year, func, port, got, want, 'ok' if ok else 'MISMATCH'))
        # the other direction: every function the harness has must be driven by the firmware
        for func in exp:
            if fw.get(func, '-') == '-':
                errors.append(f'{year}: harness function {func} ({exp[func]}) has no firmware output/input')
    for r in rows:
        print('%-10s %-12s %-5s harness %-5s expected %-5s %s' % r)
    print()
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    print(f'end-to-end OK: {len(rows)} firmware functions across {len(configs)} years land on the expected harness cavities')


if __name__ == '__main__':
    main(sys.argv[1])
