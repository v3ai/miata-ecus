"""1999-2000 Miata (NB1, BP-4W 1.8) motherboard.

Header: TE 176122-6 (4-174518-7), 64 positions: plugs 1 (22) | 2 (16) | 3 (26).
Pin map: rusEFI wiki 1999 page (3M/3O swap corrected), Hellen NB1 connector map, board netlist and its
'OEM ECU pin' sheet, DIY MSPNP Pro MM9900, Alex Engineering Speeduino NB manual, Haltech, 2005 FSM.
Crank (2J) and cam (2H) are 3-wire hall sensors fed +12 V from the main relay.
"""
import mb_later as L
from mb_later import OUTLINE, W, H, DAUGHTER
# the wide header covers where the NA case has its two top bosses: provisional board keeps the four side holes
CASE_HOLES = {k: v for k, v in L.CASE_HOLES.items() if k not in ('H1', 'H2')}

NAME = 'miata_mb_9900'
TITLE = 'Miata ECU motherboard 1999-2000 (NB1)'
HDR_1A = (16.0, 18.13)
CASE_NOTE = L.CASE_NOTE_PROVISIONAL
HEADER_DESC = ('TE **178780-1**, 76 positions, the same header as the 1996-97 board (rev 0.8; the car\'s own header is '
               'the 64-position 176122-6, whose three plugs are the same housings): plug 1 = 1A-1V (22), plug 2 = 2A-2P '
               '(16), plug 3 = 3A-3Z (26). The 12-position bay between plugs 1 and 2 has no harness plug and is not '
               'connected. Fitted by hand.')
CHANGES = ["Rev 0.7, for daughterboard rev 0.9: the daughterboard sits 16 mm lower, centred on the board (42 mm from the top, as up to rev 0.7), with its J1 on its top edge again: JD1 and the upper standoffs HD1/HD2 are back at their rev 0.7 places, JD2, the lower standoffs HD3/HD4, the AUX header J5 (with F4 beside it) and the parts placed against JD2 (CAN termination R1/R6, pull-up options) are 16 mm lower, and the board is routed again. Not compatible with a rev 0.8 daughterboard.", "Rev 0.6, for daughterboard rev 0.8: the harness's sensor 5 V (2I) and the AUX header pin J5-14 now come from the daughterboard's protected 5 V (V5_EXT, JD1 pin 13, which was a ground pin): a sensor 5 V wire shorted to the battery no longer back-feeds the MAP sensor and the ECU's own 5 V. The MAP sensor keeps its own supply (V5_SENS). The daughterboard outline on the silkscreen is 16 mm taller (125 x 76 mm): its new strip of output drivers overhangs the free area above JD1.",
           "Rev 0.5: LSU heater fuse F1 is a 3 A hold PTC (LUTE 2920L300/30GR, 30 V, 2920 size) instead of the 2 A 1812 part. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's warm-up, more than the old fuse holds once warm, so it could trip and the controller time out. No 1812 PTC holds 3 A above 8 V.",
           'Rev 0.4: freewheel diode D1 on the idle valve to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.',
           'Rev 0.3: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.1: first release (design complete, case geometry provisional).']
VERIFY = ['**The case outline, mounting holes and header position (provisional here).**',
          '2K: tach output per three sources, "unused" per one; check on the harness.',
          '3O feeds +12 V to the idle valve through F2 (2 A resettable).',
          '3Q (VICS solenoid) is driven by the spare relay-driver channel (OUT_MAINRLY net, a ZXMS6004FF since daughterboard rev 0.8): the main relay itself is key-switched on NB1.',
          '1U (front O2 heater) uses the PWM low side normally used for VVT (NB1 has no VVT).',
          'Left open: 1A (battery backup), 1D/1L (diagnostic link), 1K/1N (A/T), 1T (alternator sense), 1H, 3K, 3P (EU fuel pump), '
          'the EGR stepper (2M-2P), purge (3L), CDCV (3U), rear O2 heater (3V), brake / power-steering / neutral switches.']

