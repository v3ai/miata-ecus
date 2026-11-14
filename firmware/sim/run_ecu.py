#!/usr/bin/env python3
"""Firmware-in-the-loop run of the miata-ecus ECU: the real OpenBLT bootloader and rusEFI application images on an
emulated STM32F407 (Renode), with the car outside it modelled: battery and key, sensors seen through the board's
analog front end, crank/cam signals on the hall inputs (real recorded cranking captures, then synthetic running at
set speeds), and every driver output recorded with its virtual time.

For each model year the run goes: key on -> cranking (recorded capture) -> idle -> cruise -> high rpm -> engine
stop -> key off, and checks what the firmware does at the pins against what it says it is doing (rusEFI's own
state, read from emulated RAM through the ELF's debug info) and against the car's expectations (RPM, sensor values,
injector and coil order, spark angle relative to TDC, fuel pump prime, main relay hold on 2003-05).

usage: run_ecu.py [--years 1989-93,2003-05] [--board 0.10|0.9] [--out DIR]
Needs: Renode 1.15 (RENODE env or /home/claude/renode/renode_1.15.3_portable/renode), the rusEFI build with this
board (RUSEFI env, default /home/claude/fw/rusefi/firmware: build/rusefi.elf, build/rusefi_crc32.bin,
bootloader/blbuild/openblt_f407-discovery.elf) and rusEFI's unit-test trigger captures (unit_tests/tests/trigger/
resources).
Exit code 0 when every check passes.
"""
import argparse
import glob
import json
import math
import os
import re
import subprocess
import sys
import time

SIM = os.path.dirname(os.path.abspath(__file__))
RENODE = os.environ.get('RENODE', '/home/claude/renode/renode_1.15.3_portable/renode')
RUSEFI = os.environ.get('RUSEFI', '/home/claude/fw/rusefi/firmware')
ELF = os.path.join(RUSEFI, 'build/rusefi.elf')
APP = os.path.join(RUSEFI, 'build/rusefi_crc32.bin')
# openblt_<board>.elf: f407-discovery from the offline compile check, miata-ecu from the real (CI) build
BOOT = (sorted(glob.glob(os.path.join(RUSEFI, 'bootloader/blbuild/openblt_*.elf'))) or
        [os.path.join(RUSEFI, 'bootloader/blbuild/openblt_f407-discovery.elf')])[0]
CAPTURES = os.path.join(os.path.dirname(RUSEFI), 'unit_tests/tests/trigger/resources')
sys.path.insert(0, os.path.join(SIM, 'tools'))

# engine_type_e values (rusEFI controllers/algo/engine_type_e.h)
YEARS = {
    '1989-93': dict(engine_type=34, family='NA', nb2_early=False, ign_sense=False, main_relay=False, vign='start'),
    '1994-95': dict(engine_type=80, family='NA', nb2_early=False, ign_sense=False, main_relay=False, vign='start'),
    '1996-97': dict(engine_type=10, family='NA', nb2_early=False, ign_sense=False, main_relay=False, vign=None),
    '1999-2000': dict(engine_type=83, family='NB', nb2_early=False, ign_sense=False, main_relay=False, vign=None),
    '2001-02': dict(engine_type=69, family='NB', nb2_early=True, ign_sense=False, main_relay=False, vign=None),
    '2003-05': dict(engine_type=69, family='NB', nb2_early=False, ign_sense=True, main_relay=True, vign='key'),
}

# Output pins as PinRecorder inputs (port * 16 + pin), from firmware/board/miata_pins.h
def pin_index(name):
    return 'ABCDE'.index(name[1]) * 16 + int(name[2:])

OUTPUTS = {'IGN1': 'PE1', 'IGN2': 'PE0', 'IGN3': 'PB9', 'IGN4': 'PB8', 'INJ1': 'PB7', 'INJ2': 'PB6', 'INJ3': 'PB5',
           'INJ4': 'PB4', 'IACV': 'PB3', 'VVT': 'PD7', 'BOOST': 'PD6', 'ALT': 'PD5', 'FP': 'PC14', 'MAINRLY': 'PC13',
           'AC': 'PE6', 'FAN': 'PE5', 'CEL': 'PE4', 'TACH': 'PE3', 'LS7': 'PE2', 'DRV_EN': 'PA8'}
GPIO_ENUM = {2 + pin_index(p): n for n, p in OUTPUTS.items()}   # rusEFI Gpio enum: A0 = 2, then 16 per port

CFG = 'persistentState.persistentConfiguration.engineConfiguration'
PROBES = {
    'rpm': '___engine.rpmCalculator.cachedRpmValue',
    'spin': '___engine.rpmCalculator.state',
    'sync': '___engine.triggerCentral.triggerState.shaft_is_synchronized',
    'trigErr': '___engine.triggerCentral.triggerState.totalTriggerErrorCounter',
    'adv0': '___engine.engineState.timingAdvance[0]',
    'adv1': '___engine.engineState.timingAdvance[1]',
    'injMs': '___engine.engineState.injectionDuration',
    'dwellMs': '___engine.ignitionState.sparkDwell',
    'vvt': '___engine.triggerCentral.vvtPosition[0][0]',
    'warn': '___engine.engineState.warnings.lastErrorCode',
    'warnCount': '___engine.engineState.warnings.warningCounter',
    'crit': 'hasCriticalFirmwareErrorFlag',
    'critMsg': 'criticalErrorMessageBuffer',
    'cfgMsg': 'configErrorMessageBuffer',
    'engineType': CFG + '.engineType',
    'trigType': CFG + '.trigger.type',
    'injMode': CFG + '.injectionMode',
    'ignMode': CFG + '.ignitionMode',
    'firingOrder': CFG + '.firingOrder',
    'trigOffset': CFG + '.globalTriggerAngleOffset',
    'fpPin': CFG + '.fuelPumpPin',
    'mainRelayPin': CFG + '.mainRelayPin',
    'primeS': CFG + '.startUpFuelPumpDuration',
}
# rev 0.10: the card socket's SPI2 pins and the two new inputs, as the tune holds them
PROBES.update({'spi2sck': CFG + '.spi2sckPin', 'spi2miso': CFG + '.spi2misoPin', 'spi2mosi': CFG + '.spi2mosiPin',
               'sdSpi': CFG + '.sdCardSpiDevice', 'sdCs': CFG + '.sdCardCsPin', 'flexPin': CFG + '.flexSensorPin'})
