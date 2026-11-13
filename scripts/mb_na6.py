"""1989-1995 Miata (NA6 B6ZE 1.6 and NA8 BP 1.8) motherboard. Rev 0.12 merges the 1989-93 and 1994-95 boards: same
case, same header, and the few pins that differ are on jumpers (see JUMPERS).

Stock case: the NA 48-pin case (same case for 1990-95). Outline and holes from the rusEFI
microRusEFI NA PnP board (fits this case) and the early Hellen NA6 board (same Mazda case
family). Harness header TE 174917-6: plug 1 = 1A-1V (22), plug 2 = 2A-2Z (26).
(rusEFI's 1990 / Hellen pages call the 26-pin plug "3A-3Z".)
"""
import math
import mb_common as C

NAME = 'miata_mb_8995'
TITLE = 'Miata ECU motherboard 1989-1995 (NA6 / NA8)'
W, H = 154.0, 161.5

# ---- outline: Mazda NA case, notched corners (all mm, origin top-left, y down)
# (kind, start, end, centre) arcs; concave notch arcs bulge into the board
OUTLINE = [
    ('L', (15.5, 0.0), (138.5, 0.0)),
    ('A', (138.5, 0.0), (141.5, 3.0), (138.5, 3.0)),
    ('L', (141.5, 3.0), (141.5, 3.5)),
    ('A', (141.5, 3.5), (147.5, 9.5), (147.5, 3.5)),
    ('L', (147.5, 9.5), (151.0, 9.5)),
    ('A', (151.0, 9.5), (154.0, 12.5), (151.0, 12.5)),
    ('L', (154.0, 12.5), (154.0, 146.0)),
    ('A', (154.0, 146.0), (151.0, 149.0), (151.0, 146.0)),
    ('L', (151.0, 149.0), (148.5, 149.0)),
    ('A', (148.5, 149.0), (142.5, 155.0), (148.5, 155.0)),
    ('L', (142.5, 155.0), (142.5, 159.0)),
    ('A', (142.5, 159.0), (140.0, 161.5), (140.0, 159.0)),
    ('L', (140.0, 161.5), (14.0, 161.5)),
    ('A', (14.0, 161.5), (11.5, 159.0), (14.0, 159.0)),
    ('L', (11.5, 159.0), (11.5, 155.0)),
    ('A', (11.5, 155.0), (5.5, 149.0), (5.5, 155.0)),
    ('L', (5.5, 149.0), (3.0, 149.0)),
    ('A', (3.0, 149.0), (0.0, 146.0), (3.0, 146.0)),
    ('L', (0.0, 146.0), (0.0, 12.5)),
    ('A', (0.0, 12.5), (3.0, 9.5), (3.0, 12.5)),
    ('L', (3.0, 9.5), (6.5, 9.5)),
    ('A', (6.5, 9.5), (12.5, 3.5), (6.5, 3.5)),
    ('L', (12.5, 3.5), (12.5, 3.0)),
    ('A', (12.5, 3.0), (15.5, 0.0), (15.5, 3.0)),
]

# case bosses, M4. J27-J32 are the microRusEFI NA PnP names.
CASE_HOLES = {
    'H1': (17.0, 7.3),     # J27, recessed boss: stack 3 M4 washers under the board
    'H2': (137.0, 7.3),    # J28
    'H3': (4.0, 84.0),     # J29
    'H4': (150.0, 84.0),   # J30
    'H5': (4.0, 143.0),    # J31
    'H6': (150.0, 143.0),  # J32
}

CASE_NOTE = ('Stock NA case (same for 1990-95). Outline and holes come from the rusEFI microRusEFI NA plug-and-play '
             'board, which fits this case, measured against its known 48-pin header footprint, and from the early Hellen '
             'NA6 KiCad board (rev a/b), which uses the same Mazda case outline. H1 is a recessed boss: stack 3 M4 washers under the board.')
HEADER_DESC = ('TE **174917-6**, 48 pins: plug 1 = 1A-1V (22 pins), plug 2 = 2A-2Z (26 pins); rusEFI\'s 1990 page calls the '
               'second plug 3A-3Z. TE lists it as not currently available: desolder one from a stock ECU or use a clone. Fitted by hand.')
