#!/usr/bin/env python3
"""Cross-check the firmware pin map against the daughterboard design.

Reads the MCU pin -> net map from scripts/design.py, then checks
  - every MIATA_* define in firmware/board/board_configuration.cpp,
  - the LED and wideband-link pins used in board_configuration.cpp / wideband_uart_flash.cpp / board.mk,
  - every pin in firmware/board/connectors/daughterboard.yaml (against the J1/J2 header nets too),
and exits non-zero on any mismatch.

usage: firmware/tools/check_pins.py   (from anywhere in the repo)
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'scripts')
BOARD = os.path.join(ROOT, 'firmware', 'board')

# design.py builds the whole netlist on import; it only needs its own folder on the path
sys.path.insert(0, SCRIPTS)
cwd = os.getcwd()
os.chdir(SCRIPTS)
import design  # noqa: E402
os.chdir(cwd)

pins = {int(n): name for n, name in
        (line.split(':') for line in open(os.path.join(SCRIPTS, 'stm32f407v_lqfp100_pins.txt')).read().split())}
port_net = {pins[int(p)]: net for p, net in design.mcu.items()}      # 'PB7' -> 'INJ1_CTL'
ADC = {**{f'EFI_ADC_{i}': f'PA{i}' for i in range(8)}, 'EFI_ADC_8': 'PB0', 'EFI_ADC_9': 'PB1',
       **{f'EFI_ADC_{10 + i}': f'PC{i}' for i in range(6)}}

errors = []


def port_of(token):
    """'Gpio::B7' / 'B7' / 'EFI_ADC_4' -> 'PB7' / 'PA4'."""
    token = token.strip()
    if token.startswith('EFI_ADC_'):
        return ADC[token]
    token = token.replace('Gpio::', '')
    return 'P' + token


def expect(where, token, nets):
    port = port_of(token)
    net = port_net.get(port)
    if net not in nets:
        errors.append(f'{where}: {token} is {port} = {net!r} on the board, expected one of {sorted(nets)}')


# --- board_configuration.cpp defines ---------------------------------------------------------------------------
DEFINES = {
    'IGN1': 'IGN1_CTL', 'IGN2': 'IGN2_CTL', 'IGN3': 'IGN3_CTL', 'IGN4': 'IGN4_CTL',
    'INJ1': 'INJ1_CTL', 'INJ2': 'INJ2_CTL', 'INJ3': 'INJ3_CTL', 'INJ4': 'INJ4_CTL',
    'IACV': 'IACV_CTL', 'VVT': 'VVT_CTL', 'BOOST': 'BOOST_CTL', 'ALT': 'ALT_CTL',
    'FP': 'FP_CTL', 'MAINRLY': 'MAINRLY_CTL', 'AC': 'AC_CTL', 'FAN': 'FAN_CTL', 'CEL': 'CEL_CTL',
    'TACH': 'TACH_CTL', 'LS7': 'LS7_CTL',
    'HALL1': 'HALL1', 'HALL2': 'HALL2', 'SW1': 'SW1', 'SW2': 'SW2', 'SW3': 'SW3',
    'IN_VBATT': 'AN_VBATT', 'IN_VIGN': 'AN_VIGN', 'IN_TPS': 'AN_TPS', 'IN_MAP': 'AN_MAP', 'IN_CLT': 'AN_CLT',
    'IN_IAT': 'AN_IAT', 'IN_AFR': 'AN_AFR', 'IN_AUX1': 'AN_AUX1', 'IN_AUX2': 'AN_AUX2', 'IN_AUX3': 'AN_AUX3',
}
cfg = open(os.path.join(BOARD, 'board_configuration.cpp')).read() + open(os.path.join(BOARD, 'miata_board.cpp')).read()
found = dict(re.findall(r'^#define MIATA_(\w+)\s+(\S+)', open(os.path.join(BOARD, 'miata_pins.h')).read(), re.M))
for name, net in DEFINES.items():
    if name not in found:
        errors.append(f'miata_pins.h: MIATA_{name} missing')
    else:
        expect(f'MIATA_{name}', found[name], {net})
for name in found:
    if name not in DEFINES:
        errors.append(f'miata_pins.h: MIATA_{name} is not checked by check_pins.py')

# LEDs, CAN, wideband link
leds = dict(re.findall(r'Gpio get(\w+)LedPin\(\) \{\s+return (Gpio::\w+);', cfg))
for led, net in (('Running', 'LED_RUN'), ('Comms', 'LED_COMM'), ('Warning', 'LED_WARN')):
    expect(f'get{led}LedPin', leds.get(led, 'Gpio::??'), {net})
mk = open(os.path.join(BOARD, 'board.mk')).read()
expect('LED_CRITICAL_ERROR_BRAIN_PIN', re.search(r'LED_CRITICAL_ERROR_BRAIN_PIN=(Gpio::\w+)', mk).group(1), {'LED_ERR'})
expect('can2TxPin', re.search(r'can2TxPin = (Gpio::\w+)', cfg).group(1), {'CAN_TX'})
expect('can2RxPin', re.search(r'can2RxPin = (Gpio::\w+)', cfg).group(1), {'CAN_RX'})
wbo = open(os.path.join(BOARD, 'wideband_uart_flash.cpp')).read()
for label, net in (('WBO BOOT0', 'WB_BOOT0'), ('WBO NRST', 'WB_NRST'), ('WBO prog TX', 'WB_PROG_TX'),
                   ('WBO prog RX', 'WB_PROG_RX')):
    expect(label, re.search(r'efiSetPadMode\("' + label + r'", (Gpio::\w+)', wbo).group(1), {net})
for pad, net in (('10', 'WB_BOOT0'), ('11', 'WB_NRST'), ('8', 'WB_PROG_TX'), ('9', 'WB_PROG_RX')):
    if not re.search(r'GPIOD, ' + pad + r'\b', wbo):
        errors.append(f'wideband_uart_flash.cpp: GPIOD pad {pad} ({net}) not used')
expect('knock_config.h', re.search(r'KNOCK_PIN_CH1 (Gpio::\w+)', open(os.path.join(BOARD, 'knock_config.h')).read()).group(1),
       {'AN_KNOCK'})

# --- connector yaml: MCU pin and daughterboard header net ------------------------------------------------------
HEADER_NET = {  # header net -> MCU net it is conditioned into
    'OUT_IGN1': 'IGN1_CTL', 'OUT_IGN2': 'IGN2_CTL', 'OUT_IGN3': 'IGN3_CTL', 'OUT_IGN4': 'IGN4_CTL',
    'IN_KNOCK': 'AN_KNOCK', 'IN_HALL1': 'HALL1', 'IN_HALL2': 'HALL2', 'IN_SW1': 'SW1', 'IN_SW2': 'SW2', 'IN_SW3': 'SW3',
    'VR1_P': 'VR1_OUT', 'VR2_P': 'VR2_OUT',
}
y = yaml.safe_load(open(os.path.join(BOARD, 'connectors', 'daughterboard.yaml')))
for p in y['pins']:
    ids = p['id'] if isinstance(p['id'], list) else [p['id']]
    ports = {port_of(i) for i in ids}
    if len(ports) != 1:
        errors.append(f'yaml {p["pin"]}: ids {ids} name different MCU pins')
        continue
    port = ports.pop()
    if 'pin' not in p:  # on-board signal, no header pin
        continue
    hdr, num = p['pin'].split('-')
    hnet = (design.J1 if hdr == 'J1' else design.J2)[int(num)]
    if hnet in HEADER_NET:
        want = HEADER_NET[hnet]
    elif hnet.startswith('OUT_'):
        want = hnet[len('OUT_'):] + '_CTL'
    else:
        want = 'AN_' + hnet[len('IN_'):]
    if port_net.get(port) != want:
        errors.append(f'yaml {p["pin"]} ({hnet}): {port} = {port_net.get(port)!r}, expected {want!r}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'pins OK: {len(found)} defines, {len(y["pins"])} connector entries, LEDs, CAN, knock and wideband link match design.py')