# ... and as the port registers hold them (GPIOB MODER / AFRH for PB10, PB14, PB15; GPIOD MODER / ODR for PD13)
REGS = {'gpiobModer': 0x40020400, 'gpiobAfrh': 0x40020424, 'gpiodModer': 0x40020C00, 'gpiodOdr': 0x40020C14}
SD_CS_INDEX = 3 * 16 + 13       # PD13 on the pin recorder
for i in range(4):
    PROBES[f'injPin{i}'] = f'{CFG}.injectionPins[{i}]'
    PROBES[f'ignPin{i}'] = f'{CFG}.ignitionPins[{i}]'
for s in ('clt', 'iat'):
    for f in ('tempC_1', 'tempC_2', 'tempC_3', 'resistance_1', 'resistance_2', 'resistance_3', 'bias_resistor'):
        PROBES[f'{s}_{f}'] = f'{CFG}.{s}.config.{f}'
# Sensors read from rusEFI's registry, by SensorType name. Only sensors that store their value (StoredValueSensor and
# its subclasses) can be read this way: combined ones (Map, Tps1) are proxies, so their underlying sensors are used.
SENSOR_NAMES = {'sClt': 'Clt', 'sIat': 'Iat', 'sTps': 'Tps1Primary', 'sMap': 'MapSlow', 'sVbatt': 'BatteryVoltage',
                'sRpm': 'Rpm', 'sIgnKey': 'IgnKeyVoltage', 'sMaf': 'Maf', 'sLambda': 'Lambda1'}
SENSORS = {}


def sensor_ids(elf):
    """SensorType enum values of this build (gdb)."""
    args = []
    for n in SENSOR_NAMES.values():
        args += ['-ex', f'print (int)SensorType::{n}']
    out = subprocess.run(['gdb', '-batch', '-nx'] + args + [elf], capture_output=True, text=True).stdout
    vals = [int(v) for v in re.findall(r'^\$\d+ = (\d+)$', out, re.M)]
    if len(vals) != len(SENSOR_NAMES):
        raise SystemExit('could not read SensorType values from ' + elf + '\n' + out)
    return dict(zip(SENSOR_NAMES, vals))

# --- the board's analog front end (firmware/board/miata_pins.h, scripts/design.py) ---
VBATT_DIV = (33.0 + 6.8) / 6.8
ANALOG_DIV = (5.6 + 10.0) / 10.0
# Where the board takes its battery measurement, as a drop below the battery pin. A rev 0.10 daughterboard senses the
# battery input itself; up to rev 0.9 the divider sat on the +12V rail behind the reverse diode D7 and the fuse F1.
# Set from --board in main().
BOARDS = {'0.10': 0.0, '0.9': 0.35}
RAIL_DROP = BOARDS['0.10']
TEMP_PULLUP, TEMP_LOAD = 2700.0, 15600.0


def thermistor_pin(r_ohm):
    """CLT/IAT: 2.7k pull-up to the 5 V sensor rail, loaded by the 5.6k/10k divider; volts at the MCU pin."""
    node = 5.0 / TEMP_PULLUP / (1 / TEMP_PULLUP + 1 / TEMP_LOAD + 1 / r_ohm)
    return node / ANALOG_DIV


def mpx5700(kpa):
    return 5.0 * (0.0012858 * kpa + 0.04)


def car_pins(vbat, key, tps_v, map_kpa, clt_ohm, iat_ohm, maf_v=1.2, vign_mode=None, cranking=False):
    """MCU pin voltages for one car state.

    vign_mode: what the harness puts on the VIGN_IN cavity. 'key' (2003-05 4S): battery while the key is on.
    'start' (1989-95 1C): battery only while the starter turns. None: no wire on that cavity."""
    if vign_mode == 'key':
        vign = vbat if key else 0.0
    elif vign_mode == 'start':
        vign = vbat if (key and cranking) else 0.0
    else:
        vign = 0.0
    return {
        'PA1': max(0.0, vbat - RAIL_DROP) / VBATT_DIV,    # VBATT (the board's battery sense point)
        'PA2': vign / VBATT_DIV,                          # ignition sense (1C / 4S)
        'PA4': tps_v / ANALOG_DIV,
        'PA5': mpx5700(map_kpa) / ANALOG_DIV,
        'PA6': thermistor_pin(clt_ohm),
        'PA7': thermistor_pin(iat_ohm),
        'PB1': maf_v / ANALOG_DIV,                        # AFM flap / MAF
        'PB0': 0.45 / ANALOG_DIV,                         # front narrowband O2
        'PC5': 0.10 / ANALOG_DIV,                         # AUX1
        'PC4': 0.0,                                       # external wideband input, unused
        'PA3': 1.65,                                      # knock input bias
    }