CHANGES = ["Rev 0.11, for daughterboard rev 0.9: the throttle position sensor conversion uses the stock throttle switch plug, as rusEFI's Hellen NA6 and MRE boards do, instead of rev 0.10's separate lead: J6 is gone. Harness pin 1N (the manual cars' idle contact) is no longer wired straight to the sensor 5 V: it goes through R28 (0R, not fitted), so a car with the stock switch no longer shorts the 5 V to ground at every idle (rev 0.10 and earlier did, if 1N is the idle contact as the rusEFI sources say). Pin 2L goes through R29 (0R, fitted) to the spare analog AUX1 as before, or through R30 (0R, not fitted) to the TPS input. For a sensor on the stock plug: fit R28, move R29 to R30. The links are hand-routed into the rev 0.9 copper; nothing else moved.", "Rev 0.10 (replaced by 0.11): J6, a 4-pin connector for a separate TPS lead.", "Rev 0.9, for daughterboard rev 0.9: the daughterboard sits 16 mm lower, centred on the board (42 mm from the top, as up to rev 0.7), with its J1 on its top edge again: JD1 and the upper standoffs HD1/HD2 are back at their rev 0.7 places, JD2, the lower standoffs HD3/HD4, the AUX header J5 (with F4 beside it) and the parts placed against JD2 (CAN termination R1/R6, pull-up options) are 16 mm lower, and the board is routed again. Not compatible with a rev 0.8 daughterboard.", "Rev 0.8, for daughterboard rev 0.8: the harness's sensor 5 V (1N, 2K) and the AUX header pin J5-14 now come from the daughterboard's protected 5 V (V5_EXT, JD1 pin 13, which was a ground pin): a sensor 5 V wire shorted to the battery no longer back-feeds the MAP sensor and the ECU's own 5 V. The MAP sensor keeps its own supply (V5_SENS). The daughterboard outline on the silkscreen is 16 mm taller (125 x 76 mm): its new strip of output drivers overhangs the free area above JD1. D3/D4 (the batch injector clamps) are now SMCJ30A (33.3-36.8 V breakdown) instead of SMCJ40A: the new daughterboard drivers clamp at 40 V minimum, so a 40 V TVS could leave the turn-off energy in a driver; at 30 V the TVS always clamps first. Not-fitted option R27: 4.7k pull-up from the protected 5 V for the manual cars' TPS idle switch on 2L.",
           "Rev 0.7: LSU heater fuse F1 is a 3 A hold PTC (LUTE 2920L300/30GR, 30 V, 2920 size) instead of the 2 A 1812 part. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's warm-up, more than the old fuse holds once warm, so it could trip and the controller time out. No 1812 PTC holds 3 A above 8 V.",
           'Rev 0.6: freewheel diode D1 on the idle valve and D2 on the purge solenoid (2X) to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs. INJ1+INJ4 drive 2U and INJ2+INJ3 drive 2V in parallel (R23/R24), with an SMCJ40A clamp per wire (D3/D4), so no driver carries two injectors; 2Y/2Z are only reached through the not-fitted sequential-conversion links R25/R26.',
           'Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.3: sensor 5 V now on both 1N (NA6, per the Hellen NA6 map) and 2K; spare low side on 1R (the early cars\' '
           'BLK/GRN fan-relay wire); 2S left open (it is only used on 94-95).',
           'Rev 0.2: wideband controller moved to the daughterboard; J5 centred; MAP sensor rotated 90 deg clockwise; LSU '
           'connector 6 mm right; SWD header removed; heater fuse now 30 V rated.']
VERIFY = ['The case geometry: hole centres and header 1A position, with calipers on a stock case.',
          'Your car\'s fan wiring: early cars switch the fan relay on 1R, later ones on 1L; both are driven (fan and spare outputs).',
          'LCSC stock for the extended parts (C124412, C127367, C277684, C587650, C3020560, C410772, C46641168, C3406).',
          'Harness pins 1N and 2L on a 1989-93 car: with the throttle switch unplugged, which plug wire reaches each (the '
          'rusEFI sources give 1N = idle contact, 2D = ground, 2L = full-throttle contact). Do this before fitting R28.',
          'The TPS conversion on a manual car: the sensor and mount against your throttle body, and the sensor\'s output '
          'across the throttle travel (calibrate closed and wide open in TunerStudio).']
HDR_1A = (39.7, 18.13)        # pad 1A of the 174917 (lower row); header centred on the board
DAUGHTER = (14.5, 42.0)       # daughterboard top-left corner on this board

