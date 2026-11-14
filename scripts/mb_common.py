"""Things shared by every year-specific motherboard: the daughterboard mating headers,
USB-C, MAP sensor, IAT and LSU connectors, CAN termination and the AUX header. Each year module adds its harness header, outline, holes and pin mapping."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import design as daughter

import os as _os
MBLIB = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'mb', 'ecu_mb.pretty'))

parts = []
SILK = {}      # jumper silkscreen: ref -> (name, {pad number: position label}); filled by the year modules


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
    # 2026-11-02 (rev 0.7 / 0.5): 3 A hold. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's
    # warm-up ramp, above the old 2 A hold (about 1.6 A once the board is at 60 C), so the PTC could trip and the
    # controller time out. No 1812 part holds 3 A at more than 8 V, so this is the 2920 size (LUTE 2920L300/30GR,
    # 3 A hold / 5 A trip, 30 V).
    add('F1', '3A hold', 'Fuse:Fuse_2920_7451Metric', 'C22446884', {1: 'VBAT_IN', 2: 'HTR_PWR'},
        'Resettable fuse for the LSU heater supply (LUTE 2920L300/30GR: 3 A hold, 5 A trip, 30 V)')
    # The wideband connector takes AEM's X-Series sensor harness (30-3427), 8 positions. AEM's instructions for the
    # 30-0300 gauge (documents 10-0300, 2017 and 10-0400, 2022) give the pin functions (1 trim, 2 heater -, 3 common,
    # 5 pump, 6 sense, 8 heater +) and name the replacement terminal: JST SPUD-001T-P0.5. That is the contact of JST's
    # PUD series (2.0 mm pitch, two rows, locking; housing PUDP-08V-S), so the board header is the PUD side-entry
    # header S08B-PUDSS-1. (Up to 1989-95 rev 0.12 / the others' rev 0.8 this was a Molex Micro-Fit 3.0 2x4, a guess
    # that was wrong.) JST numbers the circuits 1/2 in the first column, odd numbers in the row away from the mating
    # face; that AEM's pin numbers are JST's is not stated by AEM: the wire colours are on the silkscreen to check.
    add('J2', 'AEM 30-3427', 'Connector_JST:JST_PUD_S08B-PUDSS-1_2x04_P2.00mm_Horizontal', '',
        {1: 'LSU_RT', 2: 'LSU_HTR_N', 3: 'LSU_VM', 4: '', 5: 'LSU_IP', 6: 'LSU_UN', 7: '', 8: 'HTR_PWR'},
        'Wideband sensor harness AEM 30-3427 (to a Bosch LSU 4.9). JST PUD side-entry header S08B-PUDSS-1. AEM pin: '
        '1 trim (RT, green), 2 heater - (white), 3 common (VM, orange), 5 pump (IP, red), 6 sense (UN, black), '
        '8 heater + (brown); 4 and 7 empty')
    # Rev 0.10: no air-temperature connector or jumper any more: the stock sensor wire goes straight to the input
    # (year modules map their air-temperature cavity to IN_IAT).

    # Rev 0.10: the CAN bus (shared with the on-board wideband, 500 kbit/s) now leaves the board on J5-19/20 for gauges;
    # R1 / R6 above are its terminator.
    # flex-fuel sensor (open-collector 50-150 Hz output) and nitrous arming switch (12 V or 5 V = armed)
    add('R35', '4.7k', 'Resistor_SMD:R_0603_1608Metric', 'C23162', {1: 'V5_EXT', 2: 'IN_FLEX'}, 'Flex-fuel sensor signal pull-up to 5 V')
    add('R36', '10k', 'Resistor_SMD:R_0603_1608Metric', 'C25804', {1: 'IN_N2O', 2: 'GND'},
        'Nitrous arming input pull-down: an open wire reads "not armed"')
    add('D5', 'SS34', 'Diode_SMD:D_SMA', 'C8678', {1: 'AUX_VBAT', 2: 'OUT_BOOST'},
        'Boost valve freewheel diode to the AUX +12 V pin (feed the valve from J5-15)')

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
    # Rev 0.10: 20 pins. 1-11 and 14-16 as before; 12/13 were a spare UART and are now the flex-fuel and nitrous
    # arming inputs; 17/18 ground, 19/20 CAN. The nitrous relay coil goes on any free driver (J5-5 on most years).
    add('J5', 'AUX 2x10', 'Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical', '', AUX,
        'Add-on I/O: COP 3/4, boost, alternator, main relay, knock, VR crank/cam, external AFR, flex-fuel sensor, nitrous '
        'arming switch, CAN for gauges, 5 V, +12 V (fused, F4)')
    # The AUX +12 V pin leaves the board, so it has its own resettable fuse. Rev 0.10: 1.1 A hold (0.5 A before): a
    # boost valve (about 0.45 A), a flex sensor and a nitrous relay coil together stay under it.
    add('F4', '1.1A hold', 'Fuse:Fuse_1812_4532Metric', 'C883150', {1: 'VBAT_IN', 2: 'AUX_VBAT'},
        'Resettable fuse for the AUX +12 V pin J5-15 (BHFUSE BSMD1812-110-33V: 1.1 A hold, 2.2 A trip, 33 V, 1812; the '
        'daughterboard\'s F1 is the same part)')


AUX = {1: 'OUT_IGN3', 2: 'OUT_IGN4', 3: 'OUT_BOOST', 4: 'OUT_ALT', 5: 'OUT_MAINRLY', 6: 'IN_KNOCK',
       7: 'VR1_P', 8: 'VR1_N', 9: 'VR2_P', 10: 'VR2_N', 11: 'IN_AFR', 12: 'IN_FLEX', 13: 'IN_N2O',
       14: 'V5_EXT', 15: 'AUX_VBAT', 16: 'GND', 17: 'GND', 18: 'GND', 19: 'CAN_H', 20: 'CAN_L'}


def protection_parts(iac_supply, vvt_supply=None):
    """Freewheel diodes for the PWM valve coils (idle valve always; VVT driver only where it drives a coil) to the
    valve's own +12 V feed, and not-fitted 12 V pull-up options for the three switch inputs."""
    add('D1', 'SS34', 'Diode_SMD:D_SMA', 'C8678', {1: iac_supply, 2: 'OUT_IACV'},
        f'Idle valve freewheel diode (to its +12 V feed, {iac_supply}): keeps the PWM turn-off energy out of the driver')
    if vvt_supply:
        add('D2', 'SS34', 'Diode_SMD:D_SMA', 'C8678', {1: vvt_supply, 2: 'OUT_VVT'},
            f'VVT-driver coil freewheel diode (to its +12 V feed, {vvt_supply})')
    for ref, net, what in (('R20', 'IN_SW1', 'vehicle speed'), ('R21', 'IN_SW2', 'A/C switch'),
                           ('R22', 'IN_SW3', 'clutch switch')):
        add(ref, '4.7k', 'Resistor_SMD:R_0603_1608Metric', '', {1: 'VBAT_IN', 2: net},
            f'NOT FITTED: 12 V pull-up for the {what} input. Fit (4.7k 0603, LCSC C23162: 48 mW at 15 V with the '
            'switch closed) only if your car\'s signal switches to ground or is open collector; a switch that drives '
            '12 V must not have it')


