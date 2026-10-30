"""1989-1993 Miata (NA6, B6ZE 1.6) motherboard.

Stock case: the NA 48-pin case (same case for 1990-95). Outline and holes from the rusEFI
microRusEFI NA PnP board (fits this case) and the early Hellen NA6 board (same Mazda case
family). Harness header TE 174917-6: plug 1 = 1A-1V (22), plug 2 = 2A-2Z (26).
(rusEFI's 1990 / Hellen pages call the 26-pin plug "3A-3Z".)
"""
import math
import mb_common as C

NAME = 'miata_mb_8993'
TITLE = 'Miata ECU motherboard 1989-1993 (NA6)'
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
CHANGES = ['Rev 0.6: freewheel diode D1 on the idle valve and D2 on the purge solenoid (2X) to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs. INJ1+INJ4 drive 2U and INJ2+INJ3 drive 2V in parallel (R23/R24), with an SMCJ40A clamp per wire (D3/D4), so no driver carries two injectors; 2Y/2Z are only reached through the not-fitted sequential-conversion links R25/R26.',
           'Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.3: sensor 5 V now on both 1N (NA6, per the Hellen NA6 map) and 2K; spare low side on 1R (the early cars\' '
           'BLK/GRN fan-relay wire); 2S left open (it is only used on 94-95).',
           'Rev 0.2: wideband controller moved to the daughterboard; J5 centred; MAP sensor rotated 90 deg clockwise; LSU '
           'connector 6 mm right; SWD header removed; heater fuse now 30 V rated.']
VERIFY = ['The case geometry: hole centres and header 1A position, with calipers on a stock case.',
          'Your car\'s fan wiring: early cars switch the fan relay on 1R, later ones on 1L; both are driven (fan and spare outputs).',
          'LCSC stock for the extended parts (C124412, C127367, C587650, C3020560, C410772, C46641168, C3406).']
HDR_1A = (39.7, 18.13)        # pad 1A of the 174917 (lower row); header centred on the board
DAUGHTER = (14.5, 42.0)       # daughterboard top-left corner on this board

# ---- stock harness -> daughterboard signal map (Mazda pin names)
HARNESS = {
    # plug 1, 22 pins
    '1A': '',            # constant +12 V (memory): not used, the ECU runs off the main relay
    '1B': 'VBAT_IN',     # main relay output: ECU power
    '1C': 'VIGN_IN',     # ignition switch
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
    '1N': 'V5_SENS',     # sensor 5 V ref on NA6 (Hellen NA6 map); 2K carries it too
    '1O': '',            # brake light switch
    '1P': '',            # power steering switch
    '1Q': 'IN_SW2',      # A/C switch
    '1R': 'OUT_LS7',     # A/C extra cooling fan relay (BLK/GRN) on 1990-91; moved to 1L on later cars
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
    '2I': 'OUT_TACH',
    '2J': '',
    '2K': 'V5_SENS',     # 5 V sensor reference
    '2L': 'IN_AUX1',     # MT idle switch (TPS) / spare analog
    '2M': 'IN_TPS',      # TPS signal (AT / VTPS conversion)
    '2N': 'IN_AUX2',     # stock narrowband O2
    '2O': 'IN_AUX3',     # AFM flap signal
    '2P': 'HARN_IAT',    # AFM air temp (IAT jumper JP1 on STOCK to use it)
    '2Q': 'IN_CLT',
    '2R': '',
    '2S': '',            # unused on 1990-93 (94-95: condenser fan relay)
    '2T': 'OUT_FP',      # fuel pump relay
    '2U': 'OUT_INJ1',    # stock: two injectors on this wire (batch); INJ1 + INJ4 drive it in parallel (R23)
    '2V': 'OUT_INJ2',    # stock: the other two injectors (batch); INJ2 + INJ3 in parallel (R24)
    '2W': 'OUT_IACV',
    '2X': 'OUT_VVT',     # purge solenoid (VVT driver reused, set as purge / generic PWM)
    '2Y': 'HARN_2Y',     # empty on manual cars: INJ3 only through R25 (not fitted) after a sequential conversion
    '2Z': 'HARN_2Z',     # A/T control unit on automatics: INJ4 only through R26 (not fitted), never on an automatic
}