# ---- stock harness -> daughterboard signal map (Mazda pin names)
HARNESS = {
    # plug 1, 22 pins
    '1A': '',            # constant +12 V (memory): not used, the ECU runs off the main relay
    '1B': 'VBAT_IN',     # main relay output: ECU power
    '1C': 'VIGN_IN',     # starter (START) signal: battery only while cranking. Not ignition-on: the firmware doesn't use it as ignition sense
    '1D': '',            # diagnosis / data link
    '1E': 'OUT_CEL',
    '1F': '',
    '1G': 'OUT_IGN1',    # igniter 1&4 (wasted spark) / COP 1
    '1H': 'OUT_IGN2',    # igniter 2&3 (wasted spark) / COP 2
    '1I': '',
    '1J': 'OUT_AC',      # A/C relay
    '1K': '',
    '1L': 'OUT_FAN',     # radiator fan relay
    '1M': 'IN_SW1',      # vehicle speed sensor
    '1N': 'HARN_1N',     # manual cars: the stock throttle switch's idle contact (closes to ground at idle). 5 V only through R28 (not fitted), for a 0-5 V sensor on the stock plug
    '1O': '',            # brake light switch
    '1P': '',            # power steering switch
    '1Q': 'IN_SW2',      # A/C switch
    '1R': 'HARN_1R',     # A/C extra cooling fan relay (BLK/GRN) on 1990-91: second fan output through JP3 (position 90-93)
    '1S': '',
    '1T': '',
    '1U': '',
    '1V': 'IN_SW3',      # clutch switch
    # plug 2, 26 pins (rusEFI "3x")
    '2A': 'GND', '2B': 'GND',   # power ground
    '2C': 'GND', '2D': 'GND',   # signal ground
    '2E': 'IN_HALL1',    # CAS crank (SGT, open collector)
    '2F': 'GND',         # AFM ground
    '2G': 'IN_HALL2',    # CAS cam (SGC)
    '2H': '',
    '2I': 'HARN_2I',     # stock: the igniter's signal INTO the ECU (the igniter drives the tachometer itself). JP5 open.
                         # Coil-on-plug without the igniter: JP5 fitted, the ECU drives the tachometer through this wire
    '2J': '',
    '2K': 'V5_EXT',      # 5 V sensor reference (protected harness 5 V)
    '2L': 'HARN_2L',     # manual cars: the throttle switch's other contact. R29 (fitted) to the spare analog AUX1, or R30 (not fitted) to the TPS input after a sensor conversion
    '2M': 'IN_TPS',      # automatics' TPS signal (a manual car's converted sensor comes in on 2L through R30)
    '2N': 'IN_AUX2',     # stock narrowband O2
    '2O': 'HARN_2O',     # airflow meter signal. JP6: to the spare analog input (AFM), or the boost valve output on this wire once the meter is gone
    '2P': 'IN_IAT',      # air temperature sensor in the airflow meter
    '2Q': 'IN_CLT',
    '2R': 'HARN_2R',     # 1994-95: pressure regulator control solenoid, through JP4. Not connected on 1989-93
    '2S': 'HARN_2S',     # 1994-95: condenser fan relay, second fan output through JP3 (position 94-95)
    '2T': 'OUT_FP',      # fuel pump relay
    '2U': 'OUT_INJ1',    # 1989-93: two injectors on this wire (JP2 on PAIR adds the INJ4 driver). 1994-95: injector 1
    '2V': 'OUT_INJ2',    # 1989-93: the other two injectors (JP1 on PAIR adds the INJ3 driver). 1994-95: injector 2
    '2W': 'OUT_IACV',
    '2X': 'OUT_VVT',     # purge solenoid (VVT driver reused, set as purge / generic PWM)
    '2Y': 'HARN_2Y',     # 1994-95: injector 3 (JP1 on SEQ). 1989-93: empty until a sequential conversion
    '2Z': 'HARN_2Z',     # 1994-95: injector 4 (JP2 on SEQ). 1989-93: A/T control unit on automatics, never JP2 on SEQ there
}