def steinhart(conf, r):
    """Temperature (C) that rusEFI's three-point thermistor model gives for resistance r."""
    l1, l2, l3 = (math.log(conf[f'resistance_{i}']) for i in (1, 2, 3))
    y1, y2, y3 = (1 / (conf[f'tempC_{i}'] + 273.15) for i in (1, 2, 3))
    g2, g3 = (y2 - y1) / (l2 - l1), (y3 - y1) / (l3 - l1)
    c = (g3 - g2) / (l3 - l2) / (l1 + l2 + l3)
    b = g2 - c * (l1 * l1 + l1 * l2 + l2 * l2)
    a = y1 - (b + l1 * l1 * c) * l1
    lr = math.log(r)
    return 1 / (a + b * lr + c * lr ** 3) - 273.15


# --- crank/cam stimulus ---
NB_CRANK_MAGIC = 70


def na_pattern():
    """TT_MAZDA_MIATA_NA (rusEFI trigger_mazda.cpp), crank degrees over 720. Primary (2-pulse SGC) is HALL2 = wheel
    Ch1, secondary (4-pulse SGT) is HALL1 = Ch0. Returns lines and the shape's sync angle and tdcPosition."""
    ev = [(52.960405, 'R', 'S'), (122.635956, 'F', 'S'), (216.897031, 'R', 'P'), (232.640068, 'R', 'S'),
          (288.819688, 'F', 'P'), (302.646323, 'F', 'S'), (412.448056, 'R', 'S'), (482.816719, 'F', 'S'),
          (577.035495, 'R', 'P'), (592.878113, 'R', 'S'), (662.899708, 'F', 'S'), (720.0, 'F', 'P')]
    lines = [(a % 720, 1 if w == 'P' else 0, 1 if e == 'R' else 0) for a, e, w in ev]
    return sorted(lines), 288.819688, 5.181


def nb_crank_angles():
    """TT_MIATA_VVT crank wheel over 720 (four repeats of the 180-degree definition), narrow 4-degree pulses."""
    out = []
    for k in range(4):
        base = 180 * k
        out += [(base + 180 - NB_CRANK_MAGIC - 4, 0, 0), (base + 180 - NB_CRANK_MAGIC, 0, 1),
                (base + 180 - 4, 0, 0), (base + 180, 0, 1)]
    return out


NB_CAM = [(325, 0), (360, 1), (641, 0), (679, 1), (700, 0), (720, 1)]   # VVT_MIATA_NB, cam edges in crank degrees


def nb_cam_phase(capture):
    """Crank angle (in nb_crank_angles() coordinates) of the cam's 720 RISE edge in a real NB2 recording."""
    rows = [l.split(',') for l in open(capture).read().split('\n')[1:] if l.strip()]
    t = [float(r[0]) for r in rows]
    crank = [int(r[1]) for r in rows]
    cam = [int(r[2]) for r in rows]
    rises, cam_rises = [], []
    for i in range(1, len(rows)):
        if crank[i] and not crank[i - 1]:
            rises.append(t[i])
        if cam[i] and not cam[i - 1]:
            cam_rises.append(t[i])
    # label crank rises: a rise after a short (70 deg) gap is at 0 mod 180, after a long (110) gap at 110 mod 180
    gaps = [b - a for a, b in zip(rises, rises[1:])]
    angle = {}
    for i in range(2, len(rises)):
        short = gaps[i - 1] < gaps[i - 2]
        angle[i] = 0.0 if short else 110.0
    # use the last cam tooth pair: the 720 rise follows a short gap after the 679 rise (21 degrees)
    best = None
    for j in range(1, len(cam_rises)):
        if cam_rises[j] - cam_rises[j - 1] < 0.25 * (cam_rises[j - 1] - cam_rises[j - 2] if j > 1 else 1e9):
            best = cam_rises[j]
    i = max(k for k in angle if rises[k] <= best and k + 1 < len(rises))
    a0 = angle[i]
    span = 70.0 if a0 == 110.0 else 110.0
    frac = (best - rises[i]) / (rises[i + 1] - rises[i])
    return (a0 + frac * span) % 180.0


def write_stimulus(family, out):
    paths = {}
    if family == 'NA':
        # cranking_na_4.csv: rusEFI reads it with REVERSE_ORDER (column 0 = secondary SGT, column 1 = primary SGC)
        src = os.path.join(CAPTURES, 'cranking_na_4.csv')
        cols = (0, 1)   # column -> wheel channel (Ch0 = HALL1 = SGT, Ch1 = HALL2 = SGC)
        lines, sync, tdc = na_pattern()
        meta = {'sync': sync, 'tdcPosition': tdc}
    else:
        src = os.path.join(CAPTURES, 'nb2-cranking-good.csv')
        cols = (0, 1)   # crank -> HALL1 (Ch0), cam -> HALL2 (Ch1)
        phase = nb_cam_phase(src)
        crank = nb_crank_angles()
        # the recorded cam edge sits at `phase` (mod 180) past a crank reference; place cam 720-rise there in cycle 4
        cam = [((a - 720 + 540 + phase) % 720, 1, lvl) for a, lvl in NB_CAM]
        lines = sorted(crank + cam)
        meta = {'camPhase': phase}
    rows = [l.split(',') for l in open(src).read().split('\n')[1:] if l.strip()]
    prev = None
    cap = []
    for r in rows:
        v = [int(float(r[1 + c])) for c in range(2)]
        for c in range(2):
            if prev is None or v[c] != prev[c]:
                cap.append((float(r[0]), cols[c], v[c]))
        prev = v
    t0 = cap[0][0]
    paths['capture'] = os.path.join(out, f'{family}_capture.csv')
    with open(paths['capture'], 'w') as f:
        f.write('# time_s,channel,level  (from %s)\n' % os.path.basename(src))
        for t, c, v in cap:
            f.write(f'{t - t0 + 0.001:.9f},{c},{v}\n')
    paths['pattern'] = os.path.join(out, f'{family}_pattern.csv')
    with open(paths['pattern'], 'w') as f:
        f.write('# angle_deg,channel,level\n')
        for a, c, v in lines:
            f.write(f'{a:.6f},{c},{v}\n')
    paths['captureLength'] = cap[-1][0] - t0
    paths['meta'] = meta
    return paths