def protection_place(P, vvt=True):
    """Under the daughterboard: freewheel diodes below their JD1 pins, pull-up options above their JD2 pins,
    the AUX fuse beside J5."""
    dx, dy = 14.5, 42.0                       # every year board puts the daughterboard here
    pin = lambda k: dx + 13.0 + (k - 1) * 2.54
    P['D1'] = (pin(31), dy + 10.0, 90)
    if vvt:
        P['D2'] = (pin(34), dy + 10.0, 90)
    import placement as dpl
    for ref, k in (('R20', 15), ('R21', 16), ('R22', 17)):
        P[ref] = (pin(k), dy + dpl.J2_Y - 5.25, 90)
    P['F4'] = (100.0, dy + dpl.BOARD_H + 11.0, 0)          # beside J5
    P['D5'] = (101.0, dy + dpl.BOARD_H + 5.0, 0)           # boost valve freewheel diode, above F4
    # flex pull-up and arming pull-down: between JD2 and the AUX header
    P['R35'] = (70.0, dy + dpl.BOARD_H + 4.0, 0)
    P['R36'] = (76.0, dy + dpl.BOARD_H + 4.0, 0)
    return P


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


YEAR_NAME = {'mb_na6': '1989-95', 'mb_na96': '1996-97', 'mb_nb1': '1999-2000', 'mb_nb2': '2001-05'}


def fab_prefix(module, rev):
    """Prefix of a motherboard's fab files, e.g. miata-ecu-motherboard-1989-93-rev0.9_"""
    return f'miata-ecu-motherboard-{YEAR_NAME.get(module, module)}-rev{rev}_'