# Jumpers (2.54 mm headers with shunts). (ref, pins, nets, silkscreen name, {pin: position label}, description)
JUMPERS = [
    ('JP1', 3, {1: 'OUT_INJ2', 2: 'OUT_INJ3', 3: 'HARN_2Y'}, 'INJ3', {1: 'PAIR', 3: 'SEQ'},
     'Injector 3 driver: PAIR = in parallel with INJ2 on 2V (1989-93 stock harness, two injectors per wire); '
     'SEQ = its own wire 2Y (1994-95, or a 1989-93 sequential conversion)'),
    ('JP2', 3, {1: 'OUT_INJ1', 2: 'OUT_INJ4', 3: 'HARN_2Z'}, 'INJ4', {1: 'PAIR', 3: 'SEQ'},
     'Injector 4 driver: PAIR = in parallel with INJ1 on 2U (1989-93 stock); SEQ = its own wire 2Z (1994-95, or a '
     '1989-93 sequential conversion). NEVER SEQ on a 1989-93 automatic: 2Z is the A/T control unit'),
    ('JP3', 3, {1: 'HARN_1R', 2: 'OUT_LS7', 3: 'HARN_2S'}, 'FAN2', {1: '90-93', 3: '94-95'},
     'Second fan relay output: 1R on 1990-93 (the 1990-91 A/C fan), 2S on 1994-95 (condenser fan)'),
    ('JP4', 2, {1: 'OUT_ALT', 2: 'HARN_2R'}, '94-95 2R', {},
     'Fit on 1994-95: the pressure regulator control solenoid on 2R. Leave open on 1989-93'),
    ('JP5', 2, {1: 'OUT_TACH', 2: 'HARN_2I'}, 'TACH COP', {},
     'Leave OPEN with the stock igniter: it drives the tachometer and sends its signal to the ECU on 2I. Fit only '
     'after a coil-on-plug conversion with the igniter removed: the ECU then drives the tachometer through 2I (R37 '
     'is its 12 V pull-up; join the two tach wires at the old igniter plug)'),
    ('JP6', 3, {1: 'IN_AUX3', 2: 'HARN_2O', 3: 'OUT_BOOST'}, '2O', {1: 'AFM', 3: 'BOOST'},
     'Airflow meter signal wire 2O: AFM = to the spare analog input (stock); BOOST = boost valve output on that wire '
     'once the meter is removed (valve between the old meter plug\'s signal pin and 12 V)'),
]


def build_parts(harness=None, idle_pullup=True, tps_links=True):
    C.parts.clear()
    C.add('J1', 'TE 174917-6', 'ecu_mb:TE_174917-6_48P', '', harness or HARNESS,
          'Stock harness header, 48 pins (22 + 26). Hand-solder')
    for ref in CASE_HOLES:
        C.add(ref, 'M4', 'ecu_mb:MountingHole_M4_4.5mm_Pad7', '', {1: 'GND'}, 'Case mounting boss, M4 x 10')
    C.common_parts()
    # idle valve 2W and purge solenoid 2X: both fed from the main relay
    C.protection_parts('VBAT_IN', 'VBAT_IN')
    for ref, n, pads, name, labels, desc in JUMPERS:
        C.add(ref, name, f'Connector_PinHeader_2.54mm:PinHeader_1x0{n}_P2.54mm_Vertical', 'C49257' if n == 3 else '',
              pads, desc + '. Shunt: 2.54 mm jumper cap (LCSC C5305), fitted by hand')
        C.SILK[ref] = (name, labels)
    # 1989-93 stock harness: two injectors on each of 2U and 2V. A TVS per wire takes their turn-off energy (about
    # 37.5 V at 1.8 A, below the VND7NV04 drivers' 40 V minimum clamp)
    for ref, net, pin in (('D3', 'OUT_INJ1', '2U'), ('D4', 'OUT_INJ2', '2V')):
        C.add(ref, 'SMCJ30A', 'Diode_SMD:D_SMC', 'C224048', {1: net, 2: 'GND'},
              f'Injector clamp for the two injectors on {pin} (1989-93); same part as the daughterboard\'s load-dump TVS D6')
    C.add('R37', '1k', 'Resistor_SMD:R_2512_6332Metric', '', {1: 'VBAT_IN', 2: 'OUT_TACH'},
          'Tachometer pull-up to 12 V for the coil-on-plug case (JP5 fitted): the stock tachometer needs it once the '
          'igniter is gone. 2512, 1 W (0.2 W at 14.4 V)')
    if idle_pullup:
        # 1989-93 2L: the manual cars' throttle switch contact closes to ground and has no pull-up of its own
        C.add('R27', '4.7k', 'Resistor_SMD:R_0603_1608Metric', '', {1: 'V5_EXT', 2: 'IN_AUX1'},
              'NOT FITTED: 5 V pull-up for the stock throttle switch contact on 2L (manual cars, R29 fitted). Fit (4.7k '
              '0603, LCSC C23162; 1.1 mA with the switch closed) to read the stock switch; never with a sensor on 2L')
    if tps_links:
        # rev 0.11: 1989-93 manual cars have a two-contact throttle switch, not a throttle position sensor. Its plug
        # has three wires: idle contact (1N), signal ground (2D) and the other contact (2L). Like rusEFI's Hellen NA6
        # and MRE boards, a 0-5 V sensor plugs into that stock plug: R28 puts the protected 5 V on 1N, and R30 (in
        # place of R29) takes 2L to the TPS input. Until then 1N is left open: with the stock switch fitted, 5 V on 1N
        # would be shorted to ground at every idle (rev 0.10 and earlier wired 1N straight to the sensor 5 V).
        r0805 = 'Resistor_SMD:R_0805_2012Metric'
        C.add('R28', '0R', r0805, '', {1: 'HARN_1N', 2: 'V5_EXT'},
              'NOT FITTED: TPS conversion only (manual cars): protected 5 V to 1N for a 0-5 V sensor on the stock plug. '
              'Never with the stock throttle switch: it shorts 1N to ground at idle')
        C.add('R29', '0R', r0805, 'C17477', {1: 'HARN_2L', 2: 'IN_AUX1'},
              'Stock: 2L to the spare analog input AUX1 (remove for a TPS conversion)')
        C.add('R30', '0R', r0805, '', {1: 'HARN_2L', 2: 'IN_TPS'},
              'NOT FITTED: TPS conversion only (manual cars): 2L to the TPS input, in place of R29. '
              'Never on an automatic: its sensor is on 2M')
    return C.parts


