"""Things shared by every year-specific motherboard: the daughterboard mating headers,
USB-C, MAP sensor, IAT and LSU connectors, CAN termination and the AUX header. Each year module adds its harness header, outline, holes and pin mapping."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import design as daughter

import os as _os
MBLIB = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'mb', 'ecu_mb.pretty'))

parts = []


def add(ref, value, fp, lcsc, pads, desc='', side='F'):
    parts.append(dict(ref=ref, value=value, fp=fp, lcsc=lcsc, pads={str(k): v for k, v in pads.items()},
                      desc=desc, side=side))


def common_parts():
    """Everything except the harness header and the case holes."""
    # daughterboard sockets: same pin numbers and nets as the daughter's J1/J2
    add('JD1', 'Socket 1x40 (daughter J1)', 'Connector_PinSocket_2.54mm:PinSocket_1x40_P2.54mm_Vertical', 'C124412',
        daughter.J1, '2.54 mm 1x40 female, 8.5 mm. Mates with the daughterboard J1 (power + outputs)')
    add('JD2', 'Socket 1x40 (daughter J2)', 'Connector_PinSocket_2.54mm:PinSocket_1x40_P2.54mm_Vertical', 'C124412',
        {k: ('GND' if v == 'HTR_GND' else v) for k, v in daughter.J2.items()}, '2.54 mm 1x40 female, 8.5 mm. Mates with the daughterboard J2 (inputs + comms)')
    for i in range(4):
        add(f'HD{i + 1}', 'M3 standoff', 'MountingHole:MountingHole_3.2mm_M3', '', {},
            'Daughterboard standoff, M3 x 11 mm (8.5 mm socket + 2.5 mm header plastic)')

    # CAN bus termination at the ECU end (the wideband controller now lives on the daughterboard)
    add('R1', '120', 'Resistor_SMD:R_0603_1608Metric', 'C22787', {1: 'CAN_H', 2: 'CAN_T'}, 'CAN termination')
    add('R6', '0R', 'Resistor_SMD:R_0603_1608Metric', 'C21189', {1: 'CAN_T', 2: 'CAN_L'},
        'CAN termination link: fitted = 120R terminator active; remove if the bus is terminated elsewhere')
    # LSU 4.9 sensor connector: signals and heater low side go to the daughterboard's
    # on-board wideband controller; the heater is fed from the main relay through F1
    add('F1', '2A hold', 'Fuse:Fuse_1812_4532Metric', 'C46641168', {1: 'VBAT_IN', 2: 'HTR_PWR'},
        'Resettable fuse for the LSU heater supply (R+O SMD1812-200-30: 2 A hold, 30 V)')
    add('J2', 'LSU 4.9', 'Connector_Molex:Molex_Micro-Fit_3.0_43045-0600_2x03_P3.00mm_Horizontal', 'C127367',
        {1: 'LSU_IP', 2: 'LSU_VM', 3: 'LSU_HTR_N', 4: 'HTR_PWR', 5: 'LSU_RT', 6: 'LSU_UN'},
        'Bosch LSU 4.9 wideband sensor. Pin n = LSU pin n: 1 IP, 2 VM, 3 H-, 4 H+, 5 RT, 6 UN')

    # IAT: open-element sensor with M12x1.5 thread, 2 wires
    add('J3', 'IAT', 'Connector_Molex:Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal', 'C587650',
        {1: 'IAT_EXT', 2: 'GND'}, 'Intake air temperature sensor (M12x1.5 thermistor, 2 wires)')
    add('R4', '0R', 'Resistor_SMD:R_0603_1608Metric', 'C21189', {1: 'IAT_EXT', 2: 'IN_IAT'},
        'IAT source: fitted = onboard IAT connector (default)')
    add('R5', '0R', 'Resistor_SMD:R_0603_1608Metric', '', {1: 'HARN_IAT', 2: 'IN_IAT'},
        'IAT source: fit instead of R4 to use the stock harness / AFM air temperature sensor (not fitted)')

    # MAP
    add('U2', 'MPX5700AP', MBLIB.split('/')[-1].replace('.pretty', '') + ':MPX5700AP_867B_Flat', 'C90152',
        {1: 'IN_MAP', 2: 'GND', 3: 'V5_SENS', 4: '', 5: '', 6: ''},
        'MAP sensor, 15-700 kPa absolute, single barbed port (case 867B). Lies flat, marking up, leads bent 90 deg, 2x M3 screws')
    add('C1', '1u', 'Capacitor_SMD:C_0603_1608Metric', 'C15849', {1: 'V5_SENS', 2: 'GND'}, 'MAP supply')
    add('C2', '10n', 'Capacitor_SMD:C_0603_1608Metric', 'C57112', {1: 'V5_SENS', 2: 'GND'}, 'MAP supply')
    add('C3', '470p', 'Capacitor_SMD:C_0603_1608Metric', 'C1620', {1: 'IN_MAP', 2: 'GND'}, 'MAP output filter')

    # USB-C (device, 5 V sink)
    usb = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'A4': 'USB_VBUS', 'A9': 'USB_VBUS',
           'B4': 'USB_VBUS', 'B9': 'USB_VBUS', 'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_DP', 'B6': 'USB_DP',
           'A7': 'USB_DM', 'B7': 'USB_DM', 'A8': '', 'B8': '', 'S1': 'GND'}
    add('J4', 'USB-C', 'ecu_mb:USB_C_GCT_USB4105_16P', 'C3020560', usb,
        'USB-C for tuning and firmware (USB 2.0 FS)')
    add('R2', '5.1k', 'Resistor_SMD:R_0603_1608Metric', 'C23186', {1: 'USB_CC1', 2: 'GND'}, 'USB-C sink CC1')
    add('R3', '5.1k', 'Resistor_SMD:R_0603_1608Metric', 'C23186', {1: 'USB_CC2', 2: 'GND'}, 'USB-C sink CC2')
    add('U4', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', 'C7519',
        {1: 'USB_DP', 2: 'GND', 3: 'USB_DM', 4: 'USB_DM', 5: 'USB_VBUS', 6: 'USB_DP'}, 'USB ESD protection')

    # AUX: everything the stock harness has no pin for
    aux = {1: 'OUT_IGN3', 2: 'OUT_IGN4', 3: 'OUT_BOOST', 4: 'OUT_ALT', 5: 'OUT_MAINRLY', 6: 'IN_KNOCK',
           7: 'VR1_P', 8: 'VR1_N', 9: 'VR2_P', 10: 'VR2_N', 11: 'IN_AFR', 12: 'UART_TX', 13: 'UART_RX',
           14: 'V5_SENS', 15: 'VBAT_IN', 16: 'GND'}
    add('J5', 'AUX 2x8', 'Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical', 'C3406', aux,
        'Add-on I/O: COP 3/4, boost, alternator, main relay, knock, VR crank/cam, external AFR, UART, 5 V, +12 V')


def trigger_select(refs, sig, rtn, hall, vr_p, vr_n, default, label):
    """Crank/cam input that works with either sensor type, picked by which 0R links are fitted:
       hall: sig -> hall input (the daughterboard has the pull-up)
       vr:   sig -> VR+ and rtn -> VR- (rtn = the sensor's return pin, or GND if it has none)
    refs = three resistor refs (hall, vr+, vr-). Only the default option is assembled."""
    r_h, r_p, r_n = refs
    fit = lambda opt: 'C21189' if default == opt else ''
    add(r_h, '0R', 'Resistor_SMD:R_0603_1608Metric', fit('hall'), {1: sig, 2: hall},
        f'{label}: hall sensor link (fit for a hall / open-collector sensor)')
    add(r_p, '0R', 'Resistor_SMD:R_0603_1608Metric', fit('vr'), {1: sig, 2: vr_p},
        f'{label}: VR sensor + link (fit with {r_n} for a 2-wire magnetic sensor)')
    add(r_n, '0R', 'Resistor_SMD:R_0603_1608Metric', fit('vr'), {1: rtn, 2: vr_n},
        f'{label}: VR sensor - link (fit with {r_p})')


def nets():
    out = []
    for p in parts:
        for n in p['pads'].values():
            if n and n not in out:
                out.append(n)
    return out
