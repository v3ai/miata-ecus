#!/usr/bin/python3
"""Board-level checks for every model year: complete connectivity (both directions, from the routed copper),
electrical compatibility at each MCU pin, and DC fault analysis of every harness pin.

  1. Connectivity. The routed .kicad_pcb files are the truth for copper: board_copper.py rebuilds each board's
     netlist from the copper geometry alone (pads, tracks, vias, zone fills) and compares it with the design scripts.
     Then, per year: every harness cavity -> motherboard net -> JD1/JD2 pin -> daughter J1/J2 net -> daughter circuit
     -> STM32F407 / STM32F103 pin (or rail, or nothing), and every MCU pin the firmware uses (the board code's own
     configuration, evaluated from miata_board.cpp) -> harness cavity. Flags: car-driven cavities that land nowhere,
     functions that don't reach the expected cavity (sim_report.py's reference table), two drivers on one net,
     ECU outputs on do-not-drive cavities, unconnected IC pins that a datasheet says must be tied.
  2. Electrical compatibility: the DC voltage each MCU pin sees over the normal range of its harness signal, against
     the pin's structure (FT / TTa / F103 non-FT), plus output -> input levels and pull-up rails.
  3. Faults: each harness cavity, every year, shorted to ground, to 14.4 V, to 24 V (jump start, whole car at 24 V)
     and open, solved as a DC network (resistors from the design, diodes and TVSs as piecewise-linear diodes, IC pins
     as the models listed in MODEL NOTES below). Reports MCU pin voltage and injected current, resistor dissipation
     against package rating, fuse trips, IC stress, rail back-feed, and which other functions move.
  4. Header/socket mating: re-checked from the PCBs (all 80 pads, position by pure translation, and net).

Prints [OK] / [CHECK] / [FAIL] rows and a summary; exits 1 on any FAIL.

usage: /usr/bin/python3 firmware/tools/board_checks.py [--brief] [--year 1999-2000] [--sim-log test_output.txt]
   --brief      print only CHECK / FAIL rows (plus the summary)
   --sim-log    take the firmware pin assignment from the board tests' "MIATA|...|config|" dump (see sim_report.py)
                instead of evaluating miata_board.cpp

Datasheet limits used (STM32F407 DS8626, STM32F103x8 DS5319; F4 family IINJ table re-confirmed in the STM32F412
datasheet, same structure):
  FT pins: VIN abs max VDD + 4.0 V; injected current -5 / +0 mA (no positive injection possible: there is no clamp
  to VDD, so the limit above VDD is the voltage, not a current). TTa (PA4/PA5) and F103 non-FT pins: VIN abs max
  4.0 V, injected current +-5 mA (diodes to VDDA / VDD). Total injected current +-25 mA. Operating range on FT pins
  -0.3..5.5 V. An FT pin used as an ADC input is treated as good to VDDA only (outside it the reading clips; tolerance
  above VDDA in analog mode is not relied on: CHECK).

MODEL NOTES (DC, steady state; assumptions, not measurements)
  Rails: +5V and WB_VDDA are held (stiff); current they would have to sink is reported against their minimum load
  (+5V 60 mA). +3V3: the LDO only sources, into a 50 mA minimum load (66 ohm); current pushed in beyond that lifts the
  rail to the U15 TL431 / Q20 BCP53 shunt clamp (threshold from R142/R143, 3.56 V; 0.04 ohm), which is reported by
  its current and Q20 dissipation (1 W assumed for SOT-223; CHECK above that, or above 1 A). The two TLS115 trackers
  only source (151 mA minimum current limit, output rated -5..45 V, short-to-battery protected), so back-feed lifts
  them: V5_SENS (U3) feeds only the on-board MAP sensor (7 mA); V5_EXT (U14) is the harness sensor 5 V (5 k per
  harness 5 V cavity, the CLT/IAT bias network, and the hall pull-ups through the BAT54A D35, whose cathodes V5_H1 /
  V5_H2 block a crank / cam wire shorted to battery).
  Diodes: piecewise linear, Vf / Ron / breakdown from the part (TVS at minimum breakdown). MCU pins: FT = diode to
  GND only; TTa / F103 non-FT = diodes to GND and VDD(A). TC4427 = 7 ohm to +5V / GND plus body diodes, then 100 ohm
  and a B5819W series Schottky to OUT_IGNx (a wire shorted to battery reverse-biases it); the ignition pull-downs
  Q16-Q19 are on whenever the TC4427 output is low (74HCT04 inverter). Low-side switches: on-resistance, body diode
  and drain clamp (at its minimum): VND7NV04 (Q1-Q8) 0.12 ohm (150 C max), 40 V, current limit 6 A min; ZXMS6004
  (Q9-Q19) 0.5 ohm, 60 V, 1 A min; VND14NV04 0.035 ohm, 40 V; NCV8406A 0.21 ohm, 60 V, 2.5 A. Current above the limit
  is reported as the switch's own current limit / thermal shutdown (OK for the DPAK OMNIFETs, CHECK for the SOT-23
  ZXMS6004, which cycles in thermal shutdown). ULN2003 (rev 0.7 only) = 0.9 V + 1 ohm, no current limit. Op-amp
  outputs = 72 ohm from mid-rail (23 mA short-circuit) plus rail diodes; op-amp inputs = rail diodes (MCP6004 2 mA
  abs max, AD8628 5 mA assumed, LMV321 10 mA). TCAN1042 bus pins: +-58 V, not loaded; RXD = 100 ohm to VIO. PTCs that
  carry more than their trip current (F1 nSMD050, F2 nSMD010 on the LSU VM wire, motherboard F1-F4) are opened and the
  network solved again.
  Car side (typical, assumed): relay coils 80 ohm, CEL 50 ohm, tach 1 k, VICS 30 ohm to battery; injectors 13 ohm
  (6.5 on 1989-93 paired wires); idle valve 11 ohm to its feed; purge / PRC 30 ohm; O2 heater 6 ohm; OCV 8 ohm; NB
  field 4 ohm; igniter input 2 k to ground; TPS 2.5 V / 1.25 k; MAF 2.5 V / 1 k; O2 0.45 V / 10 k; thermistors
  2.5 k (and open, for the cold / unplugged case on sensor-5 V faults); hall and switch inputs open. The battery is
  14.4 V; the 24 V cases put the whole car at 24 V (jump start) and report only what the short adds to that.
  Resistor ratings: 0402 62.5 mW, 0603 100 mW, 0805 125 mW, 1206 250 mW (generic thick film, 70 C).
  Not modelled: transients (except the knock-input note), thermal time constants, reverse battery, LSU cell
  impedances (the sensor is treated as open).
"""
import argparse
import collections
import importlib
import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'scripts')
TOOLS = os.path.join(ROOT, 'firmware', 'tools')
BOARD = os.path.join(ROOT, 'firmware', 'board')
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, TOOLS)

_cwd = os.getcwd()
os.chdir(SCRIPTS)
import design  # noqa: E402
import sim_report  # noqa: E402  (its EXPECTED cavity table is the independent reference)
os.chdir(_cwd)

YEARS = [  # (year, motherboard module, routed pcb, engine type, nb2Early)
    ('1989-93', 'mb_na6', 'motherboards/1989-93/miata_mb_8993.kicad_pcb', 'MAZDA_MIATA_NA6', False),
    ('1994-95', 'mb_na8', 'motherboards/1994-95/miata_mb_9495.kicad_pcb', 'MAZDA_MIATA_NA94', False),
    ('1996-97', 'mb_na96', 'motherboards/1996-97/miata_mb_9697.kicad_pcb', 'MAZDA_MIATA_NA96', False),
    ('1999-2000', 'mb_nb1', 'motherboards/1999-2000/miata_mb_9900.kicad_pcb', 'MAZDA_MIATA_NB1', False),
    ('2001-02', 'mb_nb2', 'motherboards/2001-05/miata_mb_0105.kicad_pcb', 'MAZDA_MIATA_NB2', True),
    ('2003-05', 'mb_nb2', 'motherboards/2001-05/miata_mb_0105.kicad_pcb', 'MAZDA_MIATA_NB2', False),
]
RESEARCH_YEAR = {'1996-97': '1996-1997', '1999-2000': '1999-2000', '2001-02': '2001-2005', '2003-05': '2001-2005'}
DAUGHTER_PCB = 'daughterboard/miata_ecu_daughter.kicad_pcb'

# ------------------------------------------------------------------------------------------------------------------
# report
# ------------------------------------------------------------------------------------------------------------------
ROWS = []
SEV = {'OK': 0, 'CHECK': 1, 'FAIL': 2}


def row(status, section, year, text):
    ROWS.append((status, section, year, text))


# ------------------------------------------------------------------------------------------------------------------
# MCU pin facts
# ------------------------------------------------------------------------------------------------------------------
F407_NAME = {int(n): name for n, name in
             (s.split(':') for s in open(os.path.join(SCRIPTS, 'stm32f407v_lqfp100_pins.txt')).read().split())}
F407_PIN = {v: k for k, v in F407_NAME.items()}
# DS8626 pin definitions, LQFP100: every GPIO is FT except PA4/PA5 (TTa, DAC outputs); PC13-15 are FT but sit in the
# backup domain (2 MHz, 3 mA total sink/source through the power switch).
F407_TTA = {'PA4', 'PA5'}
F103_NAME = {1: 'VBAT', 2: 'PC13', 3: 'PC14', 4: 'PC15', 5: 'PD0', 6: 'PD1', 7: 'NRST', 8: 'VSSA', 9: 'VDDA',
             10: 'PA0', 11: 'PA1', 12: 'PA2', 13: 'PA3', 14: 'PA4', 15: 'PA5', 16: 'PA6', 17: 'PA7', 18: 'PB0',
             19: 'PB1', 20: 'PB2', 21: 'PB10', 22: 'PB11', 23: 'VSS', 24: 'VDD', 25: 'PB12', 26: 'PB13', 27: 'PB14',
             28: 'PB15', 29: 'PA8', 30: 'PA9', 31: 'PA10', 32: 'PA11', 33: 'PA12', 34: 'PA13', 35: 'VSS', 36: 'VDD',
             37: 'PA14', 38: 'PA15', 39: 'PB3', 40: 'PB4', 41: 'PB5', 42: 'PB6', 43: 'PB7', 44: 'BOOT0', 45: 'PB8',
             46: 'PB9', 47: 'VSS', 48: 'VDD'}