def placement():
    dx, dy = DAUGHTER
    P = {'J1': (HDR_1A[0], HDR_1A[1], 0)}
    P.update({k: (x, y, 0) for k, (x, y) in CASE_HOLES.items()})
    # daughterboard sockets: pin 1 under daughter J1/J2 pin 1, pins run +x -> rotate -90. Rev 0.9: the daughterboard
    # (125 x 76 mm) has J1 on its top edge and J2 on its bottom edge again, so JD2 and the lower standoffs sit 16 mm
    # lower than in rev 0.7 and the board is centred top to bottom
    import placement as dpl
    P['JD1'] = (dx + 13.0, dy + dpl.J1_Y, 90)
    P['JD2'] = (dx + 13.0, dy + dpl.J2_Y, 90)
    for i, (hx, hy) in enumerate(dpl.HOLES):
        P[f'HD{i + 1}'] = (dx + hx, dy + hy, 0)
    # CAN termination right under the daughterboard's CAN pins (JD2 27/28)
    P['R1'] = (dx + 13.0 + 26.5 * 2.54 - 0.9, dy + dpl.J2_Y + 4.35, 90)
    P['R6'] = (dx + 13.0 + 26.5 * 2.54 + 0.9, dy + dpl.J2_Y + 4.35, 90)
    # bottom edge, left to right: LSU, IAT, USB-C, MAP. Connector mouths at the edge.
    P['J2'] = (29.0, 152.3, 180)       # LSU 4.9 (moved 6 mm right in rev 0.2)
    P['F1'] = (44.0, 143.0, 90)
    P['J4'] = (80.0, 157.6, 0)
    P['R2'] = (73.5, 151.0, 90)
    P['R3'] = (86.5, 151.0, 90)
    P['U4'] = (80.0, 149.0, 0)
    # MAP: rotated 90 deg clockwise in rev 0.2 (port points into the board, leads on the
    # right), lying flat between the USB-C and the H6 boss; filter caps beside its pins
    P['U2'] = (124.0, 142.0, 90)
    P['C1'] = (143.6, 140.6, 90)
    P['C2'] = (143.6, 136.6, 90)
    P['C3'] = (143.6, 148.0, 90)
    # AUX box header, body centred on the board below the daughterboard (set in mb_build)
    P['J5'] = ('centre', W / 2, dy + dpl.BOARD_H + 11.0, -90)     # rev 0.9: 16 mm lower, with the daughterboard
    C.protection_place(P)
    # 1989-93 injector pairing links and clamps, under the daughterboard between JD1's injector pins
    # year / option jumpers in the band between the harness header and the daughterboard, where they can be reached
    # with the daughterboard fitted
    for ref, x in (('JP3', 22.0), ('JP5', 36.0), ('JP6', 96.0), ('JP4', 110.0), ('JP1', 120.0), ('JP2', 132.0)):
        if ref in C.SILK:
            P[ref] = (x, 29.5, 90)
    P['R37'] = (44.0, 36.5, 0)
    P['D3'] = (72.0, 64.0, 0)
    P['D4'] = (86.0, 64.0, 0)
    # 2L idle-switch pull-up option, above its JD2 pin (IN_AUX1 = J2 pin 9) like R20-R22
    P['R27'] = (DAUGHTER[0] + 13.0 + 8 * 2.54, DAUGHTER[1] + dpl.J2_Y - 5.25, 90)
    # rev 0.11 TPS links (positions set against the routed rev 0.9 copper; see VERIFICATION.md)
    P['R28'] = (58.2, 22.75, 0)      # just below the harness header, under 1N
    P['R29'] = (49.09, 102.5, 270)   # in a gap cut into the old 2L-AUX1 run
    P['R30'] = (42.5, 102.5, 180)    # between the 2L run and the TPS run
    return P