# --- the timeline ---
def timeline(year, stim):
    y = YEARS[year]
    cold = 2500.0     # ~20 C coolant
    warm = 240.0      # ~85 C
    iat = 2000.0
    steps = []

    def pins(**kw):
        steps.append(('pins', car_pins(vign_mode=y['vign'], **kw)))

    def run(name, seconds):
        steps.append(('run', name, seconds))

    pins(vbat=12.6, key=False, tps_v=0.6, map_kpa=100, clt_ohm=cold, iat_ohm=iat)
    run('boot', 1.2)
    pins(vbat=12.4, key=True, tps_v=0.6, map_kpa=100, clt_ohm=cold, iat_ohm=iat)
    run('keyOn', 1.5)
    pins(vbat=10.5, key=True, tps_v=0.6, map_kpa=90, clt_ohm=cold, iat_ohm=iat, maf_v=0.6, cranking=True)
    steps.append(('wheel', 'LoadCapture @%s' % stim['capture']))
    steps.append(('wheel', 'Start'))
    run('crank', stim['captureLength'] + 0.05)
    steps.append(('wheel', 'LoadPattern @%s 720' % stim['pattern']))
    steps.append(('wheel', 'SetRpm 900'))
    steps.append(('wheel', 'Start'))
    pins(vbat=14.2, key=True, tps_v=0.6, map_kpa=35, clt_ohm=warm, iat_ohm=iat, maf_v=1.3)
    run('idle', 1.5)
    steps.append(('wheel', 'SetRpm 3000'))
    pins(vbat=14.2, key=True, tps_v=1.4, map_kpa=60, clt_ohm=warm, iat_ohm=iat, maf_v=2.4)
    run('cruise', 1.2)
    steps.append(('wheel', 'SetRpm 6500'))
    # heavy load but inside every preset's sensor ranges (4.2 V on the TPS reads as "TPS high" on some presets)
    pins(vbat=14.2, key=True, tps_v=3.6, map_kpa=90, clt_ohm=warm, iat_ohm=iat, maf_v=3.4)
    run('high', 1.0)
    steps.append(('wheel', 'Stop'))
    pins(vbat=12.4, key=True, tps_v=0.6, map_kpa=100, clt_ohm=warm, iat_ohm=iat)
    run('stalled', 2.5)
    pins(vbat=12.4, key=False, tps_v=0.6, map_kpa=100, clt_ohm=warm, iat_ohm=iat)
    run('keyOff', 3.0)
    return steps


def symbol(name):
    for line in subprocess.run(['arm-none-eabi-nm', '-C', ELF], capture_output=True, text=True).stdout.splitlines():
        if line.endswith(' ' + name) or (' ' + name + ' ') in line + ' ':
            return int(line.split()[0], 16)
    raise SystemExit('symbol not found: ' + name)


def raw_symbol(prefix):
    for line in subprocess.run(['arm-none-eabi-nm', ELF], capture_output=True, text=True).stdout.splitlines():
        f = line.split()
        if len(f) == 3 and f[2].startswith(prefix):
            return int(f[0], 16)
    raise SystemExit('symbol not found: ' + prefix)


def platform(names, out):
    """Write the platform files `names` (one, or several joined into one file) with @SIM@ replaced by this
    checkout's path. They are joined because the NVIC has no bus address (see NvicRettobase.cs), and Renode only
    lets later description files reference peripherals that have one."""
    names = [names] if isinstance(names, str) else names
    dst = os.path.join(out, '+'.join(n.replace('.repl', '') for n in names) + '.repl')
    open(dst, 'w').write('\n'.join(open(os.path.join(SIM, n)).read() for n in names).replace('@SIM@', SIM))
    return dst