# DS5319 pin definitions: FT = PA8-PA15, PB2-PB4, PB6-PB15, PD0/PD1; not FT: PA0-PA7, PB0, PB1, PB5, PC13-PC15
F103_FT = {'PA8', 'PA9', 'PA10', 'PA11', 'PA12', 'PA13', 'PA14', 'PA15', 'PB2', 'PB3', 'PB4', 'PB6', 'PB7', 'PB8',
           'PB9', 'PB10', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15', 'PD0', 'PD1'}
VDD = 3.3
LIM_FT_V = VDD + 4.0          # abs max on FT pins
LIM_NONFT_V = 4.0             # abs max on TTa / non-FT pins
LIM_INJ = 5e-3                # per pin
LIM_INJ_TOTAL = 25e-3
FT_OPER_MAX = 5.5
VIL, VIH = 0.3 * VDD, 0.7 * VDD   # DS8626 CMOS levels (conservative; FT inputs switch at 1.79 V by design)

ADC = {**{f'EFI_ADC_{i}': f'PA{i}' for i in range(8)}, 'EFI_ADC_8': 'PB0', 'EFI_ADC_9': 'PB1',
       **{f'EFI_ADC_{10 + i}': f'PC{i}' for i in range(6)}}

# alternate functions whose direction matters (DS8626 / DS5319 alternate-function tables)
AF_DIR = {('U1', 'PB12'): ('CAN2_RX', 'in'), ('U1', 'PB13'): ('CAN2_TX', 'out'),
          ('U1', 'PC6'): ('USART6_TX', 'out'), ('U1', 'PC7'): ('USART6_RX', 'in'),
          ('U1', 'PD8'): ('USART3_TX', 'out'), ('U1', 'PD9'): ('USART3_RX', 'in'),
          ('U102', 'PA9'): ('USART1_TX', 'out'), ('U102', 'PA10'): ('USART1_RX', 'in'),
          ('U102', 'PA11'): ('CAN_RX', 'in'), ('U102', 'PA12'): ('CAN_TX', 'out')}


def mcu_pin_info(ref, pad):
    n = int(pad)
    if ref == 'U1':
        name = F407_NAME.get(n, '?')
        if not re.match(r'P[A-H]\d+$', name):
            return name, 'PWR'
        return name, 'TTa' if name in F407_TTA else 'FT'
    name = F103_NAME.get(n, '?')
    if not re.match(r'P[A-D]\d+$', name):
        return name, 'PWR'
    return name, 'FT' if name in F103_FT else 'IO'


# ------------------------------------------------------------------------------------------------------------------
# firmware configuration per year, evaluated from the board code (miata_board.cpp + miata_pins.h)
# ------------------------------------------------------------------------------------------------------------------
FW_FIELDS = {  # rusEFI field -> function label used in the rows
    'ignitionPins[0]': 'ign1&4', 'ignitionPins[1]': 'ign3(COP)', 'ignitionPins[2]': 'ign2&3', 'ignitionPins[3]': 'ign4(COP)',
    'injectionPins[0]': 'inj1', 'injectionPins[1]': 'inj2', 'injectionPins[2]': 'inj3', 'injectionPins[3]': 'inj4',
    'idle.solenoidPin': 'idle', 'fuelPumpPin': 'fuelPump', 'acRelayPin': 'acRelay', 'fanPin': 'fan', 'fan2Pin': 'fan2',
    'malfunctionIndicatorPin': 'cel', 'tachOutputPin': 'tach', 'boostControlPin': 'boost', 'mainRelayPin': 'mainRelay',
    'alternatorControlPin': 'alternator', 'vvtPins[0]': 'vvt', 'o2heaterPin': 'o2heater',
    'triggerInputPins[0]': 'trigger1', 'triggerInputPins[1]': 'trigger2', 'camInputs[0]': 'cam',
    'vehicleSpeedSensorInputPin': 'vss', 'acSwitch': 'acSwitch', 'clutchDownPin': 'clutch',
    'tps1_1AdcChannel': 'tps', 'mafAdcChannel': 'maf', 'afr.hwChannel': 'afr', 'ignKeyAdcChannel': 'ignKey',
    'vbattAdcChannel': 'vbatt', 'clt.adcChannel': 'clt', 'iat.adcChannel': 'iat', 'map.sensor.hwChannel': 'map',
    'canTxPin': 'can2Tx', 'canRxPin': 'can2Rx',   # PB13/PB12 = CAN2 peripheral, rusEFI's first bus
}
FW_OUTPUTS = {'ign1&4', 'ign3(COP)', 'ign2&3', 'ign4(COP)', 'inj1', 'inj2', 'inj3', 'inj4', 'idle', 'fuelPump',
              'acRelay', 'fan', 'fan2', 'cel', 'tach', 'boost', 'mainRelay', 'alternator', 'vvt', 'o2heater'}


def _functions(src):
    """name -> body of every top-level C++ function in src (brace matched)."""
    out = {}
    for m in re.finditer(r'^(?:static\s+)?(?:void|float|bool)\s+(\w+)\s*\([^)]*\)\s*\{', src, re.M):
        depth, i = 1, m.end()
        while depth and i < len(src):
            depth += {'{': 1, '}': -1}.get(src[i], 0)
            i += 1
        out[m.group(1)] = src[m.end():i - 1]
    return out


def firmware_configs():
    pins_h = open(os.path.join(BOARD, 'miata_pins.h')).read()
    defines = dict(re.findall(r'^#define (MIATA_\w+)\s+(\S+)', pins_h, re.M))
    src = open(os.path.join(BOARD, 'miata_board.cpp')).read()
    funcs = _functions(src)
    external = set()

    def resolve(tok):
        tok = tok.strip()
        tok = defines.get(tok, tok)
        if tok.startswith('Gpio::'):
            t = tok[6:]
            return None if t == 'Unassigned' else 'P' + t
        if tok.startswith('EFI_ADC_'):
            return None if tok == 'EFI_ADC_NONE' else ADC[tok]
        return tok

    def execute(body, cfg, ctx):
        stack = []
        for raw in body.split('\n'):
            line = raw.split('//')[0].strip()
            if not line:
                continue
            active = all(stack)
            if line.startswith('switch'):
                continue
            m = re.match(r'if\s*\((.*)\)\s*\{$', line)
            if m:
                cond = m.group(1).replace(' ', '')
                stack.append({'!nb2Early': not ctx['early'], 'nb2Early': ctx['early']}.get(cond, True))
                continue
            if line == '}' and stack:
                stack.pop()
                continue
            if not active:
                continue
            m = re.match(r'engineConfiguration->([\w.\[\]]+)\s*=\s*([^;]+);', line)
            if m:
                cfg[m.group(1)] = resolve(m.group(2))
                continue
            for name in re.findall(r'\b(\w+)\s*\([^;]*\)\s*;', line):
                if name in funcs:
                    execute(funcs[name], cfg, ctx)
                elif name not in ('strcpy', 'setTable', 'firmwareError'):
                    external.add(name)

    preset = funcs['miataApplyYearPreset']
    cases = {m.group(1): m.group(2) for m in re.finditer(r'case engine_type_e::(\w+):(.*?)break;', preset, re.S)}
    out = {}
    for year, _m, _p, etype, early in YEARS:
        cfg = {}
        ctx = {'early': early}
        execute(funcs['miataBoardDefaultConfiguration'], cfg, ctx)
        execute(cases[etype], cfg, ctx)
        execute(funcs['miataAfterTuneDefaults'], cfg, ctx)
        fw = {}
        for field, label in FW_FIELDS.items():
            v = cfg.get(field)
            if v and re.match(r'P[A-E]\d+$', v):
                fw[label] = v
        out[year] = fw
    # board-wide pins outside the tune (board_configuration.cpp, board.mk, knock_config.h, wideband flasher)
    bc = open(os.path.join(BOARD, 'board_configuration.cpp')).read()
    board = {}
    for led, port in re.findall(r'Gpio get(\w+)LedPin\(\) \{\s+return Gpio::(\w+);', bc):
        board['led' + led] = 'P' + port
    mk = re.search(r'LED_CRITICAL_ERROR_BRAIN_PIN=Gpio::(\w+)', open(os.path.join(BOARD, 'board.mk')).read())
    board['ledError'] = 'P' + mk.group(1)
    kn = re.search(r'KNOCK_PIN_CH1 Gpio::(\w+)', open(os.path.join(BOARD, 'knock_config.h')).read())
    board['knock'] = 'P' + kn.group(1)
    board['drvEnable'] = resolve('MIATA_DRV_EN')
    wb = open(os.path.join(BOARD, 'wideband_uart_flash.cpp')).read()
    for label, port in re.findall(r'efiSetPadMode\("WBO ([\w ]+)", Gpio::(\w+)', wb):
        board['wbo ' + label] = 'P' + port
    board['usbDM'], board['usbDP'], board['swdio'], board['swclk'] = 'PA11', 'PA12', 'PA13', 'PA14'
    board['uart6Tx'], board['uart6Rx'] = 'PC6', 'PC7'   # rusEFI's TS secondary / AUX UART (J5-12/13)
    return out, board, sorted(external)


def firmware_from_simlog(path):
    out = {}
    for line in open(path):
        if line.startswith('MIATA|') and '|config|' in line:
            parts = line.strip().split('|')
            kv = dict(p.split('=', 1) for p in parts[5:] if '=' in p)
            fw = {}
            ign, inj = kv['ign'].split(','), kv['inj'].split(',')
            for i, lab in enumerate(['ign1&4', 'ign3(COP)', 'ign2&3', 'ign4(COP)']):
                fw[lab] = ign[i]
            for i in range(4):
                fw[f'inj{i + 1}'] = inj[i]
            t = kv['trigger'].split(',')
            fw['trigger1'], fw['trigger2'], fw['cam'] = t[0], t[1], kv['cam']
            for k in ('fuelPump', 'fan', 'fan2', 'acRelay', 'cel', 'tach', 'idle', 'mainRelay', 'alternator',
                      'o2heater', 'vvt', 'boost', 'vss', 'acSwitch', 'clutch'):
                fw[k] = kv.get(k, '-')
            fw = {k: ('P' + v if not v.startswith('P') else v) for k, v in fw.items() if v not in ('-', '')}
            out[parts[1]] = fw
    return out


# ------------------------------------------------------------------------------------------------------------------
# design data: daughterboard, motherboards (copied, build_parts reuses a global list), harness notes
# ------------------------------------------------------------------------------------------------------------------
def mb_parts(module):
    os.chdir(SCRIPTS)
    try:
        M = importlib.import_module(module)
        parts = [dict(p, pads=dict(p['pads'])) for p in M.build_parts()]
    finally:
        os.chdir(_cwd)
    return M, parts


def harness_notes(module):
    """cavity -> comment text from the year module's HARNESS dict (and its base module's)."""
    notes = {}
    mods = [module]
    if module == 'mb_na8':
        mods = ['mb_na6', 'mb_na8']
    for mod in mods:
        src = open(os.path.join(SCRIPTS, mod + '.py')).read()
        m = re.search(r'^HARNESS(?: = \{|\.update\(\{)(.*?)^\}', src, re.S | re.M)
        if not m:
            continue
        for line in m.group(1).split('\n'):
            code, _, comment = line.partition('#')
            for k in re.findall(r"'(\w+)':", code):
                notes[k] = comment.strip()
    return notes


def load_research():
    path = os.path.join(ROOT, 'research', 'pinouts_9605.json')
    d = json.load(open(path))
    return {y: {p['terminal']: p for p in d[y]['pins']} for y in ('1996-1997', '1999-2000', '2001-2005')}


def fitted(p, board):
    if board == 'D':
        return not p.get('dnp')
    if p['ref'] == 'JP1':
        return True
    if p.get('desc', '').upper().startswith('NOT FITTED'):
        return False
    if p['value'] == '0R' and not p['lcsc']:
        return False
    return True


# ------------------------------------------------------------------------------------------------------------------
# section A: copper (routed PCB) against the design
# ------------------------------------------------------------------------------------------------------------------
def copper_names(cu, design_pads):
    """(ref, pad) -> net as the copper connects it: each copper cluster is named after the design net(s) of its pads."""
    names = {}
    for c, members in cu['clusters'].items():
        nets = sorted({design_pads[m] for m in members if m in design_pads and design_pads[m]})
        name = '+'.join(nets) if nets else ''
        for m in members:
            names[m] = name
    return names


def check_copper(label, path, parts, section='copper'):
    import board_copper
    cu = board_copper.copper_netlist(os.path.join(ROOT, path))
    dp = {(p['ref'], k): v for p in parts for k, v in p['pads'].items()}
    r = board_copper.compare(cu, dp)
    bad = False
    for net, groups in r['opens']:
        bad = True
        row('FAIL', section, label, f'{path}: net {net} is split in copper: ' + ' | '.join(','.join(g) for g in groups))
    for nets in r['shorts']:
        bad = True
        row('FAIL', section, label, f'{path}: copper shorts ' + ' + '.join(f'{n} ({",".join(v[:4])})' for n, v in nets.items()))
    for ref, pad, net, got in r['label']:
        bad = True
        row('FAIL', section, label, f'{path}: {ref}.{pad} design net {net}, net stored in the PCB {got}')
    for ref in r['missing_fp']:
        bad = True
        row('FAIL', section, label, f'{path}: footprint {ref} from the design is not on the board')
    for ref, pad, net in r['missing_pad']:
        bad = True
        row('FAIL', section, label, f'{path}: {ref} has no pad {pad} (design net {net})')
    for ref, pad, net in r['extra_net']:
        row('CHECK', section, label, f'{path}: {ref}.{pad} carries {net} in the PCB but has no net in the design')
    extra = [x for x in r['extra_fp'] if not re.match(r'H\d+$|HD\d+$', x)]
    if extra:
        row('CHECK', section, label, f'{path}: footprints not in the design: {extra}')
    st = cu['stats']
    if not bad:
        row('OK', section, label, f'{path}: copper netlist from geometry ({st["pads"]} pads, {st["tracks"]} tracks, '
            f'{st["vias"]} vias, {st["zone_islands"]} zone islands, layers {"/".join(cu["layers"])}) = design: '
            f'0 opens, 0 shorts, 0 label differences')
    return cu, copper_names(cu, dp)


def check_mating(daughter_cu_path, mb_path, year, pcbs):
    """Re-run of the header/socket check (VERIFICATION.md 'Daughter <-> motherboard', 5 x 80): J1/J2 pads of the
    daughterboard against JD1/JD2 of the motherboard, by position (pure translation) and net."""
    import pcbnew
    if 'D' not in pcbs:
        pcbs['D'] = pcbnew.LoadBoard(os.path.join(ROOT, daughter_cu_path))
    if mb_path not in pcbs:
        pcbs[mb_path] = pcbnew.LoadBoard(os.path.join(ROOT, mb_path))
    d, m = pcbs['D'], pcbs[mb_path]

    def pads(b, ref):
        fp = b.FindFootprintByReference(ref)
        return {p.GetNumber(): (p.GetPosition().x * 1e-6, p.GetPosition().y * 1e-6, p.GetNetname().split('/')[-1])
                for p in fp.Pads()}
    dj = {**{('1', k): v for k, v in pads(d, 'J1').items()}, **{('2', k): v for k, v in pads(d, 'J2').items()}}
    mj = {**{('1', k): v for k, v in pads(m, 'JD1').items()}, **{('2', k): v for k, v in pads(m, 'JD2').items()}}
    ox = mj[('1', '1')][0] - dj[('1', '1')][0]
    oy = mj[('1', '1')][1] - dj[('1', '1')][1]
    bad = []
    for k, (x, y, n) in dj.items():
        if k not in mj:
            bad.append(f'J{k[0]}.{k[1]} has no socket pad')
            continue
        X, Y, N = mj[k]
        if abs(X - x - ox) > 0.02 or abs(Y - y - oy) > 0.02:
            bad.append(f'J{k[0]}.{k[1]} off by {X - x - ox:.3f},{Y - y - oy:.3f} mm')
        if N != n and not (n == 'HTR_GND' and N == 'GND'):
            bad.append(f'J{k[0]}.{k[1]} {n} on JD{k[0]}.{k[1]} {N}')
    if bad:
        row('FAIL', 'mating', year, f'{mb_path}: ' + '; '.join(bad[:6]))
    else:
        row('OK', 'mating', year, f'{mb_path}: all {len(dj)} J1/J2 pads land on JD1/JD2 by pure translation '
            f'({ox:.2f}, {oy:.2f} mm), same pin and net (HTR_GND -> motherboard GND by design)')


# ------------------------------------------------------------------------------------------------------------------
# system netlist (daughterboard + one motherboard, joined at J1/JD1 and J2/JD2) from the copper-derived nets
# ------------------------------------------------------------------------------------------------------------------
class System:
    def __init__(self, year, dparts, dnames, mparts, mnames):
        self.year = year
        uf = {}

        def find(a):
            uf.setdefault(a, a)
            while uf[a] != a:
                uf[a] = uf[uf[a]]
                a = uf[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                uf[ra] = rb
        dnet = lambda ref, pad: dnames.get((ref, pad), '')
        mnet = lambda ref, pad: ('M:' + mnames[(ref, pad)]) if mnames.get((ref, pad)) else ''
        for hdr, sock in (('J1', 'JD1'), ('J2', 'JD2')):
            for k in range(1, 41):
                a, b = dnet(hdr, str(k)), mnet(sock, str(k))
                if a and b:
                    union(a, b)
        classes = collections.defaultdict(set)
        for p in dparts:
            for k in p['pads']:
                n = dnet(p['ref'], k)
                if n:
                    classes[find(n)].add(n)
        for p in mparts:
            for k in p['pads']:
                n = mnet(p['ref'], k)
                if n:
                    classes[find(n)].add(n)
        self.canon = {}
        self.joined = []
        for root, members in classes.items():
            dn = sorted(m for m in members if not m.startswith('M:'))
            if 'GND' in dn:
                name = 'GND'
            elif dn:
                name = dn[0]
            else:
                name = sorted(members)[0]
            if len(set(dn) - {'HTR_GND'}) > 1 or (len(dn) > 1 and 'GND' not in dn):
                self.joined.append(sorted(members))
            for m in members:
                self.canon[m] = name
        self.parts = []
        for p in dparts:
            pads = {k: self.canon.get(dnet(p['ref'], k), '') for k in p['pads']}
            self.parts.append(dict(p, ref=p['ref'], board='D', pads=pads, fitted=fitted(p, 'D')))
        for p in mparts:
            pads = {k: self.canon.get(mnet(p['ref'], k), '') for k in p['pads']}
            self.parts.append(dict(p, ref='M.' + p['ref'], board='M', pads=pads, fitted=fitted(p, 'M')))
        self.by_ref = {p['ref']: p for p in self.parts}
        self.net_pads = collections.defaultdict(list)
        for p in self.parts:
            for k, n in p['pads'].items():
                if n:
                    self.net_pads[n].append((p['ref'], k))
        # harness cavity -> system net; JD pins per net
        self.cavity = {k: v for k, v in self.by_ref['M.J1']['pads'].items()}

    def mcu_pins(self, net):
        return [(r, k) for r, k in self.net_pads.get(net, []) if r in ('U1', 'U102')]


# ------------------------------------------------------------------------------------------------------------------
# path tracing through the circuit
# ------------------------------------------------------------------------------------------------------------------
RAILS = {'GND', '+3V3', '+3V3A', '+5V', '+12V', 'V5_SENS', 'V5_EXT', 'V5_H1', 'V5_H2', 'WB_VDDA', '+12V_F', 'DAMP',
         'KN_BIAS', 'VR_BIAS', 'VCAP1', 'VCAP2', 'BUCK_SW', 'BUCK_BOOT', 'SH_K', 'SH_REF'}
V5_RAILS = {'V5_SENS': 'U3 TLS115 output, on-board MAP sensor only', 'V5_EXT': 'U14 TLS115 output, protected harness 5 V'}
IC_MAP = {}   # value -> [(pad a, pad b, label)]
IC_MAP['ULN2003AD'] = [(str(1 + i), str(16 - i), 'ULN2003 ch%d' % (1 + i)) for i in range(7)]   # rev 0.7
IC_MAP['TC4427'] = [('2', '7', 'TC4427 A'), ('4', '5', 'TC4427 B')]
IC_MAP['SN74LVC4245APWR'] = [(str(14 + i), str(10 - i), 'LVC4245 B%d->A%d' % (7 - i, 7 - i)) for i in range(8)]
IC_MAP['NCV8406ASTT3G'] = [('1', '2', 'NCV8406A gate->drain')]
IC_MAP['VND7NV04TR-E'] = [('1', '2', 'VND7NV04 input->drain')]
IC_MAP['ZXMS6004FFTA'] = [('1', '3', 'ZXMS6004 input->drain')]
IC_MAP['74HCT04PW'] = [('1', '2', '74HCT04 1A->1Y'), ('3', '4', '74HCT04 2A->2Y'), ('5', '6', '74HCT04 3A->3Y'),
                       ('9', '8', '74HCT04 4A->4Y'), ('11', '10', '74HCT04 5A->5Y'), ('13', '12', '74HCT04 6A->6Y')]
IC_MAP['VND14NV04'] = [('1', '2', 'VND14NV04 gate->drain')]
IC_MAP['LM2903DR'] = [('3', '1', 'LM2903 A+'), ('2', '1', 'LM2903 A-'), ('5', '7', 'LM2903 B+'), ('6', '7', 'LM2903 B-')]
IC_MAP['LMV321IDBVR'] = [('1', '4', 'LMV321 +'), ('3', '4', 'LMV321 -')]
IC_MAP['SN65HVD230DR'] = [('1', '7', 'CAN D->H'), ('1', '6', 'CAN D->L'), ('4', '7', 'CAN R<-H'), ('4', '6', 'CAN R<-L')]
IC_MAP['TCAN1042VDRQ1'] = [('1', '7', 'CAN TXD->H'), ('1', '6', 'CAN TXD->L'), ('4', '7', 'CAN RXD<-H'),
                           ('4', '6', 'CAN RXD<-L')]
IC_MAP['MCP6004'] = [('2', '1', 'MCP6004 A-'), ('3', '1', 'MCP6004 A+'), ('6', '7', 'MCP6004 B-'), ('5', '7', 'MCP6004 B+'),
                     ('9', '8', 'MCP6004 C-'), ('10', '8', 'MCP6004 C+'), ('13', '14', 'MCP6004 D-'), ('12', '14', 'MCP6004 D+')]
IC_MAP['AD8628'] = [('3', '1', 'AD8628 +'), ('4', '1', 'AD8628 -')]
IC_MAP['TLS115B0EJ'] = [('5', '1', 'TLS115 ADJ->OUT')]
CONNECTORS = {'M.J1': 'harness', 'M.J2': 'LSU conn', 'M.J3': 'IAT conn', 'M.J4': 'USB-C', 'M.J5': 'AUX',
              'M.U2': 'MAP sensor'}


def graph(sysm):
    """net -> [(other net, label)] for passable elements."""
    g = collections.defaultdict(list)
    blocked = collections.defaultdict(list)    # net -> [(other net, why)] for not-fitted / jumper-open parts
    for p in sysm.parts:
        ref, val, pads = p['ref'], p['value'], p['pads']
        base = ref.split('.')[-1]
        kind = re.match(r'[A-Z]+', base).group(0)
        if kind in ('R', 'F', 'L', 'FB') and len(pads) == 2:
            a, b = pads.get('1', ''), pads.get('2', '')
            if not a or not b:
                continue
            lab = f'{ref}({val})'
            if not p['fitted']:
                blocked[a].append((b, f'{ref} not fitted')); blocked[b].append((a, f'{ref} not fitted'))
                continue
            g[a].append((b, lab)); g[b].append((a, lab))
        elif kind == 'RN':
            for i in range(1, 5):
                a, b = pads.get(str(i), ''), pads.get(str(9 - i), '')
                if a and b:
                    g[a].append((b, f'{ref}({val})')); g[b].append((a, f'{ref}({val})'))
        elif kind == 'C' and len(pads) == 2 and p['board'] == 'D':
            a, b = pads.get('1', ''), pads.get('2', '')
            if a and b and a not in RAILS and b not in RAILS:
                g[a].append((b, f'{ref}({val}, AC)')); g[b].append((a, f'{ref}({val}, AC)'))
        elif kind == 'D' and p['board'] == 'D' and len(pads) == 2:
            a, b = pads.get('1', ''), pads.get('2', '')
            if a and b and a not in RAILS and b not in RAILS:
                g[b].append((a, f'{ref}({val})'))          # anode (pad 2) -> cathode (pad 1) only
        elif base == 'JP1':
            # shunt on 2-3 (EXT) by default; 1-2 (STOCK) is an option
            a, b, c = pads.get('1', ''), pads.get('2', ''), pads.get('3', '')
            g[b].append((c, 'JP1 2-3 (EXT, default)')); g[c].append((b, 'JP1 2-3 (EXT, default)'))
            blocked[a].append((b, 'JP1 1-2 (STOCK) shunt option')); blocked[b].append((a, 'JP1 1-2 (STOCK) shunt option'))
        elif val in IC_MAP and p['fitted']:
            for x, y, lab in IC_MAP[val]:
                a, b = pads.get(x, ''), pads.get(y, '')
                if a and b:
                    g[a].append((b, f'{ref} {lab}')); g[b].append((a, f'{ref} {lab}'))
    return g, blocked


def trace(sysm, g, blocked, start, stop_at_rails=True):
    """BFS from a net. -> dict endpoint -> path list; endpoints: ('mcu', ref, pad), ('rail', net), ('conn', ref, pad),
    ('blocked', why)."""
    seen = {start: []}
    queue = collections.deque([start])
    ends = {}
    while queue:
        n = queue.popleft()
        path = seen[n]
        if n in RAILS and stop_at_rails and n != start:
            ends.setdefault(('rail', n), path + [n])
            continue
        for r, k in sysm.net_pads.get(n, []):
            if r in ('U1', 'U102'):
                ends.setdefault(('mcu', r, k), path + [n])
            elif r in CONNECTORS and not (r == 'M.J1' and n == start):
                ends.setdefault(('conn', r, k), path + [n])
        if n in RAILS and stop_at_rails:      # the start itself is a rail (e.g. a V5_SENS cavity)
            ends.setdefault(('rail', n), path + [n])
            continue
        for m, lab in g.get(n, []):
            if m not in seen:
                seen[m] = path + [n, lab]
                queue.append(m)
        for m, why in blocked.get(n, []):
            ends.setdefault(('blocked', why, m), path + [n])
    return ends


def fmt_path(p):
    return ' -> '.join(p)


def mcu_label(ref, pad):
    name, typ = mcu_pin_info(ref, pad)
    return f'{"F407" if ref == "U1" else "F103"} {name}({typ})'


# ------------------------------------------------------------------------------------------------------------------
# expected daughter endpoints for each header net (design intent)
# ------------------------------------------------------------------------------------------------------------------
HDR_EXPECT = {
    'VBAT_IN': {'AN_VBATT', 'WB_VBAT_DIV'}, 'VIGN_IN': {'AN_VIGN'}, 'IN_KNOCK': {'AN_KNOCK'},
    'VR1_P': {'VR1_OUT'}, 'VR1_N': {'VR1_OUT'}, 'VR2_P': {'VR2_OUT'}, 'VR2_N': {'VR2_OUT'},
    'CAN_H': {'CAN_RX', 'CAN_TX', 'WB_CAN_RX', 'WB_CAN_TX'}, 'CAN_L': {'CAN_RX', 'CAN_TX', 'WB_CAN_RX', 'WB_CAN_TX'},
    'USB_DM': {'USB_DM'}, 'USB_DP': {'USB_DP'}, 'UART_TX': {'UART_TX_M'}, 'UART_RX': {'UART_RX_M'},
    'LSU_UN': {'WB_UN_SENSE'}, 'LSU_VM': {'LSU_VM', 'WB_VM'}, 'LSU_IP': {'WB_IP_SENSE'}, 'LSU_RT': {'WB_IP_SENSE'},
    'LSU_HTR_N': {'WB_HTR_PWM'}, 'IN_HALL1': {'HALL1'}, 'IN_HALL2': {'HALL2'},
    'IN_SW1': {'SW1'}, 'IN_SW2': {'SW2'}, 'IN_SW3': {'SW3'},
}


def expected_mcu_nets(net):
    if net in HDR_EXPECT:
        return HDR_EXPECT[net]
    if net.startswith('OUT_'):
        return {net[4:] + '_CTL'}
    if net.startswith('IN_'):
        return {'AN_' + net[3:]}
    return set()


# semantic check against the independent research table (1996-2005)
SEM = [('OUT_INJ', r'injector'), ('OUT_IGN', r'igniter|ignition|IGT'), ('OUT_FP', r'fuel pump'),
       ('OUT_FAN', r'fan'), ('OUT_LS7', r'fan'), ('OUT_AC', r'A/C'), ('OUT_CEL', r'MIL|check engine'),
       ('OUT_TACH', r'tach'), ('OUT_IACV', r'idle|IAC'), ('OUT_VVT', r'OCV|oil control|heater|purge'),
       ('OUT_ALT', r'generator|alternator|field'), ('OUT_MAINRLY', r'main relay|VICS'),
       ('IN_TPS', r'throttle|TP sensor'), ('IN_CLT', r'coolant|ECT'), ('HARN_IAT', r'intake air temp|IAT'),
       ('IN_AUX3', r'MAF|air flow'), ('IN_AUX2', r'HO2S|O2'), ('IN_AUX1', r'HO2S|O2'),
       ('IN_HALL1', r'crank|CKP|SGT|NE\b'), ('IN_HALL2', r'cam|CMP|SGC'), ('IN_SW1', r'speed|VSS'),
       ('IN_SW2', r'A/C'), ('IN_SW3', r'clutch'), ('IN_KNOCK', r'knock'), ('V5_SENS', r'\+5|VREF|reference'),
       ('V5_EXT', r'\+5|VREF|reference'),
       ('GND', r'ground'), ('VBAT_IN', r'main relay|\+12'), ('VIGN_IN', r'ignition|IG1'),
       ('M:IAC_12V', r'IAC|idle'), ('M:OCV_12V', r'OCV')]

# car-driven text (1989-95 harness comments)
NA_CAR_DRIVES = r'\+12|switch|sensor|signal|speed|data link|diagnosis|A/T|temp|flap|O2'
NA_ECU_DRIVES = r'relay|igniter|injector|solenoid|lamp|tach'
DOCUMENTED = r'not used|not read|not driven|never drive|left open|only through|unused|not any more|not the fan|empty|A/T'


def documented_open(module, cav, func_txt):
    """the year module's docstring / VERIFY list names the cavity (or its function) as left open"""
    M = importlib.import_module(module)
    text = (M.__doc__ or '') + ' '.join(getattr(M, 'VERIFY', []))
    if re.search(r'(?<![0-9A-Z])' + re.escape(cav) + r'(?![A-Z0-9])', text):
        return True
    words = [w for w in re.findall(r'[A-Za-z][A-Za-z-]{3,}', func_txt) if w.lower() not in
             ('sensor', 'signal', 'input', 'control', 'valve', 'solenoid', 'switch', 'output', 'from', 'with')]
    return any(re.search(re.escape(w), text, re.I) for w in words[:2])


# ------------------------------------------------------------------------------------------------------------------
# section 1: connectivity
# ------------------------------------------------------------------------------------------------------------------
def connectivity(sysm, year, module, fw, board_fw, research, notes):
    g, blocked = graph(sysm)
    for members in sysm.joined:
        row('FAIL', 'connect', year, f'the motherboard joins different daughterboard nets: {members}')
    res = research.get(RESEARCH_YEAR.get(year, ''), {})
    harness = importlib.import_module(module).HARNESS
    # which MCU pins each firmware function uses (per year) and pins used board-wide
    port_func = collections.defaultdict(list)
    for f, port in fw.items():
        port_func[port].append(f)
    for f, port in board_fw.items():
        port_func[port].append(f)
    early = year == '2001-02'
    unwired_early = {'3H', '4S'} if early else set()

    n_ok = n_open = 0
    cav_ends = {}
    for cav in sorted(sysm.cavity, key=lambda c: (c[0], len(c), c)):
        net = sysm.cavity[cav]
        design_net = harness.get(cav, '')
        rinfo = res.get(cav)
        note = notes.get(cav, '')
        func_txt = rinfo['function'] if rinfo else note
        direction = rinfo['direction'] if rinfo else None
        if (design_net or '') and net != sysm.canon.get('M:' + design_net, design_net) and not net:
            row('FAIL', 'connect', year, f'{cav}: design net {design_net}, copper leaves it unconnected')
        if not net:
            # empty cavity: does the car drive something here?
            car_drives = (direction in ('in', 'power', 'ground')) if rinfo else bool(re.search(NA_CAR_DRIVES, note))
            ecu_out = (direction == 'out') if rinfo else bool(re.search(NA_ECU_DRIVES, note))
            if car_drives or ecu_out:
                what = 'car-driven signal' if car_drives else 'OEM ECU output'
                documented = bool(note) or bool(re.search(DOCUMENTED, func_txt, re.I)) \
                    or bool(rinfo and rinfo.get('do_not_drive')) or documented_open(module, cav, func_txt)
                n_open += 1
                row('OK' if documented else 'CHECK', 'connect', year,
                    f'{cav}: not connected; {what}: "{func_txt[:70]}"' + ('' if documented else ' (not documented as intentional)'))
            continue
        ends = trace(sysm, g, blocked, net)
        cav_ends[cav] = ends
        mcu = sorted({e for e in ends if e[0] == 'mcu'}, key=lambda e: len(ends[e]))
        rails = sorted({e[1] for e in ends if e[0] == 'rail'})
        blk = sorted({e[1] for e in ends if e[0] == 'blocked'})
        # JD pins on the way
        jd = [f'{r[2:]}.{k}' for r, k in sysm.net_pads.get(net, []) if r in ('M.JD1', 'M.JD2')]
        if len(jd) > 4:
            jd = [f'{len(jd)} pins']
        exp = expected_mcu_nets(net)
        got_nets = {sysm.by_ref[e[1]]['pads'][e[2]] for e in mcu}
        status, issues = 'OK', []
        if cav in unwired_early:
            issues.append('no harness wire on 2001-02')
        if exp and not (exp & got_nets):
            status = 'FAIL'
            issues.append(f'expected to reach {sorted(exp)}')
        if not mcu and not rails and net not in RAILS:
            if blk:
                issues.append('reaches nothing with the default fit: ' + ', '.join(blk))
                # JP1 on EXT and the not-fitted links are deliberate options; anything else blocked is a problem
                status = 'OK' if all('JP1' in x or 'not fitted' in x for x in blk) else 'CHECK'
            else:
                status = 'FAIL'
                issues.append('lands nowhere')
        # semantic / direction check against the independent table (96-05)
        if rinfo:
            if rinfo.get('do_not_drive') and (net.startswith('OUT_') or net in V5_RAILS):
                status = 'FAIL'
                issues.append('ECU output on a do-not-drive cavity')
            for pre, pat in SEM:
                if net.startswith(pre) or net == pre:
                    if not re.search(pat, rinfo['function'], re.I):
                        status = 'FAIL' if rinfo.get('confidence') == 'high' else max(status, 'CHECK', key=SEV.get)
                        issues.append(f'research says "{rinfo["function"][:60]}"')
                    break
            if net.startswith('OUT_') and direction in ('in', 'power'):
                status = 'FAIL'
                issues.append(f'two drivers: the car drives this cavity ({direction})')
        if year == '1989-93' and cav == '1N':
            status = max(status, 'CHECK', key=SEV.get)
            issues.append('sensor 5 V driven onto 1N: the 1990 table shows 1N empty and on 1994 cars it goes to the A/T unit '
                          '(VERIFICATION pinout finding 4): check on automatics')
        if year in ('1989-93', '1994-95') and cav == '2I':
            status = max(status, 'CHECK', key=SEV.get)
            issues.append('two-driver risk: rusEFI wiki tables call 2I a tach INPUT (VERIFICATION pinout finding 6)')
        # describe the main endpoint(s)
        desc = []
        for e in mcu[:3]:
            ref, pad = e[1], e[2]
            pname = mcu_pin_info(ref, pad)[0]
            funcs = port_func.get(pname, []) if ref == 'U1' else []
            desc.append(f'{mcu_label(ref, pad)}' + (f' [fw: {",".join(funcs)}]' if funcs else
                                                    (' [fw: not used]' if ref == 'U1' else '')))
        if net in RAILS:
            src = {'GND': 'ECU ground', '+12V': 'logic supply', **V5_RAILS}.get(net, '')
            desc = [f'rail {net} ({src})']
            mcu = []
        else:
            for rl in rails:
                if rl == 'GND':
                    continue
                sensed = sorted({mcu_label(r, k) for q in sysm.parts if q['ref'][0] == 'R' and rl in q['pads'].values()
                                 for n2 in q['pads'].values() if n2 != rl for r, k in sysm.mcu_pins(n2)})
                desc.append(f'rail {rl}' + (f' (sensed by {", ".join(sensed)})' if sensed else ''))
        main_path = fmt_path(ends[mcu[0]]) if mcu else ''
        n_ok += status == 'OK'
        row(status, 'connect', year, f'{cav} {net} (JD {",".join(jd) or "-"}): ' + '; '.join(desc or ['-'])
            + (f'  path: {main_path}' if main_path else '')
            + (f'  {"!!" if status != "OK" else "note:"} {"; ".join(issues)}' if issues else ''))

    # reverse direction: every firmware function -> cavity, compared with sim_report's EXPECTED
    exp_tab = sim_report.EXPECTED.get(year, {})
    fw_to_exp = {'ign1&4': 'ign1&4', 'ign2&3': 'ign2&3', 'inj1': 'inj1', 'inj2': 'inj2', 'inj3': 'inj3', 'inj4': 'inj4',
                 'fuelPump': 'fuelPump', 'fan': 'fan', 'fan2': 'fan2', 'acRelay': 'acRelay', 'cel': 'cel', 'tach': 'tach',
                 'idle': 'idle', 'vss': 'vss', 'acSwitch': 'acSwitch', 'clutch': 'clutch', 'mainRelay': 'mainRelay',
                 'alternator': 'alternator', 'o2heater': 'o2heater', 'vvt': 'vvt'}
    if year in ('1989-93', '1994-95', '1996-97'):
        fw_to_exp.update({'trigger1': 'cam(SGC)', 'trigger2': 'crank(SGT)'})
    else:
        fw_to_exp.update({'trigger1': 'crank', 'cam': 'cam'})
    seen_exp = set()
    for func, port in sorted(fw.items()):
        pin = F407_PIN.get(port)
        net = sysm.by_ref['U1']['pads'].get(str(pin), '') if pin else ''
        if not net:
            row('FAIL', 'reverse', year, f'{func} on {port}: pin has no net on the daughterboard')
            continue
        ends = trace(sysm, g, blocked, net)
        cavs = sorted({e[2] for e in ends if e[0] == 'conn' and e[1] == 'M.J1'})
        other = sorted({f'{CONNECTORS[e[1]]}-{e[2]}' for e in ends if e[0] == 'conn' and e[1] != 'M.J1'})
        key = fw_to_exp.get(func)
        want = exp_tab.get(key) if key else None
        if key:
            seen_exp.add(key)
        if func == 'ignKey':
            continue
        if want:
            ok = want in cavs and not (set(cavs) - {want} - unwired_early)
            row('OK' if ok else 'FAIL', 'reverse', year, f'{func} {port} ({net}) -> harness {cavs or "-"}'
                + (f', {other}' if other else '') + f'; reference cavity {want}')
        elif key and not want:
            # firmware drives a function the reference table doesn't have for this year
            row('FAIL' if cavs else 'CHECK', 'reverse', year, f'{func} {port} ({net}) -> harness {cavs or "-"}: '
                'no reference cavity for this function on this year')
        else:
            sev = 'OK'
            if func in FW_OUTPUTS and cavs:
                sev = 'CHECK'
            row(sev, 'reverse', year, f'{func} {port} ({net}) -> harness {cavs or "-"}' + (f', {other}' if other else '')
                + ('' if cavs or other else ' (on-board)'))
    for key, cav in exp_tab.items():
        if key not in seen_exp and key not in ('ignKey',):
            row('FAIL', 'reverse', year, f'reference function {key} ({cav}) has no firmware pin')
    # ignition sense
    vign_cav = [c for c, n in sysm.cavity.items() if n == 'VIGN_IN' and c not in unwired_early]
    has_key = 'ignKey' in fw
    want = exp_tab.get('ignKey')
    ok = (has_key and want in vign_cav) or (not has_key and not want)
    row('OK' if ok else 'FAIL', 'reverse', year, f'ignition sense {"PA2 (AN_VIGN)" if has_key else "not configured"}; '
        f'VIGN_IN cavities wired {vign_cav or "-"}; reference {want or "none"}')
    # unused F407 GPIO with a harness path but no firmware function (informational)
    for pad, net in sorted(sysm.by_ref['U1']['pads'].items(), key=lambda kv: int(kv[0])):
        name, typ = mcu_pin_info('U1', pad)
        if typ == 'PWR' or not net or port_func.get(name):
            continue
        ends = trace(sysm, g, blocked, net)
        cavs = sorted({e[2] for e in ends if e[0] == 'conn' and e[1] == 'M.J1'} - unwired_early)
        if cavs:
            fn = '; '.join(f'{c}: {(res.get(c) or {}).get("function", notes.get(c, ""))[:40]}' for c in cavs)
            row('CHECK' if net.endswith('_CTL') else 'OK', 'reverse', year,
                f'{name} ({net}) reaches harness {cavs} but the firmware assigns no function to it ({fn})'
                + (' -> that OEM output is never driven' if net.endswith('_CTL') else ' -> analog input available, not read'))
    return g, blocked, cav_ends


def drivers_check(sysm, year, fw, board_fw, research, notes):
    """two drivers on one net (push-pull + anything, open drain + car output); intentional open-drain pairs."""
    res = research.get(RESEARCH_YEAR.get(year, ''), {})
    out_ports = {p for f, p in fw.items() if f in FW_OUTPUTS} | {board_fw[k] for k in board_fw if k.startswith('led')} \
        | {board_fw['wbo BOOT0'], 'PB13', 'PC6', 'PD8'}
    od_ports = {board_fw['drvEnable'], board_fw['wbo NRST']}
    drv = collections.defaultdict(list)    # net -> [(who, kind)]  kind: pp / od
    for p in sysm.parts:
        ref, val = p['ref'], p['value']
        if not p['fitted']:
            continue
        for pad, net in p['pads'].items():
            if not net or net in RAILS:
                continue
            if ref == 'U1':
                name = mcu_pin_info('U1', pad)[0]
                if name in od_ports:
                    drv[net].append((f'U1 {name}', 'od'))
                elif name in out_ports:
                    drv[net].append((f'U1 {name}', 'pp'))
            elif ref == 'U102':
                name = mcu_pin_info('U102', pad)[0]
                if name in ('PA6', 'PB10', 'PB5', 'PB6', 'PB7', 'PB8', 'PB9', 'PA9', 'PA12'):
                    drv[net].append((f'U102 {name}', 'pp'))
            elif val == 'ULN2003AD' and pad in ('10', '11', '12', '13', '14', '15', '16'):
                drv[net].append((f'{ref}.{pad}', 'od'))
            elif val == 'TC4427' and pad in ('5', '7'):
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val in ('NCV8406ASTT3G', 'VND14NV04', 'VND7NV04TR-E') and pad == '2':
                drv[net].append((f'{ref}.{pad}', 'od'))
            elif val == 'ZXMS6004FFTA' and pad == '3':
                drv[net].append((f'{ref}.{pad}', 'od'))
            elif val == 'SN74LVC4245APWR' and pad in [str(i) for i in range(3, 11)]:
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val == '74HCT04PW' and pad in ('2', '4', '6', '8', '10', '12'):
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val == 'TCAN1042VDRQ1' and pad == '4':
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val == 'MCP6004' and pad in ('1', '7', '8', '14'):
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val in ('AD8628',) and pad == '1' or val == 'LMV321IDBVR' and pad == '4':
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val == 'LM2903DR' and pad in ('1', '7'):
                drv[net].append((f'{ref}.{pad}', 'od'))
            elif val == 'SN65HVD230DR' and pad == '4':
                drv[net].append((f'{ref}.{pad}', 'pp'))
            elif val == 'MPX5700AP' and pad == '1':
                drv[net].append((f'{ref}.{pad}', 'pp'))
    # nets joined through fitted 0R links count as one net
    links = [(p['pads']['1'], p['pads']['2'], p['ref']) for p in sysm.parts
             if p['fitted'] and p['value'] == '0R' and p['board'] == 'M']
    group = {}
    for a, b, r in links:
        ga, gb = group.get(a, {a}), group.get(b, {b})
        for n in ga | gb:
            group[n] = ga | gb
    done = set()
    # the car side: a cavity whose OEM signal is driven by the car
    car_drv = collections.defaultdict(list)
    for cav, net in sysm.cavity.items():
        if not net:
            continue
        r = res.get(cav)
        if r and r['direction'] in ('in', 'power') and net.startswith('OUT_'):
            car_drv[net].append(f'car {cav}')
    for net in list(drv):
        nets = frozenset(group.get(net, {net}))
        if nets in done:
            continue
        done.add(nets)
        ds = [d for n in nets for d in drv.get(n, [])]
        cars = [c for n in nets for c in car_drv.get(n, [])]
        pp = [d for d in ds if d[1] == 'pp']
        if len(ds) + len(cars) <= 1:
            continue
        names = ', '.join(d[0] for d in ds) + (', ' + ', '.join(cars) if cars else '')
        if pp and len(ds) + len(cars) > 1:
            row('FAIL', 'drivers', year, f'{"/".join(sorted(nets))}: push-pull driver with another driver: {names}')
        elif cars:
            row('FAIL', 'drivers', year, f'{"/".join(sorted(nets))}: ECU low side on a cavity the car drives: {names}')
        else:
            # open-drain pair: fine only if the firmware switches both together (1989-93 batch pairs)
            pair_ok = False
            if year == '1989-93' and nets >= {'OUT_INJ1', 'OUT_INJ4'} or nets >= {'OUT_INJ2', 'OUT_INJ3'}:
                inj = [fw.get(f'inj{i}') for i in range(1, 5)]
                pair_ok = all(inj) and len(set(inj)) == 4
            row('OK' if pair_ok else 'FAIL', 'drivers', year,
                f'{"/".join(sorted(nets))}: open-drain drivers in parallel ({names})'
                + (': rusEFI batch mode fires slot 1 with 4 and 3 with 2 (1-3-4-2), so they switch together'
                   if pair_ok else ''))
    if not any(r[1] == 'drivers' and r[2] == year and r[0] != 'OK' for r in ROWS):
        row('OK', 'drivers', year, f'no net has two drivers except intentional pairs ({len(done)} driven nets checked, '
            'MCU outputs per this year\'s tune, IC outputs, car-driven cavities from the research table)')


# datasheet rules for pins left unconnected in the design ('' or absent): value -> {pad: reason it may float}
NC_OK = {
    'STM32F407VGT6': 'unused GPIO (rusEFI starts unused pins as input with pull-down; ST: no tie needed)',
    'STM32F103C8T6': 'unused GPIO (F103 resets to floating input; ST AN4899 recommends analog/pull, not required)',
    'TC4427': {'1': 'NC per datasheet', '8': 'NC per datasheet'},
    'SN65HVD230DR': {'5': 'Vref output, may be left open'},
    'SN74LVC4245APWR': {'3': 'A8 output of an unused channel (its B8 input is tied to GND): may float'},
    '74HCT04PW': {'10': 'output of an unused inverter (input tied to GND)',
                  '12': 'output of an unused inverter (input tied to GND)'},
    'TLS115B0EJ': {'2': 'N.C. (leave unconnected)', '4': 'N.C. (leave unconnected)', '6': 'N.C. (leave unconnected)'},
    'MPX5700AP': {'4': 'internal connection: do not connect', '5': 'internal connection: do not connect',
                  '6': 'internal connection: do not connect'},
}
MUST_TIE = {  # value -> {pad: (required net, why)}
    'TLS115B0EJ': {'7': ('+12V', 'EN: internal pull-down turns the tracker off; tie to IN'), '8': ('+12V', 'IN'),
                   '5': ('+5V', 'ADJ reference')},
    'LMR14020': {'3': ('+12V_F', 'EN (tie to VIN or divider)'), '7': ('GND', 'GND'), '9': ('GND', 'exposed pad')},
    'SN74LVC4245APWR': {'2': ('GND', 'DIR: low = B->A'), '22': ('DRV_EN_N', 'OE')},
    'STM32F407VGT6': {'94': ('BOOT0', 'BOOT0 pulled down'), '37': ('BOOT1', 'PB2/BOOT1 pulled down'),
                      '20': ('GND', 'VSSA'), '21': ('+3V3A', 'VREF+'), '22': ('+3V3A', 'VDDA'),
                      '49': ('VCAP1', 'VCAP1'), '73': ('VCAP2', 'VCAP2'), '6': ('+3V3', 'VBAT')},
    'STM32F103C8T6': {'1': ('+3V3', 'VBAT'), '8': ('GND', 'VSSA'), '9': ('WB_VDDA', 'VDDA'), '44': ('WB_BOOT0', 'BOOT0'),
                      '20': ('WB_BOOT1', 'PB2/BOOT1')},
    'SN65HVD230DR': {'8': ('GND', 'Rs: GND = high speed (open would be standby? low-power mode)')},
    'TCAN1042VDRQ1': {'3': ('+5V', 'VCC 4.5-5.5 V'), '5': ('+3V3', 'VIO = MCU I/O level'),
                      '8': ('GND', 'STB: low = normal mode (internal pull-up would select standby)'), '2': ('GND', 'GND')},
    '74HCT04PW': {'14': ('+5V', 'VCC'), '7': ('GND', 'GND'), '11': ('GND', 'unused CMOS input must be tied'),
                  '13': ('GND', 'unused CMOS input must be tied')},
    'TL431AIDBZR': {'3': ('GND', 'anode')},
}
PULL_REQ = {('STM32F407VGT6', 'BOOT0'): 'GND', ('STM32F407VGT6', 'BOOT1'): 'GND',
            ('STM32F103C8T6', 'WB_BOOT0'): 'GND', ('STM32F103C8T6', 'WB_BOOT1'): 'GND'}


FLOAT_INPUTS = [  # (value, pads, what, needs a pull, why it may float)
    ('TC4427', ['2', '4'], 'TC4427 input', True, 'MCU pin is high-Z in reset / DFU: a floating input could fire a coil'),
    ('NCV8406ASTT3G', ['1'], 'NCV8406A gate', True, 'shifter outputs are disabled until the firmware enables them'),
    ('VND7NV04TR-E', ['1'], 'VND7NV04 input', True, 'shifter outputs are disabled until the firmware enables them'),
    ('ZXMS6004FFTA', ['1'], 'ZXMS6004 input', True, 'shifter outputs are disabled until the firmware enables them'),
    ('74HCT04PW', ['1', '3', '5', '9'], '74HCT04 input', True,
     'MCU pin is high-Z in reset / DFU: the inverter input must sit low so the ignition pull-down stays on'),
    ('SN74LVC4245APWR', ['22'], 'LVC4245 OE', True, 'must disable the drivers while the MCU is in reset'),
    ('SN74LVC4245APWR', [str(i) for i in range(14, 22)], 'LVC4245 B input', False,
     'floats only while OE is high (outputs off): costs supply current only (VERIFICATION minor item)'),
    ('SN65HVD230DR', ['1'], 'SN65HVD230 D', False, 'datasheet: D open -> bus recessive'),
    ('TCAN1042VDRQ1', ['1'], 'TCAN1042 TXD', False, 'datasheet: internal pull-up to VIO, TXD open -> bus recessive'),
    ('VND14NV04', ['1'], 'VND14NV04 input', True, 'F103 pin is high-Z in reset / bootloader: heater must stay off'),
    ('LM2903DR', ['2', '3', '5', '6'], 'LM2903 input', True, 'unused VR channel must sit at a defined level'),
    ('LMV321IDBVR', ['1', '3'], 'LMV321 input', True, 'knock amp bias'),
    ('STM32F407VGT6', ['94', '37'], 'F407 BOOT0/BOOT1', True, 'boot mode'),
    ('STM32F103C8T6', ['44', '20'], 'F103 BOOT0/BOOT1', True, 'boot mode (BOOT0 is driven by the F407 PD10, high-Z in reset)'),
]


def floating_inputs(sysm, year):
    for val, pads, what, need, why in FLOAT_INPUTS:
        for p in sysm.parts:
            if p['value'] != val or not p['fitted']:
                continue
            for k in pads:
                net = p['pads'].get(k, '')
                if not net:
                    row('FAIL', 'nc-pins', year, f'{p["ref"]}.{k} {what}: not connected')
                    continue
                if net in RAILS:
                    row('OK', 'nc-pins', year, f'{p["ref"]}.{k} {what}: tied to {net}')
                    continue
                pulls = []
                for q in sysm.parts:
                    if q['ref'][0] in 'R' and q['fitted'] and net in q['pads'].values():
                        others = [n for kk, n in q['pads'].items() if n != net and n]
                        if q['value'] == '4x10k':
                            # resistor array: element i is pad i <-> pad 9-i
                            kk = [x for x, n in q['pads'].items() if n == net][0]
                            others = [q['pads'].get(str(9 - int(kk)), '')]
                        pulls += [f'{q["ref"]} {q["value"]} to {o}' for o in others if o in RAILS]
                if not pulls:
                    # pull through one series resistor (e.g. VND14NV04 gate: R125 1k -> WB_HTR_PWM -> R126 1k -> GND)
                    for q in sysm.parts:
                        if q['ref'][0] == 'R' and q['fitted'] and len(q['pads']) == 2 and net in q['pads'].values():
                            n2 = [n for n in q['pads'].values() if n != net][0]
                            for q2 in sysm.parts:
                                if q2 is not q and q2['ref'][0] == 'R' and len(q2['pads']) == 2 and n2 in q2['pads'].values():
                                    o = [n for n in q2['pads'].values() if n != n2][0]
                                    if o in RAILS:
                                        pulls.append(f'{q["ref"]} {q["value"]} + {q2["ref"]} {q2["value"]} to {o}')
                if not pulls:
                    # driven by an always-enabled CMOS output (74HCT04 on +5V, no output enable)
                    for q in sysm.parts:
                        if q['value'] == '74HCT04PW' and q['fitted']:
                            for kk, n in q['pads'].items():
                                if n == net and kk in ('2', '4', '6', '8', '10', '12'):
                                    pulls.append(f'driven by {q["ref"]}.{kk} (74HCT04 push-pull output, always enabled)')
                if pulls or not need:
                    row('OK', 'nc-pins', year, f'{p["ref"]}.{k} {what} ({net}): ' +
                        (', '.join(pulls) if pulls else f'no pull; {why}'))
                else:
                    row('FAIL', 'nc-pins', year, f'{p["ref"]}.{k} {what} ({net}): no pull resistor to a rail ({why})')


def power_paths(sysm, year, fw, board_fw):
    """the supply chain: which cavities power the logic rail, wake on ignition, main-relay hold, sensor 5 V, grounds"""
    vb = sorted(c for c, n in sysm.cavity.items() if n == 'VBAT_IN')
    vi = sorted(c for c, n in sysm.cavity.items() if n == 'VIGN_IN' and c not in year_unwired(year))
    gn = sorted(c for c, n in sysm.cavity.items() if n == 'GND')
    dc = build_dc(sysm, year, fw, board_fw)
    V = dc.solve()
    ok = V.get('+12V', 0) > 12.5 and abs(V.get('+5V', 0) - 5) < 0.05 and abs(V.get('+3V3', 0) - 3.3) < 0.05
    row('OK' if ok and vb and gn else 'FAIL', 'power', year,
        f'key on: VBAT_IN {vb} -> D7 -> F1 -> +12V {V.get("+12V", 0):.2f} V -> buck +5V {V.get("+5V", 0):.2f} V / '
        f'LDO +3V3 {V.get("+3V3", 0):.2f} V; grounds {gn}')
    # sensor 5 V: two TLS115 trackers. V5_SENS -> on-board MAP only; V5_EXT -> harness 5 V cavities and AUX J5-14
    j5 = sysm.by_ref.get('M.J5', {}).get('pads', {})
    mapu = sysm.by_ref.get('M.U2', {}).get('pads', {})
    want = {'V5_SENS': ('MAP sensor M.U2', False), 'V5_EXT': ('harness cavities + AUX J5', True)}
    for rail, (what, harness) in want.items():
        cav = sorted(c for c, n in sysm.cavity.items() if n == rail and c not in year_unwired(year))
        aux = sorted(f'J5-{k}' for k, n in j5.items() if n == rail)
        mp = sorted(f'U2.{k}' for k, n in mapu.items() if n == rail)
        src = [p['ref'] for p in sysm.parts if p['value'] == 'TLS115B0EJ' and p['pads'].get('1') == rail]
        v = V.get(rail)
        bad = []
        if v is None or abs(v - 5) > 0.1:
            bad.append(f'rail at {v if v is None else round(v, 2)} V')
        if not src:
            bad.append('no TLS115 drives it')
        if harness and not cav:
            bad.append('reaches no harness cavity')
        if harness and 'J5-14' not in aux:
            bad.append('not on AUX J5-14')
        if not harness and (cav or aux):
            bad.append(f'also on {cav + aux}: the MAP supply should stay on the board')
        if not harness and not mp:
            bad.append('does not reach the MAP sensor')
        row('FAIL' if bad else 'OK', 'power', year,
            f'sensor 5 V {rail} ({V5_RAILS[rail]}; {", ".join(src) or "-"}): {v if v is None else f"{v:.2f}"} V -> '
            f'{", ".join(cav + aux + mp) or "-"} (expected: {what})' + (f'  !! {"; ".join(bad)}' if bad else ''))
    if vi:
        dc = build_dc(sysm, year, fw, board_fw, open_cav=vb[0] if len(vb) == 1 else None)
        V = dc.solve()
        hold = fw.get('mainRelay')
        relay = [c for c, n in sysm.cavity.items() if n == 'OUT_MAINRLY' and c not in year_unwired(year)]
        txt = f'ignition wake: {vi} -> D8 -> F1: +12V {V["+12V"]:.2f} V with the main relay open'
        if hold:
            txt += f'; firmware holds the main relay on {relay} ({hold}) and reads the key on PA2'
        row('OK' if V['+12V'] > 12 else 'FAIL', 'power', year, txt)
    elif fw.get('mainRelay'):
        row('FAIL', 'power', year, 'firmware drives a main relay but no ignition wake cavity is wired')
    else:
        row('OK', 'power', year, 'key-switched main relay (no ECU main-relay output, no ignition sense): the ECU runs '
            'only while the car powers VBAT_IN, and rusEFI uses battery voltage as the key')


def unconnected_pins(sysm, year):
    # the rules don't depend on the year; run them once
    pad_counts = {'STM32F407VGT6': 100, 'STM32F103C8T6': 48, 'TC4427': 8, 'SN65HVD230DR': 8, 'TLS115B0EJ': 9,
                  'LMR14020': 9, 'SN74LVC4245APWR': 24, 'ULN2003AD': 16, 'LM2903DR': 8, 'LMV321IDBVR': 5,
                  'MCP6004': 14, 'AD8628': 5, 'REF3033': 3, 'AMS1117-3.3': 3, 'LDL1117S33R': 3, 'NCV8406ASTT3G': 4, 'VND14NV04': 3,
                  'MPX5700AP': 6, 'USBLC6-2SC6': 6, 'TCAN1042VDRQ1': 8, '74HCT04PW': 14, 'VND7NV04TR-E': 3,
                  'ZXMS6004FFTA': 3, 'TL431AIDBZR': 3, 'BCP53-16': 4}
    for p in sysm.parts:
        val = p['value']
        if val not in pad_counts or not p['fitted']:
            continue
        floating = [k for k in [str(i) for i in range(1, pad_counts[val] + 1)] if not p['pads'].get(k)]
        bad = []
        for k in floating:
            rule = NC_OK.get(val)
            if isinstance(rule, str):
                if mcu_pin_info('U1' if val.startswith('STM32F4') else 'U102', k)[1] == 'PWR':
                    bad.append(f'{k} (power pin)')
                continue
            if not rule or k not in rule:
                bad.append(k)
        for k, (want, why) in MUST_TIE.get(val, {}).items():
            got = p['pads'].get(k, '')
            if got != want:
                bad.append(f'{k} {why}: on {got or "nothing"}, needs {want}')
        # pull resistors required on boot pins
        for (v, net), rail in PULL_REQ.items():
            if v == val and net in p['pads'].values():
                pulls = [q for q in sysm.parts if q['ref'][0] == 'R' and set(q['pads'].values()) == {net, rail}]
                if not pulls:
                    bad.append(f'{net} has no pull to {rail}')
        if bad:
            row('FAIL', 'nc-pins', year, f'{p["ref"]} {val}: ' + '; '.join(bad))
        else:
            note = ''
            if floating:
                rule = NC_OK.get(val)
                note = f' floating: {len(floating)} pads ({rule if isinstance(rule, str) else ", ".join(f"{k}: {rule[k]}" for k in floating)})'
            row('OK', 'nc-pins', year, f'{p["ref"]} {val}: required ties present;{note or " no unconnected pads"}')


# ------------------------------------------------------------------------------------------------------------------
# DC network solver: resistors + piecewise-linear diodes (forward Vf/Ron, optional reverse breakdown Vbr), MNA
# ------------------------------------------------------------------------------------------------------------------
class DC:
    def __init__(self):
        self.R, self.D = [], []
        self.fixed = {'GND': 0.0}

    def r(self, a, b, ohm, tag=None):
        if a and b and a != b:
            self.R.append((a, b, max(ohm, 1e-3), tag))

    def d(self, a, k, vf=0.6, ron=1.0, vbr=None, tag=None):
        if a and k and a != k:
            self.D.append((a, k, vf, ron, vbr, tag))

    def fix(self, node, volts):
        self.fixed[node] = volts

    def src(self, node, volts, ron, tag):
        """a stiff rail: holds its voltage either way; the current it would have to sink is reported"""
        s = '_S:' + node
        self.fix(s, volts)
        self.r(s, node, ron, tag=tag)

    def src_only(self, node, volts, ron, tag):
        """a regulator that can source but not sink (ideal diode from a fixed source)"""
        s = '_S:' + node
        self.fix(s, volts)
        self.d(s, node, 0.0, ron, tag=tag)

    def solve(self):
        nodes = set(self.fixed)
        for a, b, *_ in self.R:
            nodes.update((a, b))
        for a, k, *_ in self.D:
            nodes.update((a, k))
        free = sorted(n for n in nodes if n not in self.fixed)
        idx = {n: i for i, n in enumerate(free)}
        n = len(free)
        st = [0] * len(self.D)          # 0 off, 1 forward, -1 breakdown
        V = {}
        for it in range(400):
            G = np.zeros((n, n))
            b = np.zeros(n)
            G[np.diag_indices(n)] += 1e-9

            def stamp(a, k, g, c):
                # current a -> k = g (Va - Vk) + c
                ia, ik = idx.get(a), idx.get(k)
                va, vk = self.fixed.get(a), self.fixed.get(k)
                if ia is not None:
                    G[ia, ia] += g
                    b[ia] -= c
                    if ik is not None:
                        G[ia, ik] -= g
                    else:
                        b[ia] += g * vk
                if ik is not None:
                    G[ik, ik] += g
                    b[ik] += c
                    if ia is not None:
                        G[ik, ia] -= g
                    else:
                        b[ik] += g * va
            for a, k_, ohm, _t in self.R:
                stamp(a, k_, 1.0 / ohm, 0.0)
            for i, (a, k_, vf, ron, vbr, _t) in enumerate(self.D):
                g = 1.0 / ron
                if st[i] == 1:
                    stamp(a, k_, g, -g * vf)
                elif st[i] == -1:
                    stamp(a, k_, g, g * vbr)
                else:
                    stamp(a, k_, 1e-9, 0.0)
            x = np.linalg.solve(G, b)
            V = dict(self.fixed)
            V.update({nn: x[i] for nn, i in idx.items()})
            changes = []
            for i, (a, k_, vf, ron, vbr, _t) in enumerate(self.D):
                v = V[a] - V[k_]
                if st[i] == 1 and v < vf - 1e-9:
                    changes.append((vf - v, i, 0))
                elif st[i] == -1 and v > -vbr + 1e-9:
                    changes.append((v + vbr, i, 0))
                elif st[i] == 0:
                    if v > vf + 1e-6:
                        changes.append((v - vf, i, 1))
                    elif vbr is not None and v < -vbr - 1e-6:
                        changes.append((-vbr - v, i, -1))
            if not changes:
                break
            if it < 30:
                for _e, i, s in changes:
                    st[i] = s
            else:   # damp: flip the worst offender only
                _e, i, s = max(changes)
                st[i] = s
        self.V, self.st = V, st
        return V

    def i_r(self, e):
        a, b, ohm, _ = e
        return (self.V[a] - self.V[b]) / ohm

    def i_d(self, i):
        a, k, vf, ron, vbr, _ = self.D[i]
        v = self.V[a] - self.V[k]
        if self.st[i] == 1:
            return (v - vf) / ron
        if self.st[i] == -1:
            return (v + vbr) / ron
        return 0.0


# ------------------------------------------------------------------------------------------------------------------
# models of the parts
# ------------------------------------------------------------------------------------------------------------------
def ohms(v):
    v = v.replace('R', '').replace('ohm', '')
    mult = {'k': 1e3, 'M': 1e6}
    if v and v[-1] in mult:
        return float(v[:-1]) * mult[v[-1]]
    return float(v) if v else 0.0


def r_rating(fp):
    for key, w in (('0402', 0.0625), ('0603', 0.1), ('0805', 0.125), ('1206', 0.25), ('2512', 1.0)):
        if key in fp:
            return w
    return 0.1


DIODES = {  # value -> (vf, ron, vbr, steady-state rating text, max continuous A)
    'SMCJ30A': (0.8, 0.05, 33.3, 'SMC TVS 1500 W peak', 3.0), 'SMAJ33A': (0.8, 0.05, 36.7, 'SMA TVS 400 W peak', 1.0),
    'SMCJ40A': (0.8, 0.05, 44.4, 'SMC TVS 1500 W peak', 3.0), 'SS34': (0.45, 0.05, 40, 'SS34 3 A', 3.0),
    'B5819W': (0.45, 0.1, 40, 'B5819W 1 A', 1.0), 'B360A': (0.5, 0.05, 60, 'B360A 3 A', 3.0),
    '1N4148WS': (0.7, 1.0, 75, '1N4148WS 150 mA', 0.15),
    'BAT54WS': (0.3, 10.0, 30, 'BAT54WS 200 mA', 0.2),        # rev 0.7 analog-input / VDDA clamps
    'RED': (1.9, 10, None, 'LED', 0.02), 'YELLOW': (1.9, 10, None, 'LED', 0.02), 'GREEN': (2.6, 10, None, 'LED', 0.02),
    'BLUE': (2.8, 10, None, 'LED', 0.02),
}
INDUCT = {'L1': 0.3, 'L2': 0.067, 'FB1': 0.15}
FUSES = {'F1': (0.5, 0.5, 1.0), 'F2': (1.6, 0.1, 0.25),   # F2 nSMD010 (LSU VM wire): 0.1 A hold, 0.25 A trip
         'M.F1': (0.04, 3.0, 5.0), 'M.F2': (0.07, 2.0, 3.5), 'M.F3': (0.07, 2.0, 3.5),
         'M.F4': (0.5, 0.5, 1.0)}    # ref -> (ohm, hold A, trip A)
# low-side switches: value -> (pad in, drain, source, Ron, clamp V, current limit A, severity above it, text)
LOWSIDE = {
    'NCV8406ASTT3G': ('1', '2', '3', 0.21, 60.0, 2.5, 'OK', 'NCV8406A body diode / 60 V clamp'),
    'VND14NV04': ('1', '2', '3', 0.035, 40.0, 2.5, 'OK', 'VND14NV04 body diode / 40 V clamp'),
    'VND7NV04TR-E': ('1', '2', '3', 0.12, 40.0, 6.0, 'OK', 'VND7NV04 body diode / 40 V clamp'),
    'ZXMS6004FFTA': ('1', '3', '2', 0.5, 60.0, 1.0, 'CHECK', 'ZXMS6004 body diode / 60 V clamp'),
}
SHUNT_P_MAX = 1.0      # W, BCP53 in SOT-223 on this board's copper (assumed; datasheet 0.65-1.35 W by pad area)
OPAMP = {'MCP6004': (['2', '3', '5', '6', '9', '10', '12', '13'], ['1', '7', '8', '14'], 2e-3, 30e-3, '+3V3'),
         'AD8628': (['3', '4'], ['1'], 5e-3, 30e-3, '+3V3'),        # input limit assumed (not in our notes)
         'LMV321IDBVR': (['1', '3'], ['4'], 10e-3, 40e-3, '+3V3')}
VCAR = 14.4


def base_net(net):
    return net[2:] if net.startswith('M:') else net


def build_dc(sysm, year, fw, board_fw, vcar=VCAR, states=None, fault=None, jp1='EXT', open_cav=None, sweep=None,
             tripped=()):
    """the whole ECU (daughterboard + this year's motherboard) and the car around it, as a DC network.
    states: {'U5.16': 'on', 'U6.7': 'high', 'Q1': 'on', ...}; fault: (net, 'GND'|'BAT'); open_cav: cavity unplugged;
    sweep: {cavity: ('src', volts, ohm) | ('res', ohm) | ('open',)} replaces that cavity's car model."""
    states = states or {}
    dc = DC()
    dc.fix('CAR', vcar)
    dc.fix('_HALF', 1.65)
    dc.fix('_MAP', 0.85)
    out_ports = {p for f, p in fw.items() if f in FW_OUTPUTS} | {board_fw[k] for k in board_fw if k.startswith('led')} \
        | {board_fw['wbo BOOT0'], 'PB13', 'PC6', 'PD8'}
    for p in sysm.parts:
        ref, val, pads, fp = p['ref'], p['value'], p['pads'], p['fp']
        base = ref.split('.')[-1]
        kind = re.match(r'[A-Z]+', base).group(0)
        if not p['fitted'] and base != 'JP1':
            continue
        g = lambda k: pads.get(k, '')
        if base == 'JP1':
            if jp1 == 'EXT':
                dc.r(g('2'), g('3'), 0.01)
            else:
                dc.r(g('1'), g('2'), 0.01)
        elif kind == 'R' and len(pads) == 2:
            v = ohms(val)
            dc.r(g('1'), g('2'), v if v > 0 else 0.01, tag=('R', ref, v, r_rating(fp)) if v > 0 else None)
        elif kind == 'RN':
            for i in range(1, 5):
                dc.r(g(str(i)), g(str(9 - i)), 10e3, tag=('R', f'{ref}.{i}', 10e3, 0.0625))
        elif kind in ('L', 'FB') and ref in INDUCT:
            dc.r(g('1'), g('2'), INDUCT[ref])
        elif ref in FUSES:
            if ref in tripped:
                continue
            o, hold, trip = FUSES[ref]
            dc.r(g('1'), g('2'), o, tag=('F', ref, hold, trip))
        elif kind == 'D' and val in DIODES:
            vf, ron, vbr, txt, imax = DIODES[val]
            dc.d(g('2'), g('1'), vf, ron, vbr, tag=('D', ref, val, imax))
        elif kind == 'D' and val == 'BAT54S':
            # series pair: pad 1 = anode of the low diode, pad 2 = cathode of the high diode, pad 3 = middle
            dc.d(g('1'), g('3'), 0.35, 2.0, 30, tag=('D', ref + '-lo', val, 0.2))
            dc.d(g('3'), g('2'), 0.35, 2.0, 30, tag=('D', ref + '-hi', val, 0.2))
        elif kind == 'D' and val == 'BAT54A':
            # common anode (pad 3), cathodes pads 1 and 2
            dc.d(g('3'), g('1'), 0.35, 2.0, 30, tag=('D', ref + '-1', val, 0.2))
            dc.d(g('3'), g('2'), 0.35, 2.0, 30, tag=('D', ref + '-2', val, 0.2))
        elif val in LOWSIDE:
            _i, dr, so, ron, vcl, ilim, sev_lim, txt = LOWSIDE[val]
            dc.d(g(so), g(dr), 0.7, 0.05, vcl, tag=('CLAMP', ref, txt))
            if states.get(ref) == 'on':
                dc.r(g(dr), g(so), ron, tag=('NCV_ON', ref, val, ron, ilim, sev_lim))
        elif val == '74HCT04PW':
            for i_ in ('1', '3', '5', '9', '11', '13'):
                dc.d(g(i_), g('14'), 0.7, 10)
                dc.d('GND', g(i_), 0.7, 10)
        elif val == 'TL431AIDBZR':
            pass        # modelled with its pass transistor (BCP53-16 below) as one shunt element
        elif val == 'BCP53-16':
            # TL431 + PNP shunt clamp: emitter = clamped rail, base = TL431 cathode; threshold from the divider on REF
            rail_, base_ = g('3'), g('1')
            tl = [q for q in sysm.parts if q['value'] == 'TL431AIDBZR' and q['fitted'] and q['pads'].get('1') == base_]
            vth = None
            if tl:
                ref_n = tl[0]['pads'].get('2')
                top = [ohms(q['value']) for q in sysm.parts if q['ref'][0] == 'R' and q['fitted']
                       and set(q['pads'].values()) == {ref_n, rail_}]
                bot = [ohms(q['value']) for q in sysm.parts if q['ref'][0] == 'R' and q['fitted']
                       and set(q['pads'].values()) == {ref_n, 'GND'}]
                if top and bot:
                    vth = 2.495 * (1 + top[0] / bot[0])
            if vth:
                dc.d(rail_, 'GND', vth, 0.04, tag=('SHUNT', f'{rail_} shunt ({tl[0]["ref"]} TL431 + {ref} BCP53)', vth))
        elif val == 'ULN2003AD':
            for i in range(7):
                inp, out = g(str(1 + i)), g(str(16 - i))
                bn = f'{ref}.b{i}'
                dc.r(inp, bn, 2700)
                dc.d(bn, 'GND', 1.3, 100)
                dc.d(out, g('9'), 0.8, 1.0, tag=('ULN_CLAMP', f'{ref}.{16 - i}'))
                dc.d('GND', out, 0.7, 1.0, tag=('ULN_SUB', f'{ref}.{16 - i}'))
                if states.get(f'{ref}.{16 - i}') == 'on':
                    dc.d(out, 'GND', 0.9, 1.0, tag=('ULN_ON', f'{ref}.{16 - i}'))
        elif val == 'TC4427':
            for o in ('5', '7'):
                out = g(o)
                dc.d(out, g('6'), 0.7, 1.0, tag=('TC_BODY', f'{ref}.{o}'))
                dc.d('GND', out, 0.7, 1.0, tag=('TC_BODY', f'{ref}.{o}'))
                if states.get(f'{ref}.{o}') == 'high':
                    dc.r(out, g('6'), 7.0, tag=('TC_OUT', f'{ref}.{o}'))
                else:
                    dc.r(out, 'GND', 7.0, tag=('TC_OUT', f'{ref}.{o}'))
            for i_ in ('2', '4'):
                dc.d(g(i_), g('6'), 0.7, 10)
                dc.d('GND', g(i_), 0.7, 10)
        elif val == 'SN74LVC4245APWR':
            for k in range(3, 11):
                a = g(str(k))
                dc.d(a, g('1'), 0.7, 10)
                dc.d('GND', a, 0.7, 10)
                dc.r(a, 'GND', 25)          # enabled, driving low (MCU control pins low)
            for k in range(14, 22):
                dc.d(g(str(k)), g('23'), 0.7, 10)
                dc.d('GND', g(str(k)), 0.7, 10)
        elif val == 'LM2903DR':
            for k in ('1', '2', '3', '5', '6', '7'):
                dc.d('GND', g(k), 0.6, 10)
        elif val in OPAMP:
            ins, outs, lim_in, lim_out, vcc = OPAMP[val]
            for k in ins:
                dc.d(g(k), vcc, 0.6, 10, tag=('OA_IN', f'{ref}.{k}', val, lim_in))
                dc.d('GND', g(k), 0.6, 10, tag=('OA_IN', f'{ref}.{k}', val, lim_in))
            for k in outs:
                dc.r(g(k), '_HALF', 72, tag=('OA_OUT', f'{ref}.{k}', val, lim_out))
                dc.d(g(k), vcc, 0.6, 2, tag=('OA_OUT', f'{ref}.{k}', val, lim_out))
                dc.d('GND', g(k), 0.6, 2, tag=('OA_OUT', f'{ref}.{k}', val, lim_out))
        elif val == 'SN65HVD230DR':
            dc.r(g('4'), '+3V3', 100)
        elif val == 'TCAN1042VDRQ1':
            dc.r(g('4'), g('5'), 100)                # RXD recessive high at VIO; bus pins +-58 V, not loaded
        elif val == 'TLS115B0EJ':
            dc.src_only(g('1'), 5.0, 0.5, tag=('SRC', f'{g("1")} ({ref} TLS115)', g('1')))
        elif val in ('AMS1117-3.3', 'LDL1117S33R'):
            if any(q['value'] == 'BCP53-16' and q['fitted'] and q['pads'].get('3') == g('2') for q in sysm.parts):
                # source-only LDO into its minimum load; the shunt clamp takes what is pushed in beyond that
                dc.src_only(g('2'), 3.3, 0.01, tag=('LDO', f'{g("2")} (U4 {val[:7]})'))
                dc.r(g('2'), 'GND', 3.3 / 0.05)      # load >= 50 mA (MCUs, transceivers)
            else:
                dc.src(g('2'), 3.3, 0.01, tag=('RAIL', f'+3V3 (U4 {val[:7]})', 0.05))   # load >= 50 mA
        elif val == 'LMR14020':
            dc.src('+5V', 5.0, 0.01, tag=('RAIL', '+5V (U2 buck)', 0.06))          # load >= 60 mA (LDO, drivers)
            dc.r(g('2'), 'GND', 100)                 # about 2 W drawn from +12V_F
        elif val == 'REF3033':
            dc.src(g('2'), 3.3, 0.1, tag=('RAIL', 'WB_VDDA (U103 REF3033)', 0.003))
        elif val == 'MPX5700AP':
            dc.r(g('3'), g('2'), 714)                # 7 mA supply current
            dc.r(g('1'), '_MAP', 100)
        elif ref in ('U1', 'U102'):
            for k, net in pads.items():
                if not net:
                    continue
                name, typ = mcu_pin_info(ref, k)
                if typ == 'PWR':
                    continue
                vdd = '+3V3A' if typ == 'TTa' else '+3V3'
                dc.d('GND', net, 0.5, 10, tag=('MCU-', ref, k))
                if typ in ('TTa', 'IO'):
                    dc.d(net, vdd, 0.5, 10, tag=('MCU+', ref, k))
                if ref == 'U1' and name in out_ports:
                    dc.r(net, '+3V3' if states.get(f'U1.{name}') == 'high' else 'GND', 40, tag=('MCU_OUT', ref, k))
                if ref == 'U102' and name == 'PB10':
                    dc.r(net, 'GND', 40)
                if ref == 'U102' and name == 'PA6':
                    dc.r(net, '_HALF', 40)
    car_models(dc, sysm, year, open_cav, sweep or {})
    if fault:
        net, kind = fault
        dc.r(net, 'GND' if kind == 'GND' else 'CAR', 0.02, tag=('FAULT', net, kind))
    return dc


def year_unwired(year):
    return {'3H', '4S'} if year == '2001-02' else set()


def car_models(dc, sysm, year, open_cav, sweep):
    """what the car connects to each cavity (assumed typical loads, see MODEL NOTES)"""
    canon = sysm.canon
    iac_feed = canon.get('M:IAC_12V', 'CAR')
    ocv_feed = canon.get('M:OCV_12V', 'CAR')
    for key, s_ in sweep.items():
        if key.startswith('NET:'):
            dc.fix('_SW:' + key, s_[1])
            dc.r(canon.get(key[4:], key[4:]), '_SW:' + key, s_[2])
    for cav, net in sysm.cavity.items():
        if not net or cav == open_cav or cav in year_unwired(year):
            continue
        b = base_net(net)
        if cav in sweep:
            s = sweep[cav]
            if s[0] == 'src':
                dc.fix('_SW:' + cav, s[1])
                dc.r(net, '_SW:' + cav, s[2])
            elif s[0] == 'res':
                dc.r(net, 'GND', s[1])
            continue
        n_inj = 2 if (year == '1989-93' and b in ('OUT_INJ1', 'OUT_INJ2')) else 1
        if b == 'VBAT_IN':
            dc.r('CAR', net, 0.05, tag=('CARSRC', cav))
        elif b == 'VIGN_IN':
            dc.r('CAR', net, 0.2, tag=('CARSRC', cav))
        elif b in ('OUT_FP', 'OUT_FAN', 'OUT_AC', 'OUT_LS7'):
            dc.r('CAR', net, 80)
        elif b == 'OUT_MAINRLY':
            dc.r('CAR', net, 30 if year == '1999-2000' else 80)
        elif b == 'OUT_CEL':
            dc.r('CAR', net, 50)
        elif b == 'OUT_TACH':
            dc.r('CAR', net, 1000)
        elif b.startswith('OUT_IGN'):
            dc.r(net, 'GND', 2000)
        elif b.startswith('OUT_INJ'):
            dc.r('CAR', net, 13.0 / n_inj)
        elif b == 'OUT_IACV':
            dc.r(iac_feed, net, 11)
        elif b == 'OUT_VVT':
            if year in ('1989-93', '1994-95'):
                dc.r('CAR', net, 30)
            elif year in ('1996-97', '1999-2000'):
                dc.r('CAR', net, 6)
            else:
                dc.r(ocv_feed, net, 8)
        elif b == 'OUT_ALT':
            dc.r('CAR', net, 30 if year == '1994-95' else 4)
        elif b == 'IN_TPS':
            dc.fix('_TPS', 2.5)
            dc.r(net, '_TPS', 1250)
        elif b == 'IN_AUX3':
            dc.fix('_MAF', 2.5)
            dc.r(net, '_MAF', 1000)
        elif b in ('IN_AUX1', 'IN_AUX2'):
            dc.fix('_O2', 0.45)
            dc.r(net, '_O2', 10e3)
        elif b in ('IN_CLT', 'HARN_IAT'):
            dc.r(net, 'GND', 2500)
        elif b in V5_RAILS:
            dc.r(net, 'GND', 5000)
    # on-board sensor connectors: external IAT thermistor on J3 (JP1 on EXT)
    iat_ext = sysm.canon.get('M:IAT_EXT')
    if iat_ext and 'J3' not in sweep:
        dc.r(iat_ext, 'GND', 2500)


# ------------------------------------------------------------------------------------------------------------------
# section 2: electrical compatibility at each MCU pin
# ------------------------------------------------------------------------------------------------------------------
ANALOG_NETS_F103 = {'WB_UN_SENSE', 'LSU_VM', 'WB_IP_SENSE', 'WB_VM', 'WB_VBAT_DIV'}


def is_analog(ref, net):
    return net.startswith('AN_') or (ref == 'U102' and net in ANALOG_NETS_F103)


def sweeps_for(base):
    """normal operating range of each harness input: list of (label, car model)"""
    if base in ('IN_TPS', 'IN_AUX1', 'IN_AUX2', 'IN_AUX3'):
        return [('0 V', ('src', 0.0, 1.0)), ('5 V', ('src', 5.0, 1.0))]
    if base in ('IN_CLT', 'HARN_IAT'):
        return [('thermistor 50 ohm', ('res', 50.0)), ('open / -40 C', ('open',))]
    if base.startswith('IN_HALL'):
        return [('sensor on (60 ohm)', ('res', 60.0)), ('sensor off', ('open',))]
    if base.startswith('IN_SW'):
        return [('switch open', ('open',)), ('9 V (cranking)', ('src', 9.0, 1.0)), ('16 V', ('src', 16.0, 1.0))]
    if base == 'VBAT_IN':
        return [('9 V', 'vcar9'), ('16 V', 'vcar16')]
    if base == 'VIGN_IN':
        return [('key off', ('open',)), ('16 V', ('src', 16.0, 0.2))]
    return []


def electrical(systems, fws, board_fw):
    seen = {}       # (ref, pad) -> list of (year, label, volts, cavity)
    for year, sysm in systems.items():
        fw = fws[year]
        g, blocked = graph(sysm)
        for cav, net in sorted(sysm.cavity.items()):
            if not net or cav in year_unwired(year):
                continue
            b = base_net(net)
            sw = sweeps_for(b)
            if not sw:
                continue
            ends = trace(sysm, g, blocked, net)
            pins = [(e[1], e[2]) for e in ends if e[0] == 'mcu']
            if not pins:
                continue
            for lab, model in sw:
                if model in ('vcar9', 'vcar16'):
                    dc = build_dc(sysm, year, fw, board_fw, vcar=9.0 if model == 'vcar9' else 16.0)
                else:
                    dc = build_dc(sysm, year, fw, board_fw, sweep={cav: model})
                V = dc.solve()
                for ref, pad in pins:
                    net_p = sysm.by_ref[ref]['pads'][pad]
                    seen.setdefault((ref, pad), []).append((year, f'{cav} {lab}', V[net_p], cav))
        # supply sense behind the +12V rail, the on-board MAP sensor and the AUX analog input
        pa1 = str(F407_PIN['PA1'])
        for lab, vc in (('9 V', 9.0), ('16 V', 16.0)):
            dc = build_dc(sysm, year, fw, board_fw, vcar=vc)
            V = dc.solve()
            seen.setdefault(('U1', pa1), []).append((year, f'battery {lab}', V['AN_VBATT'], ''))
        for net, sw in (('IN_MAP', [('MPX5700AP 0.2 V', 0.2), ('4.7 V (700 kPa)', 4.7)]),
                        ('IN_AFR', [('AUX 0 V', 0.0), ('AUX 5 V', 5.0)])):
            for lab, v in sw:
                dc = build_dc(sysm, year, fw, board_fw, sweep={'NET:' + net: ('src', v, 1.0)})
                V = dc.solve()
                for ref, pad in sysm.mcu_pins('AN_' + net[3:]):
                    seen.setdefault((ref, pad), []).append((year, lab, V['AN_' + net[3:]], ''))
    # analog MCU pins with no harness range to sweep: their operating point
    sysm0 = systems[next(iter(systems))]
    dc0 = build_dc(sysm0, next(iter(systems)), fws[next(iter(systems))], board_fw)
    V0 = dc0.solve()
    for ref, pad, net in mcu_gpio(sysm0):
        if (ref, pad) not in seen and (is_analog(ref, net) or net == 'AN_KNOCK'):
            seen[(ref, pad)] = [('all', 'operating point (sensor open)', V0[net], '')]
    # rows per MCU pin
    for (ref, pad), obs in sorted(seen.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        name, typ = mcu_pin_info(ref, pad)
        net = systems[next(iter(systems))].by_ref[ref]['pads'][pad]
        vs = [o[2] for o in obs]
        lo, hi = min(vs), max(vs)
        lo_o, hi_o = obs[vs.index(lo)], obs[vs.index(hi)]
        analog = is_analog(ref, net)
        lim = LIM_FT_V if typ == 'FT' else LIM_NONFT_V
        status, notes = 'OK', []
        if hi > lim:
            status = 'FAIL'
            notes.append(f'above abs max {lim:.1f} V')
        elif analog and hi > VDD + 0.05:
            status = 'CHECK'
            notes.append('above VDDA: ADC clips' + (' (FT pin in analog mode)' if typ == 'FT' else ''))
        elif typ == 'FT' and hi > FT_OPER_MAX:
            status = 'CHECK'
            notes.append(f'above the {FT_OPER_MAX} V FT operating range')
        elif typ != 'FT' and hi > VDD + 0.3:
            status = 'CHECK'
            notes.append('above VDD + 0.3 V on a non-FT pin (clamp conducts)')
        if lo < -0.3:
            status = max(status, 'CHECK', key=SEV.get)
            notes.append('below -0.3 V')
        if not analog and ref == 'U1':
            # digital levels: every 'high' observation >= VIH, every 'low' <= VIL
            highs = [o for o in obs if o[2] > VIL]
            mid = [o for o in highs if o[2] < VIH]
            if mid:
                status = max(status, 'CHECK', key=SEV.get)
                notes.append('between VIL and VIH: ' + ', '.join(f'{o[1]} ({o[0]}) {o[2]:.2f} V' for o in mid[:3]))
        years = sorted({o[0] for o in obs})
        row(status, 'electrical', 'all', f'{mcu_label(ref, pad)} {net}: {lo:.2f} V ({lo_o[1]}, {lo_o[0]}) .. '
            f'{hi:.2f} V ({hi_o[1]}, {hi_o[0]}); {"ADC" if analog else "digital"}; years {",".join(years)}'
            + (f'  !! {"; ".join(notes)}' if notes else ''))

    # outputs into inputs and pull-ups: from the daughterboard netlist (same on every year)
    sysm = systems[next(iter(systems))]
    recv = {  # value -> (pads, what, VIH needed at the receiver)
        'ULN2003AD': ([str(i) for i in range(1, 8)], 'ULN2003 input (VI(on) 2.4 V at 200 mA, 2.7 k series: 0.7 mA)', 2.4),
        'TC4427': (['2', '4'], 'TC4427 input (VIH 2.4 V)', 2.4),
        'SN74LVC4245APWR': ([str(i) for i in range(14, 22)], 'LVC4245 B input at VCCB 3.3 V (VIH 2.0 V)', 2.0),
        'SN65HVD230DR': (['1'], 'SN65HVD230 D (VIH 2.0 V)', 2.0),
    }
    for p in sysm.parts:
        if p['value'] in recv:
            pads, what, vih = recv[p['value']]
            for k in pads:
                net = p['pads'].get(k, '')
                drv = [mcu_label(r, kk) for r, kk in sysm.mcu_pins(net)]
                ok = bool(drv) and VDD - 0.4 >= vih
                row('OK' if ok else 'FAIL', 'electrical', 'all', f'{p["ref"]}.{k} {net} <- {", ".join(drv) or "no driver"}: '
                    f'{what}; MCU VOH min {VDD - 0.4:.1f} V')
    # direction of serial / CAN links
    for (ref, pname), (af, d) in AF_DIR.items():
        pad = str((F407_PIN if ref == 'U1' else {v: k for k, v in F103_NAME.items()})[pname])
        net = sysm.by_ref[ref]['pads'].get(pad, '')
        peers = []
        for r, k in sysm.net_pads.get(net, []):
            if (r, k) == (ref, pad):
                continue
            if r in ('U1', 'U102'):
                pn = mcu_pin_info(r, k)[0]
                peers.append((f'{r} {pn}', AF_DIR.get((r, pn), ('?', '?'))[1]))
            elif sysm.by_ref[r]['value'] == 'SN65HVD230DR':
                peers.append((f'{r}.{k}', {'1': 'in', '4': 'out'}.get(k, '?')))
            elif r in ('J2',):
                peers.append((f'J2.{k} (AUX)', 'ext'))
        bad = [p for p in peers if p[1] == d]
        row('FAIL' if bad else 'OK', 'electrical', 'all', f'{ref} {pname} {af} ({d}) on {net} -> '
            + ', '.join(f'{a} ({b})' for a, b in peers))
    # pull-ups / pull-downs on MCU nets
    for ref in ('U1', 'U102'):
        for pad, net in sorted(sysm.by_ref[ref]['pads'].items(), key=lambda kv: int(kv[0])):
            name, typ = mcu_pin_info(ref, pad)
            if typ == 'PWR' or not net:
                continue
            for q in sysm.parts:
                if q['ref'][0] != 'R' or q['board'] != 'D' or len(q['pads']) != 2:
                    continue
                a, b = q['pads'].get('1'), q['pads'].get('2')
                other = b if a == net else a if b == net else None
                lower = [x for x in sysm.parts if x['ref'][0] == 'R' and x['board'] == 'D'
                         and set(x['pads'].values()) == {net, 'GND'}]
                if other in ('+5V', '+12V', 'VBAT_IN', 'V5_SENS') and not lower:
                    sev = 'OK' if typ == 'FT' else 'FAIL'
                    row(sev, 'electrical', 'all', f'{mcu_label(ref, pad)} {net}: pulled up to {other} through {q["ref"]} '
                        f'{q["value"]}' + (' (FT pin, open-drain driver)' if sev == 'OK' else ' on a non-FT pin'))
    # backup-domain pins PC13/PC14 (ULN inputs): 3 mA total through the power switch
    i_tot = sum((VDD - 1.3) / 2700 for pn in ('PC13', 'PC14', 'PC15')
                if sysm.by_ref['U1']['pads'].get(str(F407_PIN[pn]), '').endswith('_CTL'))
    row('OK' if i_tot < 3e-3 else 'FAIL', 'electrical', 'all', f'PC13-PC15 source {i_tot * 1e3:.2f} mA into ULN2003 '
        'inputs (ST: 3 mA total for the backup-domain switch, 2 MHz max)')


# ------------------------------------------------------------------------------------------------------------------
# section 3: faults on every harness cavity
# ------------------------------------------------------------------------------------------------------------------
ULN_OUTS = [str(i) for i in range(10, 17)]
WORST = []      # (severity, magnitude, year, text)


def linked_nets(sysm, net):
    nets = {net}
    changed = True
    while changed:
        changed = False
        for p in sysm.parts:
            if p['fitted'] and p['board'] == 'M' and p['value'] == '0R':
                a, b = p['pads'].get('1'), p['pads'].get('2')
                if (a in nets) != (b in nets):
                    nets |= {a, b}
                    changed = True
    return nets


def driver_states(sysm, net):
    nets = linked_nets(sysm, net)
    # a driver behind a small series resistor (TC4427 -> 100 ohm -> OUT_IGNx) still drives the cavity
    for p in sysm.parts:
        if p['ref'][0] == 'R' and p['board'] == 'D' and len(p['pads']) == 2 and p['fitted']:
            a, b = p['pads'].get('1'), p['pads'].get('2')
            try:
                small = ohms(p['value']) <= 470
            except ValueError:
                small = False
            if small and (a in nets) != (b in nets) and not ({a, b} & RAILS):
                nets |= {a, b}
    on = {}
    for p in sysm.parts:
        for pad, n in p['pads'].items():
            if n not in nets:
                continue
            if p['value'] == 'ULN2003AD' and pad in ULN_OUTS:
                on[f'{p["ref"]}.{pad}'] = 'on'
            elif p['value'] == 'TC4427' and pad in ('5', '7'):
                on[f'{p["ref"]}.{pad}'] = 'high'
            elif p['value'] in ('NCV8406ASTT3G', 'VND14NV04') and pad == '2':
                on[p['ref']] = 'on'
    return [('off', {}), ('on', on)] if on else [('', {})]


def mcu_gpio(sysm):
    out = []
    for ref in ('U1', 'U102'):
        for pad, net in sysm.by_ref[ref]['pads'].items():
            if net and mcu_pin_info(ref, pad)[1] != 'PWR':
                out.append((ref, pad, net))
    return out


SUPPLY_SENSE = {'AN_VBATT', 'AN_VIGN', 'WB_VBAT_DIV'}
POWER_NETS = {'VBAT_IN', 'VIGN_IN', 'M:IAC_12V', 'M:OCV_12V'}


def evaluate(dc, base, sysm, focus, fault_net=None, base_findings=None):
    """-> (severity, findings list [(sev, text, magnitude)], focus readings). Findings already present in the
    baseline (same element, no worse) are dropped, so a 24 V fault only reports what the short adds to a jump start."""
    F = list({f[1]: f for f in _evaluate(dc, base, sysm, focus, fault_net)}.values())
    if base_findings:
        bk = {}
        for f in base_findings:
            bk[re.sub(r'-?[\d.]+', '#', f[1])] = f[2]
        F = [f for f in F if not (re.sub(r'-?[\d.]+', '#', f[1]) in bk
                                  and abs(f[2]) <= abs(bk[re.sub(r'-?[\d.]+', '#', f[1])]) * 1.05 + 1e-9)]
    if any('self-protected' in f[1] or 'ULN2003' in f[1] or 'PTC trips' in f[1] for f in F):
        F = [f for f in F if 'car\'s fuse' not in f[1]]
    sev = max([f[0] for f in F] + ['OK'], key=SEV.get)
    V = dc.V
    reading = ', '.join(f'{mcu_pin_info(r, k)[0]} {V.get(sysm.by_ref[r]["pads"][k], 0):.2f} V' for r, k in focus)
    return sev, F, reading


def _evaluate(dc, base, sysm, focus, fault_net):
    V = dc.V
    F = []
    inj = collections.defaultdict(float)
    for i, e in enumerate(dc.D):
        t = e[5]
        if t and t[0] in ('MCU+', 'MCU-'):
            inj[(t[1], t[2])] += abs(dc.i_d(i))
    total = sum(inj.values())
    for ref, pad, net in mcu_gpio(sysm):
        name, typ = mcu_pin_info(ref, pad)
        v = V.get(net, 0.0)
        lab = f'{"F407" if ref == "U1" else "F103"} {name}'
        lim = LIM_FT_V if typ == 'FT' else LIM_NONFT_V
        if v > lim:
            F.append(('FAIL', f'{lab} ({net}) at {v:.2f} V > {lim:.1f} V abs max ({typ})', v))
        elif typ == 'FT' and is_analog(ref, net) and v > VDD + 0.3:
            F.append(('CHECK', f'{lab} ({net}) at {v:.2f} V: FT pin in analog mode above VDDA', v))
        elif typ == 'FT' and v > FT_OPER_MAX:
            F.append(('CHECK', f'{lab} ({net}) at {v:.2f} V: above FT operating max {FT_OPER_MAX} V', v))
        if inj.get((ref, pad), 0) > LIM_INJ:
            F.append(('FAIL', f'{lab} injected {inj[(ref, pad)] * 1e3:.1f} mA > 5 mA', inj[(ref, pad)] * 1e3))
        elif inj.get((ref, pad), 0) > 0.5e-3:
            F.append(('OK', f'{lab} injects {inj[(ref, pad)] * 1e3:.2f} mA (limit 5)', 0))
    if total > LIM_INJ_TOTAL:
        F.append(('FAIL', f'total injected current {total * 1e3:.1f} mA > 25 mA', total * 1e3))
    oa_r = {}
    for e in dc.R:
        t = e[3]
        if not t:
            continue
        i = dc.i_r(e)
        if t[0] == 'R':
            p = i * i * t[2]
            if p > t[3]:
                F.append(('FAIL', f'{t[1]} ({t[2]:g} ohm, {t[3] * 1e3:.0f} mW) dissipates {p * 1e3:.0f} mW', p / t[3]))
            elif p > 0.7 * t[3]:
                F.append(('CHECK', f'{t[1]} ({t[2]:g} ohm) at {p * 1e3:.0f} mW, {p / t[3] * 100:.0f} % of rating', p / t[3]))
        elif t[0] == 'F':
            if abs(i) > t[3]:
                F.append(('OK', f'{t[1]} PTC trips ({abs(i):.1f} A > {t[3]} A trip)', 0))
            elif abs(i) > t[2]:
                F.append(('CHECK', f'{t[1]} PTC between hold and trip ({abs(i):.2f} A)', 0))
        elif t[0] == 'TC_OUT':
            p = i * i * 7.0
            if p > 0.47 or abs(i) > 0.5:
                F.append(('FAIL', f'TC4427 {t[1]} output {abs(i) * 1e3:.0f} mA, {p:.2f} W in the driver (SOIC-8 0.47 W)', p))
            elif abs(i) > 0.1:
                F.append(('CHECK', f'TC4427 {t[1]} output {abs(i) * 1e3:.0f} mA continuous', p))
        elif t[0] == 'NCV_ON':
            if abs(i) > 2.5:
                F.append(('OK', f'{t[1]} would carry {abs(i):.0f} A: current limit + thermal shutdown (self-protected)', 0))
        elif t[0] == 'FAULT' or t[0] == 'CARSRC':
            if abs(i) > 20:
                F.append(('OK', f'{abs(i):.0f} A from the car: the car\'s fuse blows', 0))
        elif t[0] == 'OA_OUT':
            oa_r[(t[0], t[1], t[2], t[3])] = abs(i)
        elif t[0] == 'RAIL':
            if -i > t[2]:
                F.append(('FAIL' if t[1].startswith('+3V3') or 'VDDA' in t[1] else 'CHECK',
                          f'{t[1]} back-fed with {-i * 1e3:.0f} mA, more than its {t[2] * 1e3:.0f} mA load: the rail rises', -i))
    oa = collections.defaultdict(float)
    for i, e in enumerate(dc.D):
        t = e[5]
        if not t:
            continue
        cur = dc.i_d(i)
        if t[0] == 'D':
            if dc.st[i] == -1 and abs(cur) > 0.01:
                F.append(('FAIL', f'{t[1]} {t[2]} in breakdown, {abs(cur):.2f} A continuous', abs(cur)))
            elif abs(cur) > t[3]:
                F.append(('FAIL', f'{t[1]} {t[2]} carries {abs(cur):.2f} A > {t[3]} A', abs(cur)))
        elif t[0] == 'ULN_ON' and cur > 0.5:
            F.append(('FAIL', f'ULN2003 {t[1]} would sink > 0.5 A (no current limit, abs max 500 mA): channel fails', cur))
        elif t[0] == 'ULN_CLAMP' and cur > 0.5:
            F.append(('FAIL', f'ULN2003 {t[1]} clamp diode {cur:.1f} A', cur))
        elif t[0] == 'TC_BODY' and abs(cur) > 0.05:
            F.append(('CHECK' if abs(cur) < 0.5 else 'FAIL', f'TC4427 {t[1]} body diode conducts {abs(cur) * 1e3:.0f} mA '
                      'into its supply', abs(cur)))
        elif t[0] == 'CLAMP' and dc.st[i] == -1 and abs(cur) > 0.01:
            F.append(('FAIL', f'{t[2]} conducting {abs(cur):.2f} A continuously', abs(cur)))
        elif t[0] in ('OA_IN', 'OA_OUT'):
            oa[(t[0], t[1], t[2], t[3])] += abs(cur)
    for k_, cur in oa_r.items():
        oa[k_] += cur
    for (kind, pin, val, lim), cur in oa.items():
        if cur > lim:
            F.append(('FAIL', f'{val} {"input" if kind == "OA_IN" else "output"} {pin}: {cur * 1e3:.0f} mA through '
                      f'its ESD/rail diodes (> {lim * 1e3:.0f} mA)', cur))
    for rail, lim_c, lim_f, why in (('+3V3', 3.45, 3.6, 'MCU VDD max 3.6 V'), ('+3V3A', 3.45, 3.6, 'VDDA'),
                                    ('WB_VDDA', 3.45, 3.6, 'F103 VDDA'), ('+5V', 5.3, 6.0, 'TC4427 / LVC4245 VCCA'),
                                    ('V5_SENS', 5.25, 6.5, 'sensor supply: MPX5700AP 4.75-5.25 V; above 6.5 V assumed damaging')):
        v = V.get(rail)
        if v is None:
            continue
        if v > lim_f:
            F.append(('FAIL', f'{rail} back-fed to {v:.2f} V ({why})', v))
        elif v > lim_c:
            F.append(('CHECK', f'{rail} back-fed to {v:.2f} V ({why})', v))
    # TLS115 current limit
    for i, e in enumerate(dc.D):
        t = e[5]
        if t and t[0] == 'SRC' and t[1].startswith('V5_SENS') and dc.i_d(i) > 0.151:
            F.append(('CHECK', 'TLS115 in current limit (151-500 mA, thermal cycling): sensor 5 V collapses (TPS, MAP, '
                      'crank/cam pull-ups)', 0))
    # other MCU inputs disturbed
    moved = []
    for ref, pad, net in mcu_gpio(sysm):
        if (ref, pad) in focus or net not in base.V:
            continue
        if fault_net in POWER_NETS and net in SUPPLY_SENSE:
            continue
        dv = V.get(net, 0) - base.V[net]
        if abs(dv) > 0.1:
            moved.append(f'{mcu_pin_info(ref, pad)[0]}({net}) {dv:+.2f} V')
    if moved:
        F.append(('CHECK', 'other MCU pins move: ' + ', '.join(moved[:6]) + (' ...' if len(moved) > 6 else ''), len(moved)))
    return F


def solve_with_trips(make):
    """solve; any PTC carrying more than its trip current is opened and the network solved again (steady state)"""
    tripped = []
    for _ in range(4):
        dc = make(tuple(tripped))
        dc.solve()
        new = [e[3][1] for e in dc.R if e[3] and e[3][0] == 'F' and abs(dc.i_r(e)) > e[3][3]]
        if not new:
            break
        tripped += new
    return dc, tripped


def faults(sysm, year, fw, board_fw, cav_list=None, section='fault', connector='M.J1'):
    g, blocked = graph(sysm)
    bases = {}
    gnd_cavs = [c for c, n in sysm.cavity.items() if n == 'GND']
    pads = sysm.by_ref[connector]['pads']
    for cav in sorted(cav_list or pads, key=lambda c: (c[0], len(c), c)):
        net = pads.get(cav, '')
        if not net or (connector == 'M.J1' and cav in year_unwired(year)):
            continue
        b = base_net(net)
        tag = f'{cav}' if connector == 'M.J1' else f'{CONNECTORS[connector]}-{cav}'
        if b == 'GND':
            row('OK', section, year, f'{tag} GND: to ground: no change | to battery: short across the battery, the car\'s '
                f'fuse blows | open: {len(gnd_cavs) - 1} other ground cavities remain ({",".join(sorted(gnd_cavs))})'
                if len(gnd_cavs) > 1 else f'{tag} GND: open = the only ground cavity: ECU loses ground')
            continue
        jp1s = ['EXT', 'STOCK'] if b == 'HARN_IAT' else ['EXT']
        for jp1 in jp1s:
            if jp1 == 'STOCK':
                g2 = {k: list(v) for k, v in g.items()}
                g2.setdefault(net, []).append((sysm.canon.get('IN_IAT', 'IN_IAT'), 'JP1 1-2'))
                ends = trace(sysm, g2, {}, net)
            else:
                ends = trace(sysm, g, blocked, net)
            focus = sorted({(e[1], e[2]) for e in ends if e[0] == 'mcu'})
            if b == 'HARN_IAT' and jp1 == 'EXT':
                row('OK', section, year, f'{tag} {net} (JP1 on EXT, default): not connected to anything, no fault reaches '
                    'the ECU; the STOCK position is analysed below')
                continue
            variants = [(sl, st, {}) for sl, st in driver_states(sysm, net)]
            if b == 'V5_SENS':
                cold = {c: ('open',) for c, n in sysm.cavity.items() if base_net(n) in ('IN_CLT', 'HARN_IAT')}
                cold['J3'] = ('open',)
                variants.append(('CLT/IAT cold or unplugged', {}, cold))
            for case in ('GND', 'BAT14', 'BAT24', 'OPEN'):
                for slabel, states, sweep in variants:
                    if case == 'OPEN' and (slabel == 'on' or sweep):
                        continue
                    vcar = 24.0 if case == 'BAT24' else VCAR
                    key = (vcar, tuple(sorted(states.items())), jp1, tuple(sorted(sweep)))
                    if key not in bases:
                        bdc, _t = solve_with_trips(lambda tr: build_dc(sysm, year, fw, board_fw, vcar=vcar, states=states,
                                                                       jp1=jp1, tripped=tr, sweep=sweep))
                        bases[key] = (bdc, _evaluate(bdc, bdc, sysm, [], None))
                    base, base_f = bases[key]
                    if case == 'OPEN':
                        mk = lambda tr: build_dc(sysm, year, fw, board_fw, vcar=vcar, states=states, jp1=jp1, tripped=tr,
                                                 open_cav=cav if connector == 'M.J1' else None)
                    else:
                        mk = lambda tr: build_dc(sysm, year, fw, board_fw, vcar=vcar, states=states, jp1=jp1, tripped=tr,
                                                 fault=(net, 'GND' if case == 'GND' else 'BAT'), sweep=sweep)
                    dc, tripped = solve_with_trips(mk)
                    sev, F, reading = evaluate(dc, base, sysm, focus, net, base_f)
                    for t in tripped:
                        F.insert(0, ('OK', f'{t} PTC trips (steady state shown with it open)', 0))
                    if net in POWER_NETS and case != 'BAT14':
                        F = [f for f in F if not f[1].startswith('other MCU pins move')] if b != 'VIGN_IN' else F
                    if b.startswith('OUT_') or b in ('M:IAC_12V', 'M:OCV_12V', 'IAC_12V', 'OCV_12V'):
                        extra = {'OPEN': 'load disconnected', 'GND': 'the car\'s load is on permanently' if
                                 b.startswith('OUT_') else 'feed shorted', 'BAT14': 'load off', 'BAT24': 'load off'}[case]
                    elif case == 'OPEN':
                        nread = ', '.join(f'{mcu_pin_info(r, k)[0]} {base.V.get(sysm.by_ref[r]["pads"][k], 0):.2f} V'
                                          for r, k in focus)
                        extra = f'reads {reading} (normal {nread})' if focus else 'load disconnected'
                    else:
                        extra = f'reads {reading}' if focus else ''
                    if b == 'VBAT_IN' and case in ('OPEN', 'GND'):
                        v12 = dc.V.get('+12V', 0)
                        extra = (f'car fuse / ' if case == 'GND' else '') + f'+12V logic rail {v12:.1f} V' + \
                            (' (kept up by VIGN_IN through D8)' if v12 > 8 else ' (ECU off: loses its supply, nothing damaged)')
                    sev = max([f[0] for f in F] + ['OK'], key=SEV.get)
                    lab = f'{tag} {net} ' + {'GND': 'to GND', 'BAT14': 'to 14.4V', 'BAT24': 'to 24V', 'OPEN': 'open'}[case] \
                        + (f' [{slabel}]' if sweep else (f' [driver {slabel}]' if slabel else '')) \
                        + (' [JP1 STOCK]' if jp1 == 'STOCK' else '')
                    txt = '; '.join(f[1] for f in sorted(F, key=lambda f: -SEV[f[0]]))
                    verdict = {'FAIL': 'DAMAGE / abs max exceeded', 'CHECK': 'affects other functions or marginal',
                               'OK': 'only this function'}[sev]
                    row(sev, section, year, f'{lab}: {verdict}' + (f'; {extra}' if extra else '') + (f' | {txt}' if txt else ''))
                    for f in F:
                        if f[0] != 'OK':
                            WORST.append((SEV[f[0]], f[2], year, lab, f[1]))
            if b == 'IN_KNOCK':
                row('CHECK', section, year, f'{tag} IN_KNOCK step to 14.4 V / 24 V (transient, not in the DC model): C44 '
                    '100 nF couples the edge straight into U8 LMV321 pin 1 with no series resistor; only the op-amp\'s ESD '
                    'diodes clamp it (about 1.4-2.4 uC, several times an HBM ESD pulse). A 1-10 k series resistor '
                    'between C44 and pin 1 would limit it')


def baseline_checks(sysm, year, fw, board_fw):
    """normal operation (14.4 V and 16 V, outputs off): nothing over its rating; 24 V jump start: what it does"""
    issues = []
    for label, vcar in (('14.4 V', VCAR), ('16 V', 16.0), ('24 V jump start', 24.0)):
        dc = build_dc(sysm, year, fw, board_fw, vcar=vcar)
        dc.solve()
        F = _evaluate(dc, dc, sysm, [], None)
        sev = 'CHECK' if vcar == 24.0 else None
        issues += [(sev or f[0], f'{label}: {f[1]}') for f in F if f[0] != 'OK']
        for rail, want in (('+3V3', 3.3), ('+5V', 5.0), ('V5_SENS', 5.0)):
            if abs(dc.V.get(rail, 0) - want) > 0.1:
                issues.append(('CHECK', f'{label}: {rail} at {dc.V.get(rail, 0):.2f} V'))
    for s_, t in issues:
        row(s_, 'baseline', year, t + ('  (whole car at 24 V; the fault rows below report only what a short adds)'
                                       if 'jump' in t else ''))
    if not any(s_ != 'CHECK' or 'jump' not in t for s_, t in issues):
        row('OK', 'baseline', year, 'normal operation at 14.4 V and 16 V: rails 3.3 / 5.0 / 5.0 V, no MCU pin outside '
            'its limits, no resistor above 70 % of rating, no injection')


# ------------------------------------------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brief', action='store_true')
    ap.add_argument('--year', action='append')
    ap.add_argument('--sim-log')
    ap.add_argument('--no-faults', action='store_true')
    args = ap.parse_args()
    years = [y for y in YEARS if not args.year or y[0] in args.year]

    # existing checks, re-run (not rebuilt)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, 'check_pins.py')], capture_output=True, text=True)
    row('OK' if r.returncode == 0 else 'FAIL', 'existing', 'all', 'check_pins.py: ' + (r.stdout.strip() or r.stderr.strip())[-200:])

    fws, board_fw, external = firmware_configs()
    if args.sim_log:
        fws.update(firmware_from_simlog(args.sim_log))
        row('OK', 'firmware', 'all', f'firmware pins taken from {args.sim_log}')
    else:
        row('OK', 'firmware', 'all', 'firmware pins evaluated from miata_board.cpp (defaults -> year preset -> overrides). '
            f'rusEFI presets called but not in this checkout: {", ".join(external)}; the board code assigns every pin '
            'after them, and test_miata_ecu.cpp + sim_report.py check the real tune (119/119)')
    research = load_research()

    # copper
    try:
        import pcbnew  # noqa: F401
    except ImportError:
        row('FAIL', 'copper', 'all', 'pcbnew not importable: run with /usr/bin/python3 (KiCad 7)')
        finish()
    dparts = list(design.parts)
    dcu, dnames = check_copper('daughter', DAUGHTER_PCB, dparts)
    mb_cache, pcbs, systems = {}, {}, {}
    for year, module, pcb, etype, early in years:
        if module not in mb_cache:
            M, mparts = mb_parts(module)
            cu, mnames = check_copper(year if module != 'mb_nb2' else '2001-05', pcb, mparts)
            check_mating(DAUGHTER_PCB, pcb, year if module != 'mb_nb2' else '2001-05', pcbs)
            mb_cache[module] = (mparts, mnames)
        mparts, mnames = mb_cache[module]
        systems[year] = System(year, dparts, dnames, mparts, mnames)

    for year, module, pcb, etype, early in years:
        sysm = systems[year]
        notes = harness_notes(module)
        connectivity(sysm, year, module, fws[year], board_fw, research, notes)
        drivers_check(sysm, year, fws[year], board_fw, research, notes)
    unconnected_pins(systems[years[0][0]], 'all')
    floating_inputs(systems[years[0][0]], 'all')
    for year, module, pcb, etype, early in years:
        power_paths(systems[year], year, fws[year], board_fw)

    electrical(systems, fws, board_fw)

    if not args.no_faults:
        for year, module, pcb, etype, early in years:
            baseline_checks(systems[year], year, fws[year], board_fw)
            faults(systems[year], year, fws[year], board_fw)
        # the LSU sensor connector and AUX header are the same on every motherboard: once, on the last year's board
        last = years[-1][0]
        sysm = systems[last]
        faults(sysm, 'all', fws[last], board_fw, section='fault-other', connector='M.J2')
        faults(sysm, 'all', fws[last], board_fw, section='fault-other', connector='M.J5')
    finish(args.brief)


def finish(brief=False):
    order = ['existing', 'firmware', 'copper', 'mating', 'connect', 'reverse', 'power', 'drivers', 'nc-pins', 'electrical',
             'baseline', 'fault', 'fault-other']
    for sec in order:
        rows = [r for r in ROWS if r[1] == sec]
        if not rows:
            continue
        print(f'\n=== {sec} ===')
        for st, _s, year, text in rows:
            if brief and st == 'OK':
                continue
            print(f'[{st}] {year:9s} {text}')
    print('\n=== summary (OK / CHECK / FAIL) ===')
    years = sorted({r[2] for r in ROWS})
    secs = [s for s in order if any(r[1] == s for r in ROWS)]
    print('%-12s' % 'section' + ''.join('%-14s' % y for y in years))
    for sec in secs:
        line = '%-12s' % sec
        for y in years:
            c = collections.Counter(r[0] for r in ROWS if r[1] == sec and r[2] == y)
            line += '%-14s' % (f'{c["OK"]}/{c["CHECK"]}/{c["FAIL"]}' if c else '-')
        print(line)
    if WORST:
        print('\n=== worst fault cases, grouped by finding (worst example first) ===')
        groups = collections.OrderedDict()
        for sev, mag, year, lab, text in sorted(WORST, key=lambda w: (-w[0], -abs(w[1]))):
            k = (sev, re.sub(r'(?<![A-Za-z_.\d])-?\d+(\.\d+)?', '#', text))
            groups.setdefault(k, []).append((year, lab, text, mag))
        for (sev, _k), items in sorted(groups.items(), key=lambda kv: (-kv[0][0], -len(kv[1]))):
            year, lab, text, mag = items[0]
            cases = sorted({f'{y} {l.split(" ")[0]}' for y, l, _t, _m in items})
            kinds = sorted({l.split(' ', 2)[2] for _y, l, _t, _m in items if len(l.split(' ', 2)) > 2})
            print(f'[{"FAIL" if sev == 2 else "CHECK"}] {text}  <- worst: {year} {lab}; {len(items)} cases '
                  f'({", ".join(kinds[:4])}) at: {", ".join(cases[:10])}{" ..." if len(cases) > 10 else ""}')
    total = collections.Counter(r[0] for r in ROWS)
    print(f'\nTOTAL: {total["OK"]} OK, {total["CHECK"]} CHECK, {total["FAIL"]} FAIL')
    sys.exit(1 if total['FAIL'] else 0)


if __name__ == '__main__':
    main()