HARNESS = {
    '1A': '',            # battery backup - never drive
    '1B': 'VBAT_IN',     # ECU +12 V from the main relay
    '1C': '', '1D': '',  # 1D: data link connector - never drive
    '1E': 'OUT_CEL',     # MIL
    '1F': '',            # brake switch (12 V; not read)
    '1G': '',            # power steering pressure switch (not read)
    '1H': '',
    '1I': 'OUT_LS7',     # A/C (condenser) fan relay
    '1J': '', '1K': '', '1L': '', '1M': '', '1N': '',   # 1K/1N: A/T, 1L: DLC - never drive
    '1O': 'OUT_ALT',     # alternator field coil control (PWM)
    '1P': 'IN_SW2',      # A/C switch
    '1Q': '',            # charge warning lamp (not driven)
    '1R': 'OUT_FAN',     # radiator cooling fan relay
    '1S': 'OUT_AC',      # A/C compressor relay
    '1T': '',            # alternator sense - never drive
    '1U': 'OUT_VVT',     # front HO2S heater (PWM low side; no VVT on NB1)
    '1V': '',            # neutral switch (not read)
    '2A': '',            # fuel tank pressure sensor (not read)
    '2B': 'IN_IAT',      # intake air temperature sensor (in the air filter box)
    '2C': 'IN_AUX2',     # front HO2S
    '2D': 'IN_SW1',      # vehicle speed sensor
    '2E': 'IN_CLT',      # coolant temperature
    '2F': 'IN_KNOCK',    # knock sensor
    '2G': '',
    '2H': 'IN_HALL2',    # cam position sensor (hall, 3-wire)
    '2I': 'V5_EXT',      # +5 V sensor reference
    '2J': 'IN_HALL1',    # crank position sensor (hall, 3-wire)
    '2K': 'OUT_TACH',    # tachometer
    '2L': 'IN_AUX3',     # MAF signal
    '2M': '', '2N': '', '2O': '', '2P': '',             # EGR stepper (not driven)
    '3A': 'GND', '3B': 'GND', '3C': 'GND',              # power grounds
    '3D': '',
    '3E': 'IN_TPS',      # throttle position sensor
    '3F': 'GND',         # sensor ground
    '3G': 'OUT_IGN1',    # igniter cylinders 1 & 4
    '3H': 'OUT_IGN2',    # igniter cylinders 2 & 3
    '3I': 'IN_SW3',      # clutch switch
    '3J': 'IN_AUX1',     # rear HO2S
    '3K': '', '3L': '',  # 3L: purge solenoid (not driven)
    '3M': 'OUT_IACV',    # idle air control valve (low side)
    '3N': 'OUT_FP',      # fuel pump relay
    '3O': 'IAC_12V',     # idle valve +12 V supply (fused, F2)
    '3P': '',            # fuel pump relay, EU cars with immobilizer - left open
    '3Q': 'OUT_MAINRLY', # VICS solenoid (spare relay-driver channel)
    '3R': '', '3S': '', '3T': '', '3U': '', '3V': '',
    '3W': 'OUT_INJ1', '3X': 'OUT_INJ2', '3Y': 'OUT_INJ3', '3Z': 'OUT_INJ4',
}
FUSES = [('F2', 'IAC_12V', 'idle valve +12 V feed (3O)')]


def build_parts():
    parts = L.build('ecu_mb:TE_178780-1_76P_NB1', 'TE 178780-1', 'Harness header, 76 positions (the 22-, 16- and 26-position '
                    'bays take the car\'s three plugs; the 12-position bay stays empty). Hand-solder',
                    dict(HARNESS, **{'X' + k: '' for k in 'ABCDEFGHIJKL'}), FUSES, holes=CASE_HOLES)
    L.C.protection_parts('IAC_12V')
    return parts


def placement():
    return L.C.protection_place(L.place(HDR_1A, [f[0] for f in FUSES]), vvt=False)