def build_resc(year, out, probes, stim):
    y = YEARS[year]
    rec = os.path.join(out, 'pins.txt')
    probe_file = os.path.join(out, 'probes.json')
    json.dump(probes, open(probe_file, 'w'))
    reg = raw_symbol('_ZL16s_sensorRegistry')
    slow = symbol('PeriodicSlowController::PeriodicTask()')
    reset_cfg = symbol('resetConfigurationExt(engine_type_e)')
    nb2 = symbol('nb2Early')
    # SetGlobalAdvanceImmediately: when every CPU sleeps (WFI), jump virtual time to the next event instead of waiting
    # for the host clock; the firmware sees the same timing, the run just takes less wall time
    L = ['using sysbus', 'emulation SetGlobalAdvanceImmediately true',
         f'include @{SIM}/models/STM32F4ADC.cs', f'include @{SIM}/models/STM32F4DMA.cs', f'include @{SIM}/models/TriggerWheel.cs',
         f'include @{SIM}/models/PinRecorder.cs', f'include @{SIM}/models/NvicRettobase.cs', f'include @{SIM}/models/CortexMDwt.cs',
         'mach create "ecu"',
         f'machine LoadPlatformDescription @{platform(["stm32f407_ecu.repl", "ecu_bench.repl"], out)}',
         'sysbus Tag <0xE0042000, 0xE0042003> "DBGMCU_IDCODE" 0x10076413',
         # system-memory facts in the (otherwise zero) ROM area: flash size 1024 KB at 0x1FFF7A22, a unique ID at
         # 0x1FFF7A10. rusEFI refuses to run ("expected at least 1024K of flash") without the first.
         'sysbus WriteDoubleWord 0x1FFF7A20 0x04000000',
         'sysbus WriteDoubleWord 0x1FFF7A10 0x00470031', 'sysbus WriteDoubleWord 0x1FFF7A14 0x34385111',
         'sysbus WriteDoubleWord 0x1FFF7A18 0x20393530',
         f'sysbus LoadELF @{BOOT}', f'sysbus LoadBinary @{APP} 0x08008000', f'sysbus LoadSymbolsFrom @{ELF}',
         'cpu VectorTableOffset 0x08000000',
         f'rec SetOutputFile @{rec}']
    # year select: the board's first boot builds a fresh tune with resetConfigurationExt(DEFAULT_ENGINE_TYPE); the
    # hook hands it this year's engine type instead (what TunerStudio's Popular Vehicles button does)
    early = f'self.GetMachine().SystemBus.WriteByte({nb2:#x}, {1 if y["nb2_early"] else 0}); '
    L.append(f'cpu AddHook {reset_cfg:#x} "from Antmicro.Renode.Peripherals.CPU import RegisterValue; {early}'
             f'self.SetRegisterUnsafe(0, RegisterValue.Create({y["engine_type"]}, 32))"')
    sensors = json.dumps(SENSORS).replace('"', "'")
    L.append(f'cpu AddHook {slow:#x} "import sys, json; sys.miata_probes = sys.__dict__.get(\'miata_probes\') or '
             f'json.load(open(\'{probe_file}\')); miata_machine = self.GetMachine(); miata_log = lambda s: self.Log(LogLevel.Error, s); sys.miata_sensors = {sensors}; sys.miata_registry = {reg:#x}; '
             # compile once: IronPython keeps every compiled code object, and recompiling at 20 Hz grew Renode by GBs
             f'sys.miata_code = sys.__dict__.get(\'miata_code\') or compile(open(\'{SIM}/tools/sampler.py\').read(), \'sampler\', \'exec\'); '
             f'exec(sys.miata_code)"')
    L.append('logLevel 3')
    for s in timeline(year, stim):
        if s[0] == 'pins':
            L += [f'adc SetPinVoltage "{p}" {v:.4f}' for p, v in s[1].items()]
        elif s[0] == 'wheel':
            L.append('wheel ' + s[1])
        elif s[0] == 'run':
            L.append(f'emulation RunFor "{s[2]:.4f}"')
    L += ['rec Flush', 'quit']
    path = os.path.join(out, 'run.resc')
    open(path, 'w').write('\n'.join(L) + '\n')
    return path


def parse_log(text):
    return [json.loads(m) for m in re.findall(r'SAMPLE (\{.*\})', text)]


def read_pins(path):
    ev = {}
    for line in open(path):
        t, n, v = line.split()
        ev.setdefault(int(n), []).append((int(t) * 1e-9, int(v)))
    return ev


def pulses(events, t0, t1):
    """(rise, fall) pairs fully inside [t0, t1]"""
    out, rise = [], None
    for t, v in events:
        if v == 1:
            rise = t
        elif rise is not None:
            if t0 <= rise and t <= t1:
                out.append((rise, t))
            rise = None
    return out


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, phase, what, ok, detail):
        status = ok if isinstance(ok, str) else ('OK' if ok else 'FAIL')
        self.rows.append((phase, what, status, detail))


