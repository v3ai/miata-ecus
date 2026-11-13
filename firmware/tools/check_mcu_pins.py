#!/usr/bin/env python3
"""Check the daughterboard's processor pin map against ST's own pin data.

Source of truth: research/st/STM32F407V(E-G)Tx.xml, ST's machine-readable pin description for the STM32F407VGT6 in
LQFP100 (github.com/STMicroelectronics/STM32_open_pin_data, BSD-3-Clause; the data STM32CubeMX uses). For every
processor pad in scripts/design.py this checks
  - the pin number carries the pin we think it does (and scripts/stm32f407v_lqfp100_pins.txt, the hand-made table the
    other tools use, agrees with ST on all 100 pins);
  - supply, ground, VCAP, reset and boot nets sit on pins of that kind, and no supply pin of the package is left open;
  - the peripheral signal a net needs exists on its pin (CAN2, USB, SPI, USART, SWD, oscillator, an ADC channel), and
    the three SPI lines belong to one SPI, the two UART lines to one UART;
  - the interrupt-driven inputs sit on different EXTI lines (the line number is the pin's number within its port);
  - nothing but an input-only or slow function sits on the backup-domain pins PC13-PC15 (3 mA in total, 2 MHz).
Exits non-zero on any mismatch.

usage: firmware/tools/check_mcu_pins.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'scripts')
sys.path.insert(0, SCRIPTS)
cwd = os.getcwd()
os.chdir(SCRIPTS)
import design  # noqa: E402
os.chdir(cwd)

NS = {'m': 'http://dummy.com'}
root = ET.parse(os.path.join(ROOT, 'research', 'st', 'STM32F407V(E-G)Tx.xml')).getroot()
assert root.get('Package') == 'LQFP100' and root.get('RefName') == 'STM32F407V(E-G)Tx', root.attrib
ST = {int(p.get('Position')): (p.get('Name'), p.get('Type'), [s.get('Name') for s in p.findall('m:Signal', NS)])
      for p in root.findall('m:Pin', NS)}
assert len(ST) == 100

errors, notes = [], []


def port(name):
    """'PH0-OSC_IN' / 'PA0-WKUP' / 'PB2-BOOT1' -> 'PH0' / 'PA0' / 'PB2'."""
    m = re.match(r'P[A-K]\d+', name)
    return m.group(0) if m else name


# ---- the hand-made pin table against ST --------------------------------------------------------------------------
local = {int(n): name for n, name in
         (line.split(':') for line in open(os.path.join(SCRIPTS, 'stm32f407v_lqfp100_pins.txt')).read().split())}
for n in range(1, 101):
    st = port(ST[n][0])
    lo = local.get(n)
    same = lo == st or (lo or '').replace('_', '').upper() == st.replace('_', '').replace('+', '').upper() \
        or (lo or '').upper().rstrip('+') == st.upper().rstrip('+')
    if not same:
        errors.append(f'pin table: pin {n} is {lo!r} in stm32f407v_lqfp100_pins.txt, ST says {ST[n][0]!r}')

# ---- every pad of U1 -----------------------------------------------------------------------------------------------
mcu = {int(k): v for k, v in design.mcu.items()}
POWER = {'VDD': '+3V3', 'VBAT': '+3V3', 'VDDA': '+3V3A', 'VREF+': '+3V3A', 'VSS': 'GND', 'VSSA': 'GND',
         'VCAP_1': 'VCAP1', 'VCAP_2': 'VCAP2', 'NRST': 'NRST', 'BOOT0': 'BOOT0'}
for n, (name, typ, sigs) in sorted(ST.items()):
    net = mcu.get(n)
    if name in POWER:
        if net != POWER[name]:
            errors.append(f'pin {n} ({name}) must be on {POWER[name]}, design has {net!r}')
    elif net in set(POWER.values()) - {'NRST', 'BOOT0'}:
        errors.append(f'pin {n} ({name}) is an I/O pin but the design ties it to {net}')

# net (regex) -> signal (regex) it needs on its pin
NEED = [
    (r'CAN_RX$', r'CAN2_RX$'), (r'CAN_TX$', r'CAN2_TX$'),
    (r'USB_DM$', r'USB_OTG_FS_DM$'), (r'USB_DP$', r'USB_OTG_FS_DP$'),
    (r'SD_SCK$', r'SPI\d_SCK$'), (r'SD_MISO$', r'SPI\d_MISO$'), (r'SD_MOSI$', r'SPI\d_MOSI$'),
    (r'WB_PROG_TX$', r'US?ART\d_TX$'), (r'WB_PROG_RX$', r'US?ART\d_RX$'),
    (r'SWDIO$', r'SYS_JTMS-SWDIO$'), (r'SWCLK$', r'SYS_JTCK-SWCLK$'),
    (r'HSE_IN$', r'RCC_OSC_IN$'), (r'HSE_OUT$', r'RCC_OSC_OUT$'),
    (r'BOOT1$', r'.*'),
    (r'AN_KNOCK$', r'ADC3_IN\d+$'),          # rusEFI's software knock runs on ADC3
    (r'AN_', r'ADC1_IN\d+$'),
]
found = {}
for n, net in sorted(mcu.items()):
    name, typ, sigs = ST[n]
    if name in POWER:
        continue
    for pat, sig in NEED:
        if re.match(pat, net):
            hit = [s for s in sigs if re.match(sig, s)]
            if net == 'BOOT1':
                if port(name) != 'PB2':
                    errors.append(f'BOOT1 is on pin {n} ({name}); BOOT1 is PB2')
            elif not hit:
                errors.append(f'{net} on pin {n} ({name}): no {sig} there (has: {" ".join(sigs)})')
            found[net] = (n, name, hit)
            break
    else:
        if 'GPIO' not in sigs:
            errors.append(f'{net} on pin {n} ({name}) is not a GPIO pin')
        found[net] = (n, name, [])


def same_unit(nets, what):
    units = []
    for net in nets:
        if net in found:
            units.append({re.match(r'[A-Z]+\d', s).group(0) for s in found[net][2]})
    if units and not set.intersection(*units):
        errors.append(f'{what}: {nets} are not on one peripheral: {units}')
    elif units:
        notes.append(f'{what}: ' + ', '.join(f'{n}={found[n][1]}' for n in nets if n in found)
                     + f' -> {sorted(set.intersection(*units))}')


same_unit(['SD_SCK', 'SD_MISO', 'SD_MOSI'], 'microSD SPI')
same_unit(['WB_PROG_TX', 'WB_PROG_RX'], 'wideband programming UART')

# interrupt-driven inputs: one EXTI line per pin number
EXTI_NETS = ['HALL1', 'HALL2', 'SW1', 'VR1_OUT', 'VR2_OUT', 'FLEX_M']
lines = {}
for net in EXTI_NETS:
    if net in found:
        ln = int(re.search(r'\d+$', port(found[net][1])).group(0))
        if ln in lines:
            errors.append(f'{net} ({found[net][1]}) shares EXTI line {ln} with {lines[ln]}')
        lines[ln] = f'{net} ({found[net][1]})'
notes.append('EXTI lines: ' + ', '.join(f'{ln}: {v}' for ln, v in sorted(lines.items())))

# backup-domain pins: PC13-PC15 are fed through the backup power switch (3 mA in total, 2 MHz, 30 pF: ST DS8626, GPIO
# notes). Only slow, lightly loaded nets may sit there
SLOW_OK = {'FP_CTL', 'MAINRLY_CTL', 'LS7_CTL', 'AC_CTL', 'FAN_CTL', 'CEL_CTL', 'TACH_CTL', 'N2O_ARM_M'}
for n, net in mcu.items():
    if port(ST[n][0]) in ('PC13', 'PC14', 'PC15'):
        if net not in SLOW_OK:
            errors.append(f'{net} is on backup-domain pin {ST[n][0]} (3 mA total, 2 MHz): only slow relay lines allowed')
        notes.append(f'backup-domain pin {ST[n][0]}: {net}')
# pins with a reset-time function worth knowing about
for n, net in mcu.items():
    p = port(ST[n][0])
    if p in ('PA15', 'PB3', 'PB4'):
        notes.append(f'{p} ({net}) is a JTAG pin after reset (PA15/PB4 pulled up, PB3 floating) until the firmware '
                     f'remaps it: its driver must stay disabled through reset')

unused = [f'{port(ST[n][0])}({n})' for n in sorted(ST) if n not in mcu and ST[n][1] == 'I/O']
print(f'{len(mcu)} processor pads checked against ST pin data ({root.get("RefName")}, {root.get("Package")})')
for s in notes:
    print('  note:', s)
print('  free I/O pins:', ' '.join(unused))
if errors:
    print('MISMATCHES:')
    for e in errors:
        print('  ' + e)
    sys.exit(1)
print('OK: every pad matches')
