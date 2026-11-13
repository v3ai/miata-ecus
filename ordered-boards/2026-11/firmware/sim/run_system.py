#!/usr/bin/env python3
"""Firmware-in-the-loop run of both microcontrollers together: the ECU (STM32F407: OpenBLT + rusEFI) and the
on-board wideband controller (STM32F103), as two Renode machines joined the way the daughterboard joins them:
USART3 + BOOT0 + NRST for programming, and the shared CAN bus.

The F103 starts blank, as on a new board. The run then does what a new board goes through:
  1. ECU boots, key on.
  2. The ECU's wideband flasher (TunerStudio button "Flash wideband over UART", here started by a hook) puts the
     F103 into its ROM bootloader, erases, writes and verifies the wideband image it carries, and restarts the F103.
  3. The engine runs (crank/cam pattern on the hall inputs); rusEFI lets the wideband heat the sensor; the
     wideband's LSU 4.9 plant (models/LsuSensor.cs) warms up, the pump loop closes, and the wideband reports lambda
     over CAN; rusEFI's lambda sensor must follow the exhaust lambda set in the plant (1.00, then 0.85, then 1.20).
Checks: flasher status and the F103 flash CRC against the image; the F103 running its new firmware; CAN bit timing of
both controllers; heater warm-up, sensor temperature and ESR in closed loop; pump current against the LSU curve;
rusEFI's lambda reading; no critical error on the ECU.

usage: run_system.py [--year 2003-05] [--out DIR]
Needs what run_ecu.py needs, plus the wideband ELF (WBO_ELF, default firmware/wideband/out/miata_wbo_f103.elf from
firmware/wideband/build.sh) and image (firmware/wideband/miata_wbo_f103.bin).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import zlib

import run_ecu as E

SIM = E.SIM
WB = os.path.join(os.path.dirname(SIM), 'wideband')
WBO_ELF = os.environ.get('WBO_ELF', os.path.join(WB, 'out/miata_wbo_f103.elf'))
WBO_BIN = os.path.join(WB, 'miata_wbo_f103.bin')

PHASES = [('keyOn', 2.0), ('flash', 12.0), ('warmup', 20.0), ('rich', 3.0), ('lean', 3.0)]
LAMBDA = {'keyOn': 1.0, 'flash': 1.0, 'warmup': 1.0, 'rich': 0.85, 'lean': 1.20}
FLASH_AT = 2.0   # start of the 'flash' phase


def build(year, out, probes, stim):
    y = E.YEARS[year]
    ecu = E.build_resc(year, out, probes, stim).replace('.resc', '')
    lines = open(ecu + '.resc').read().split('\n')
    # keep the ECU set-up (up to the first pin settings), drop its own timeline
    setup = []
    for l in lines:
        if l.startswith('adc SetPinVoltage'):
            break
        if l.startswith('include @') or l.startswith('using '):
            continue
        setup.append(l)
    flash_fn = E.symbol('startWidebandUartFlash()')
    main_loop = E.symbol('MainLoop::PeriodicTask(long long)')
    # "Flash wideband over UART" (a TunerStudio button; no USB model here): at the start of the flash phase, the next
    # call of rusEFI's main loop task (a thread, no lock held, as for TunerStudio commands) is turned into a call of
    # startWidebandUartFlash(); the hook is removed again right after, since a hook hit costs host time
    trigger = [f'cpu AddHook {main_loop:#x} "import sys; from Antmicro.Renode.Peripherals.CPU import RegisterValue; '
               f'go = not sys.__dict__.get(\'miata_flashed\'); sys.miata_flashed = True; '
               f'self.PC = RegisterValue.Create({flash_fn:#x} if go else self.PC.RawValue, 32)"',
               'emulation RunFor "0.01"', f'cpu RemoveHooksAt {main_loop:#x}']
    L = ['using sysbus']
    for m in ('STM32F4ADC', 'STM32F4DMA', 'TriggerWheel', 'PinRecorder', 'F103RomBootloader', 'CanSniffer',
              'STM32F1ADC', 'STM32F1Flash', 'LsuSensor', 'NvicRettobase', 'CortexMDwt', 'HostProbe', 'TimerCcrZero'):
        L.append(f'include @{SIM}/models/{m}.cs')
    # Serial execution: both machines run on one host thread, taking turns each time quantum. With a thread per
    # machine (Renode's default) the run froze at a random point (4.6-5.8 s) with neither CPU executing, a race in
    # Renode's cross-machine time synchronisation; one thread also makes the run deterministic.
    L += ['emulation SetGlobalSerialExecution true',
          'emulation SetGlobalAdvanceImmediately true', 'emulation CreateCANHub "can"',
          # the wideband machine: blank F103
          'mach create "wbo"',
          f'machine LoadPlatformDescription @{E.platform(["stm32f103_wbo.repl", "wbo_bench.repl"], out)}',
          'sysbus WriteDoubleWord 0x1FFFF7E0 0xFFFF0040',   # flash size 64 KB
          'sysbus WriteDoubleWord 0x1FFFF7E8 0x066DFF34', 'sysbus WriteDoubleWord 0x1FFFF7EC 0x34385111',
          'sysbus WriteDoubleWord 0x1FFFF7F0 0x43123329',
          f'sysbus LoadSymbolsFrom @{WBO_ELF}',
          'lsu LogEvery 0.05', 'lsu SetBattery 14.0', 'lsu SetLambda 1.0',
          'connector Connect sysbus.can1 can']
    # the ECU machine
    L += setup
    L += [f'machine LoadPlatformDescription @{E.platform("ecu_wbo_link.repl", out)}',
          'connector Connect sysbus.can2 can', 'connector Connect sniffer can',
          f'sniffer SetOutputFile "{os.path.join(out, "can.txt")}"',
          ]
    car = dict(vbat=14.0, key=True, tps_v=0.6, map_kpa=35, clt_ohm=240.0, iat_ohm=2000.0, maf_v=1.3, vign_mode=y['vign'])
    L += [f'adc SetPinVoltage "{p}" {v:.4f}' for p, v in E.car_pins(**{**car, 'vbat': 12.4, 'map_kpa': 100}).items()]
    t = 0.0
    for name, dur in PHASES:
        if name == 'warmup':
            L += [f'wheel LoadPattern @{stim["pattern"]} 720', 'wheel SetRpm 900', 'wheel Start']
            L += [f'adc SetPinVoltage "{p}" {v:.4f}' for p, v in E.car_pins(**car).items()]
        L += ['mach set "wbo"', f'lsu SetLambda {LAMBDA[name]}', 'mach set "ecu"']
        if name == 'flash':
            L += trigger
            dur -= 0.01
        L.append(f'emulation RunFor "{dur:.4f}"')
        t += dur
    size = os.path.getsize(WBO_BIN)
    L += [f'wboBootloader FlashCrc {size}', 'sniffer BitTiming "ecu" 0x40006800 42000000',
          'sniffer BitTiming "wbo" 0x40006400 24000000', 'rec Flush', 'quit']
    path = os.path.join(out, 'system.resc')
    open(path, 'w').write('\n'.join(L) + '\n')
    return path


def lsu_curve(lam):
    # Bosch LSU 4.9 data sheet table (pump current in mA by lambda), as in models/LsuSensor.cs
    lb = [0.650, 0.700, 0.750, 0.800, 0.822, 0.850, 0.900, 0.950, 0.970, 0.990, 1.003, 1.010, 1.050, 1.100, 1.132, 1.179, 1.429, 1.701, 1.990, 2.434, 3.413, 5.391, 7.506, 10.119, 100.0]
    ib = [-2.000, -1.602, -1.243, -0.927, -0.800, -0.652, -0.405, -0.183, -0.106, -0.040, 0.000, 0.015, 0.097, 0.193, 0.250, 0.329, 0.671, 0.938, 1.150, 1.385, 1.700, 2.000, 2.150, 2.250, 2.550]
    for i in range(1, len(lb)):
        if lam <= lb[i]:
            return ib[i - 1] + (ib[i] - ib[i - 1]) * (lam - lb[i - 1]) / (lb[i] - lb[i - 1])
    return ib[-1]


def analyse(log, samples, out, chk):
    bounds, t = {}, 0.0
    for n, d in PHASES:
        bounds[n] = (t, t + d)
        t += d
    lsu = [json.loads(m) for m in re.findall(r'LSU (\{.*\})', log)]
    json.dump(lsu, open(os.path.join(out, 'lsu.json'), 'w'))
    crit = [s for s in samples if s.get('crit')]
    chk.add('all', 'no critical error on the ECU', not crit, crit[0].get('critMsg') if crit else 'none')
    # flashing
    st = [(s['t'], s.get('wboStatus')) for s in samples if s.get('wboStatus')]
    seq = []
    for tt, v in st:
        if not seq or seq[-1][1] != v:
            seq.append((tt, v))
    chk.add('flash', 'flasher status sequence', 'INFO', ' -> '.join(f'{v} ({tt:.2f} s)' for tt, v in seq))
    done = [tt for tt, v in seq if v.startswith('done')]
    chk.add('flash', 'wideband flashed and verified', bool(done),
            f'done at {done[0] - FLASH_AT:.2f} s after start' if done else (seq[-1][1] if seq else 'no status'))
    want = '%08x' % zlib.crc32(open(WBO_BIN, 'rb').read())
    m = re.search(r'FLASHCRC (\d+) ([0-9a-f]{8})', log)
    chk.add('flash', 'F103 flash content = wideband image', bool(m) and m.group(2) == want,
            f'{m.group(2) if m else "?"} vs image {want}')
    for k in ('ecu', 'wbo'):
        mm = re.search(r'CANTIMING ' + k + r' (.*)', log)
        chk.add('can', f'{k} CAN bit timing', 'INFO', mm.group(1) if mm else 'not read')
    rates = [float(x) for x in re.findall(r'CANTIMING \w+ BTR=\S+ bitrate=(\d+)', log)]
    chk.add('can', 'both controllers at the same bit rate', len(rates) == 2 and abs(rates[0] - rates[1]) < 1,
            ' / '.join(f'{r:.0f}' for r in rates))
    # CAN traffic from the wideband
    frames = [l.split() for l in open(os.path.join(out, 'can.txt'))] if os.path.exists(os.path.join(out, 'can.txt')) else []
    ids = {}
    for f in frames:
        ids[f[1]] = ids.get(f[1], 0) + 1
    chk.add('can', 'frames on the bus by ID', 'INFO', ', '.join(f'{k}:{v}' for k, v in sorted(ids.items())[:20]))
    # sensor warm-up and loop
    a, b = bounds['warmup']
    pre = [x for x in lsu if x['heaterDuty'] > 0.005]
    chk.add('warmup', 'wideband preheat (condensation protection, before the engine runs)', 'INFO',
            f"from {pre[0]['t']:.2f} s at {100 * pre[0]['heaterDuty']:.1f} % duty" if pre else 'none')
    heat = [x for x in lsu if x['heaterDuty'] > 0.1]
    chk.add('warmup', 'wideband heats the sensor once the engine runs', bool(heat) and heat[0]['t'] >= a,
            f"from {heat[0]['t']:.2f} s (engine starts at {a:.1f} s)" if heat else 'never')
    end = [x for x in lsu if b - 2 <= x['t'] <= b]
    if end:
        T = sum(x['temp'] for x in end) / len(end)
        esr = sum(x['esr'] for x in end) / len(end)
        chk.add('warmup', 'sensor held at operating temperature', abs(T - 780) < 40, f'{T:.0f} C, ESR {esr:.0f} ohm (target 300)')
        hot = [x for x in lsu if a <= x['t'] and x['temp'] > 740]
        chk.add('warmup', 'warm-up time', 'INFO', f"{hot[0]['t'] - a:.1f} s to 740 C" if hot else 'not reached')
    for ph in ('warmup', 'rich', 'lean'):
        a, b = bounds[ph]
        lam = LAMBDA[ph]
        end = [x for x in lsu if b - 1.0 <= x['t'] <= b]
        if end:
            ip = sum(x['ip'] for x in end) / len(end)
            need = lsu_curve(lam)
            chk.add(ph, f'pump current at lambda {lam}', abs(ip - need) < 0.05 + 0.05 * abs(need),
                    f'{ip:.3f} mA (LSU curve {need:.3f} mA), Nernst {end[-1]["nernst"]:.3f} V')
        # mean over the phase's last second (rusEFI samples at 20 Hz; the wideband's reading carries the pump
        # loop's ripple, a few percent on the lean side), with the spread
        vals = [x['sLambda'] for x in samples if b - 1.0 <= x['t'] <= b and x.get('sLambda') is not None]
        got = sum(vals) / len(vals) if vals else None
        chk.add(ph, f'rusEFI lambda reading at {lam}', got is not None and abs(got - lam) < 0.02,
                f'{got:.3f} (mean of {len(vals)} readings, {min(vals):.3f} .. {max(vals):.3f})' if vals else 'no reading')


def main():
    E.crc_image()
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', default='2003-05')
    ap.add_argument('--out', default=os.path.join(SIM, 'out', 'system'))
    ap.add_argument('--reanalyse', action='store_true', help='check the renode.log already in --out, without a run')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    probes_args = [f'{k}={v}' for k, v in E.PROBES.items() if k not in ('critMsg', 'cfgMsg')]
    probes_args += ['critMsg=@_ZL26criticalErrorMessageBuffer', 'cfgMsg=@_ZL24configErrorMessageBuffer',
                    'wboStatus=@_ZN12_GLOBAL__N_19wboStatusE']
    pr = subprocess.run([sys.executable, os.path.join(SIM, 'tools/elf_probes.py'), E.ELF] + probes_args,
                        capture_output=True, text=True)
    if pr.returncode:
        sys.exit(pr.stderr)
    probes = json.loads(pr.stdout)
    for k in ('critMsg', 'cfgMsg'):
        probes[k].update(kind='bytes', size=64)
    probes['wboStatus'].update(kind='ptrstr')
    E.SENSORS.update(E.sensor_ids(E.ELF))
    stim = E.write_stimulus(E.YEARS[args.year]['family'], args.out)
    resc = build(args.year, args.out, probes, stim)
    t0 = time.time()
    if args.reanalyse:
        log = re.sub(r'\x1b\[[0-9;]*m', '', open(os.path.join(args.out, 'renode.log'), errors='replace').read())
    else:
        log = E.run_renode(resc, 4 * 3600, os.path.join(args.out, 'renode.log'))
    samples = E.parse_log(log)
    json.dump(samples, open(os.path.join(args.out, 'samples.json'), 'w'))
    chk = E.Checks()
    total = sum(d for _, d in PHASES)
    if not samples or samples[-1]['t'] < total - 0.3:
        chk.add('all', 'run completed', False, 'Renode stopped early; see renode.log')
    try:
        analyse(log, samples, args.out, chk)
    except Exception as e:
        chk.add('all', 'analysis', False, f'{type(e).__name__}: {e}')
    fails = sum(1 for r in chk.rows if r[2] == 'FAIL')
    print(f'== system run ({args.year}): {len(samples)} ECU samples, {time.time() - t0:.0f} s wall, {fails} FAIL')
    for ph, what, st, det in chk.rows:
        print(f'  {st:5} {ph:8} {what}: {det}')
    json.dump(chk.rows, open(os.path.join(args.out, 'checks.json'), 'w'), indent=1)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