def analyse(year, samples, phases, pins, stim, chk):
    y = YEARS[year]
    # phase windows from the run order
    bounds, t = {}, 0.0
    for name, dur in phases:
        bounds[name] = (t, t + dur)
        t += dur

    def at_end(name, margin=0.15):
        a, b = bounds[name]
        cand = [s for s in samples if b - margin - 0.3 <= s['t'] <= b]
        return cand[-1] if cand else None

    first = samples[0] if samples else {}
    last = samples[-1] if samples else {}
    if not samples:
        chk.add('boot', 'firmware reaches the main loop', False, 'no samples: the slow callback never ran')
        return
    chk.add('boot', 'year preset applied', last.get('engineType') == y['engine_type'],
            f"engineType {last.get('engineType')} (want {y['engine_type']})")
    crit = [s for s in samples if s.get('crit')]
    chk.add('all', 'no critical firmware error', not crit,
            (crit[0].get('critMsg') or 'flag set') if crit else 'hasCriticalFirmwareErrorFlag stays 0')
    cfg_msgs = sorted({s.get('cfgMsg') for s in samples if s.get('cfgMsg')})
    chk.add('all', 'no configuration error', not cfg_msgs, '; '.join(cfg_msgs) if cfg_msgs else 'none')

    # pin assignment as the firmware holds it
    inj_pins = [GPIO_ENUM.get(last.get(f'injPin{i}'), last.get(f'injPin{i}')) for i in range(4)]
    ign_pins = [GPIO_ENUM.get(last.get(f'ignPin{i}'), last.get(f'ignPin{i}')) for i in range(4)]
    chk.add('boot', 'injector outputs', inj_pins[:4] == ['INJ1', 'INJ2', 'INJ3', 'INJ4'], ' '.join(map(str, inj_pins)))
    chk.add('boot', 'ignition outputs', ign_pins[0] == 'IGN1' and ign_pins[2] == 'IGN2', ' '.join(map(str, ign_pins)))

    # rev 0.10: the card socket on SPI2. The tune's pins, then what the port registers say at the end of the run:
    # PB10/PB14/PB15 in alternate-function mode 5 (SPI2), PD13 a push-pull output (the card's chip select).
    def gp(v):
        if v is None:
            return None
        v = int(v)          # rusEFI's Gpio enum: 0 unassigned, PA0 = 2, then 16 per port
        return 'unassigned' if v == 0 else 'P' + 'ABCDEFGH'[(v - 2) // 16] + str((v - 2) % 16)
    card = [gp(last.get(k)) for k in ('spi2sck', 'spi2miso', 'spi2mosi', 'sdCs')]
    chk.add('boot', 'card socket pins in the tune (SCK MISO MOSI CS)', card == ['PB10', 'PB14', 'PB15', 'PD13'] and last.get('sdSpi') == 2,
            f"{' '.join(map(str, card))}, SPI device {last.get('sdSpi')}")
    chk.add('boot', 'flex input ships unassigned', last.get('flexPin') == 0, str(gp(last.get('flexPin'))))
    if last.get('gpiobModer') is not None:
        mb_, af, md, od = (int(last[k]) for k in ('gpiobModer', 'gpiobAfrh', 'gpiodModer', 'gpiodOdr'))
        mode = {p: (mb_ >> (2 * p)) & 3 for p in (10, 14, 15)}
        func = {p: (af >> (4 * (p - 8))) & 15 for p in (10, 14, 15)}
        chk.add('all', 'SPI2 on PB10 / PB14 / PB15 (alternate function 5)', all(mode[p] == 2 and func[p] == 5 for p in mode),
                ', '.join(f'PB{p}: mode {mode[p]} AF{func[p]}' for p in mode))
        cs = pins.get(SD_CS_INDEX, [])
        chk.add('all', 'card chip select PD13 is an output, driven high (no card selected)',
                (md >> 26) & 3 == 1 and (od >> 13) & 1 == 1,
                f"mode {(md >> 26) & 3}, level {(od >> 13) & 1} at the end, {len(cs)} edges in the run"
                + (f', first at {cs[0][0]:.2f} s' if cs else ''))

    # key on: sensors
    s = at_end('keyOn')
    if s:
        vb = s.get('sVbatt')
        chk.add('keyOn', 'battery voltage reading', vb is not None and abs(vb - (12.4 - RAIL_DROP)) < 0.25,
                f'{vb} V (12.4 V at the pin, {12.4 - RAIL_DROP:.2f} V at the sense point)')
        conf = {k[4:]: s[k] for k in s if k.startswith('clt_')}
        want = steinhart(conf, 2500.0)
        got = s.get('sClt')
        chk.add('keyOn', 'coolant temperature reading', got is not None and abs(got - want) < 1.5,
                f'{got} C for 2.5 kOhm (tune curve says {want:.1f} C)')
        conf = {k[4:]: s[k] for k in s if k.startswith('iat_')}
        want = steinhart(conf, 2000.0)
        got = s.get('sIat')
        chk.add('keyOn', 'intake air temperature reading', got is not None and abs(got - want) < 1.5,
                f'{got} C for 2.0 kOhm (tune curve says {want:.1f} C)')
        m = s.get('sMap')
        chk.add('keyOn', 'MAP reading (engine off = baro)', m is not None and abs(m - 100) < 2, f'{m} kPa (100 applied)')
        if y['ign_sense']:
            k = s.get('sIgnKey')
            chk.add('keyOn', 'ignition key sense', k is not None and k > 11, f'{k} V')

    # fuel pump prime at key on
    fp = pins.get(pin_index(OUTPUTS['FP']), [])
    a, b = bounds['keyOn']
    on_at_key = [e for e in fp if a - 1.3 <= e[0] <= b and e[1] == 1]
    chk.add('keyOn', 'fuel pump primes at key on', bool(on_at_key) or (fp and fp[0][1] == 1),
            f'FP edges {[(round(t, 3), v) for t, v in fp[:6]]}')

    # cranking
    s = at_end('crank', 0.2)
    if s:
        chk.add('crank', 'trigger syncs on the recorded cranking capture', s.get('sync') == 1 and (s.get('rpm') or 0) > 100,
                f"rpm {s.get('rpm'):.0f}, synced {s.get('sync')}, trigger errors {s.get('trigErr')}")
    ca, cb = bounds['crank']
    for name in ('INJ1', 'INJ2', 'INJ3', 'INJ4', 'IGN1', 'IGN2'):
        n = len(pulses(pins.get(pin_index(OUTPUTS[name]), []), ca, cb))
        chk.add('crank', f'{name} active while cranking', n > 2, f'{n} pulses')

    # running phases
    for ph, rpm in (('idle', 900), ('cruise', 3000), ('high', 6500)):
        s = at_end(ph)
        if not s:
            chk.add(ph, 'samples', False, 'none')
            continue
        r = s.get('rpm') or 0
        chk.add(ph, 'RPM', abs(r - rpm) < 0.02 * rpm, f'{r:.0f} (wheel {rpm})')
        a, b = bounds[ph]
        a = b - 0.6   # settled part
        cyc = 120.0 / rpm
        for name in ('INJ1', 'INJ2', 'INJ3', 'INJ4'):
            p = pulses(pins.get(pin_index(OUTPUTS[name]), []), a, b)
            per_cycle = len(p) * cyc / (b - a)
            width = sorted(1000 * (f - r_) for r_, f in p)
            wmed = width[len(width) // 2] if width else 0
            want_n = 2 if (y['engine_type'] == 34) else 1
            window = 1000 * cyc / want_n
            if s['injMs'] > 0.95 * window:
                # the tune asks for more fuel than fits between injections: rusEFI holds the injector open and
                # warns; a tune limit, not a board one
                chk.add(ph, f'{name} pulses per cycle', 'CHECK',
                        f'fuel demand {s["injMs"]:.2f} ms is {100 * s["injMs"] / window:.0f} % of the {window:.2f} ms '
                        f'injection window at {rpm} rpm (over 95 %)')
                continue
            chk.add(ph, f'{name} pulses per cycle', abs(per_cycle - want_n) < 0.3,
                    f'{per_cycle:.2f} (want {want_n}), width {wmed:.2f} ms, firmware {s.get("injMs"):.2f} ms')
            if wmed:
                chk.add(ph, f'{name} pulse width matches firmware', abs(wmed - s['injMs']) < 0.1 + 0.02 * s['injMs'],
                        f'{wmed:.3f} vs {s["injMs"]:.3f} ms')
        for name, n_want in (('IGN1', 2), ('IGN2', 2)):
            p = pulses(pins.get(pin_index(OUTPUTS[name]), []), a, b)
            per_cycle = len(p) * cyc / (b - a)
            dw = sorted(1000 * (f - r_) for r_, f in p)
            dmed = dw[len(dw) // 2] if dw else 0
            chk.add(ph, f'{name} sparks per cycle (wasted spark)', abs(per_cycle - n_want) < 0.3,
                    f'{per_cycle:.2f}, dwell {dmed:.2f} ms (firmware {s.get("dwellMs"):.2f} ms)')
            if dmed:
                chk.add(ph, f'{name} dwell matches firmware', abs(dmed - s['dwellMs']) < 0.15, f'{dmed:.3f} vs {s["dwellMs"]:.3f} ms')
        # spark angle: IGN1 and IGN2 fire 180 degrees apart; angle vs TDC from the NA shape geometry
        f1 = [f for _, f in pulses(pins.get(pin_index(OUTPUTS['IGN1']), []), a, b)]
        f2 = [f for _, f in pulses(pins.get(pin_index(OUTPUTS['IGN2']), []), a, b)]
        if f1 and f2:
            deg = 6.0 * rpm
            sep = [((t2 - t1) * deg) % 360 for t1 in f1 for t2 in f2 if 0 < t2 - t1 < cyc / 2]
            sm = sorted(sep)[len(sep) // 2] if sep else float('nan')
            chk.add(ph, 'IGN2 fires 180 deg after IGN1', abs(sm - 180) < 1.0, f'{sm:.2f} deg')
        if y['family'] == 'NA' and f1 and 'wheelCycle0' in stim:
            pass
    # firing order: injector start order over one cycle at cruise
    a, b = bounds['cruise']
    a = b - 0.3
    starts = []
    for name in ('INJ1', 'INJ2', 'INJ3', 'INJ4'):
        for r_, f in pulses(pins.get(pin_index(OUTPUTS[name]), []), a, b):
            starts.append((r_, name))
    starts.sort()
    seq = [n for _, n in starts]
    if y['engine_type'] != 34 and len(seq) >= 8:
        order = ' '.join(seq[:8])
        cyc = 'INJ1 INJ3 INJ4 INJ2'
        ok = any(' '.join((seq[i:] + seq[:i])[:4]) == cyc for i in range(4))
        chk.add('cruise', 'injector order 1-3-4-2', ok, order)
    # stall: outputs stop, fuel pump turns off
    a, b = bounds['stalled']
    s = at_end('stalled')
    if s:
        chk.add('stalled', 'RPM drops to 0 when the engine stops', (s.get('rpm') or 0) == 0, f"{s.get('rpm')}")
    for name in ('INJ1', 'IGN1'):
        late = [e for e in pins.get(pin_index(OUTPUTS[name]), []) if a + 0.5 <= e[0] <= b]
        chk.add('stalled', f'{name} quiet after stall', not late, f'{len(late)} edges')
    fp_off = [e for e in fp if a <= e[0] <= b and e[1] == 0]
    chk.add('stalled', 'fuel pump stops after stall', bool(fp_off), f'off at {fp_off[0][0] - a:.2f} s after stall' if fp_off else 'still on')
    # key off: 2003-05 drops the main relay it holds
    if y['main_relay']:
        mr = pins.get(pin_index(OUTPUTS['MAINRLY']), [])
        a, b = bounds['keyOff']
        on = [e for e in mr if e[1] == 1]
        off = [e for e in mr if a <= e[0] <= b and e[1] == 0]
        chk.add('keyOn', 'main relay held on (3H)', bool(on), f'{len(on)} on edges')
        chk.add('keyOff', 'main relay released after key off', bool(off), f'off {off[0][0] - a:.2f} s after key off' if off else 'still on')
    # warnings
    codes = sorted({s.get('warn') for s in samples if s.get('warn')})
    chk.add('all', 'warning codes seen', 'INFO', ', '.join(map(str, codes)) or 'none')


def run_renode(resc, timeout, log_path, stall=600):
    """Run Renode on a script (ending with `quit`), streaming its log to log_path, and return the log. The monitor
    listens on a free TCP port rather than the console: Renode's console keeps re-queueing end-of-file from a closed
    stdin until it runs out of memory, and with an open but idle stdin it blocks its own logging. Logs, including the
    SAMPLE/LSU/... lines the checks read, go to stdout either way. Renode is stopped if the log stops growing for
    `stall` seconds (the emulation has hung) or after `timeout` seconds; the port is written to log_path + '.port' so
    a hung run can be inspected (`telnet 127.0.0.1 <port>`)."""
    import socket
    import time
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    open(log_path + '.port', 'w').write(str(port))
    start = last = time.time()
    size = 0
    with open(log_path, 'w') as f:
        proc = subprocess.Popen([RENODE, '--disable-xwt', '--plain', '-P', str(port), '-e', f'include @{resc}'],
                                stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
        while proc.poll() is None:
            time.sleep(5)
            now = time.time()
            grown = os.path.getsize(log_path)
            if grown != size:
                size, last = grown, now
            if now - last > stall or now - start > timeout:
                print(f'  Renode stopped: {"no log output for %d s" % stall if now - last > stall else "time limit"}',
                      flush=True)
                proc.kill()
                proc.wait()
    log = open(log_path, errors='replace').read()
    log = re.sub(r'\x1b\[[0-9;]*m', '', log)
    open(log_path, 'w').write(log)
    return log


def crc_image():
    """OpenBLT starts the application only if the checksum in its vector table is right: rusEFI's bundle step writes
    it (hex2dfu); redo that when the .hex is newer than the image."""
    hexf = os.path.join(RUSEFI, 'build/rusefi.hex')
    if not os.path.exists(APP) or os.path.getmtime(hexf) > os.path.getmtime(APP):
        subprocess.run([os.path.join(RUSEFI, '../misc/encedo_hex2dfu/hex2dfu.bin'), '-i', hexf, '-c', '0x0800801C',
                        '-b', APP], check=True, capture_output=True)


def main():
    crc_image()
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', default=','.join(YEARS))
    ap.add_argument('--out', default=os.path.join(SIM, 'out'))
    ap.add_argument('--board', default='0.10', choices=sorted(BOARDS),
                    help='daughterboard revision the bench models (where the battery is sensed)')
    args = ap.parse_args()
    global RAIL_DROP
    RAIL_DROP = BOARDS[args.board]
    print(f'bench: daughterboard rev {args.board} (battery sensed {RAIL_DROP:.2f} V below the battery pin)', flush=True)
    pr = subprocess.run([sys.executable, os.path.join(SIM, 'tools/elf_probes.py'), ELF] +
                        [f'{k}={v}' for k, v in PROBES.items() if k not in ('critMsg', 'cfgMsg')] +
                        ['critMsg=@_ZL26criticalErrorMessageBuffer', 'cfgMsg=@_ZL24configErrorMessageBuffer'],
                        capture_output=True, text=True)
    if pr.returncode:
        sys.exit(pr.stderr)
    probes = json.loads(pr.stdout)
    for k in ('critMsg', 'cfgMsg'):
        probes[k].update(kind='bytes', size=64)
    for k, addr in REGS.items():
        probes[k] = dict(kind='reg32', addr=addr, size=4, scale=1)
    SENSORS.update(sensor_ids(ELF))
    total_fail = 0
    for year in args.years.split(','):
        out = os.path.join(args.out, year)
        os.makedirs(out, exist_ok=True)
        stim = write_stimulus(YEARS[year]['family'], out)
        resc = build_resc(year, out, probes, stim)
        t0 = time.time()
        log = run_renode(resc, 3600, os.path.join(out, 'renode.log'))
        samples = parse_log(log)
        phases = [(st[1], st[2]) for st in timeline(year, stim) if st[0] == 'run']
        json.dump(samples, open(os.path.join(out, 'samples.json'), 'w'))
        pins = read_pins(os.path.join(out, 'pins.txt')) if os.path.exists(os.path.join(out, 'pins.txt')) else {}
        chk = Checks()
        if not samples or samples[-1]['t'] < sum(d for _, d in phases) - 0.2:
            chk.add('all', 'run completed', False, 'Renode stopped early; see renode.log')
        try:
            analyse(year, samples, phases, pins, stim, chk)
        except Exception as e:  # report, don't hide
            chk.add('all', 'analysis', False, f'{type(e).__name__}: {e}')
        fails = sum(1 for r in chk.rows if r[2] == 'FAIL')
        total_fail += fails
        print(f'\n== {year}: {len(samples)} samples, {time.time() - t0:.0f} s wall, {fails} FAIL')
        for ph, what, st, det in chk.rows:
            print(f'  {st:5} {ph:8} {what}: {det}')
        json.dump(chk.rows, open(os.path.join(out, 'checks.json'), 'w'), indent=1)
    sys.exit(1 if total_fail else 0)


if __name__ == '__main__':
    main()