def build_parts(harness=None, paired_injectors=True):
    C.parts.clear()
    C.add('J1', 'TE 174917-6', 'ecu_mb:TE_174917-6_48P', '', harness or HARNESS,
          'Stock harness header, 48 pins (22 + 26). Hand-solder; salvage from a stock ECU or use a clone')
    for ref in CASE_HOLES:
        C.add(ref, 'M4', 'ecu_mb:MountingHole_M4_4.5mm_Pad7', '', {1: 'GND'}, 'Case mounting boss, M4 x 10')
    C.common_parts()
    # idle valve 2W and purge solenoid 2X: both fed from the main relay
    C.protection_parts('VBAT_IN', 'VBAT_IN')
    if paired_injectors:
        injector_pairs()
    return C.parts


def injector_pairs():
    """1989-93 batch harness: each injector wire (2U, 2V) feeds two injectors, about 1.8 A. Two drivers share each
    wire (rusEFI's batch mode fires cylinder 1's and 4's outputs together, and 3's and 2's), so each driver carries
    one injector's current, and a TVS per wire takes the turn-off energy that the drivers' own clamps would
    otherwise absorb. Moving the links (R23/R24 out, R25/R26 in) gives a sequential conversion its own 2Y/2Z
    drivers instead; never fit R26 on an automatic (2Z is the A/T control unit)."""
    r0805 = 'Resistor_SMD:R_0805_2012Metric'
    C.add('R23', '0R', r0805, 'C17477', {1: 'OUT_INJ4', 2: 'OUT_INJ1'},
          'Batch: INJ4 driver in parallel with INJ1 on 2U (remove for a sequential conversion)')
    C.add('R24', '0R', r0805, 'C17477', {1: 'OUT_INJ3', 2: 'OUT_INJ2'},
          'Batch: INJ3 driver in parallel with INJ2 on 2V (remove for a sequential conversion)')
    C.add('R25', '0R', r0805, '', {1: 'OUT_INJ3', 2: 'HARN_2Y'},
          'NOT FITTED: sequential conversion only, INJ3 to 2Y (fit instead of R24)')
    C.add('R26', '0R', r0805, '', {1: 'OUT_INJ4', 2: 'HARN_2Z'},
          'NOT FITTED: sequential conversion only, INJ4 to 2Z (fit instead of R23). NEVER on an automatic: 2Z is the A/T unit')
    for ref, net, pin in (('D3', 'OUT_INJ1', '2U'), ('D4', 'OUT_INJ2', '2V')):
        C.add(ref, 'SMCJ40A', 'Diode_SMD:D_SMC', 'C224052', {1: net, 2: 'GND'},
              f'Injector clamp for the two injectors on {pin} (40 V standoff, about 45-50 V clamp, below the drivers\' 63 V)')


def placement():
    dx, dy = DAUGHTER
    P = {'J1': (HDR_1A[0], HDR_1A[1], 0)}
    P.update({k: (x, y, 0) for k, (x, y) in CASE_HOLES.items()})
    # daughterboard sockets: pin 1 under daughter J1/J2 pin 1, pins run +x -> rotate -90
    P['JD1'] = (dx + 13.0, dy + 2.75, 90)
    P['JD2'] = (dx + 13.0, dy + 57.25, 90)
    for i, (hx, hy) in enumerate([(4.5, 4.5), (120.5, 4.5), (4.5, 55.5), (120.5, 55.5)]):
        P[f'HD{i + 1}'] = (dx + hx, dy + hy, 0)
    # CAN termination right under the daughterboard's CAN pins (JD2 27/28)
    P['R1'] = (dx + 13.0 + 26.5 * 2.54 - 0.9, dy + 61.6, 90)
    P['R6'] = (dx + 13.0 + 26.5 * 2.54 + 0.9, dy + 61.6, 90)
    # bottom edge, left to right: LSU, IAT, USB-C, MAP. Connector mouths at the edge.
    P['J2'] = (29.0, 152.3, 180)       # LSU 4.9 (moved 6 mm right in rev 0.2)
    P['F1'] = (44.0, 143.0, 90)
    P['J3'] = (55.0, 152.3, 180)
    P['JP1'] = (52.46, 145.0, 90)      # IAT source jumper: pins 1 (STOCK) .. 3 (EXT) left to right
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
    P['J5'] = ('centre', W / 2, 113.0, -90)
    C.protection_place(P)
    # 1989-93 injector pairing links and clamps, under the daughterboard between JD1's injector pins
    P['R23'] = (84.6, 49.0, 0)
    P['R24'] = (84.6, 53.0, 0)
    P['R25'] = (90.0, 57.5, 0)
    P['R26'] = (96.0, 57.5, 0)
    P['D3'] = (72.0, 64.0, 0)
    P['D4'] = (86.0, 64.0, 0)
    return P
