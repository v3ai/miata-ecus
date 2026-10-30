"""2001-2005 Miata (NB2, BP-Z3 1.8 S-VT) motherboard.

Header: TE 353830-5 (alt. 1123038-2), 72 positions: OEM plugs 2 (17) | 3 (24) | 4 (31), three rows.
Pin map: 2005 Mazda workshop manual PCM terminal tables (primary), Hellen NB2 connector map and board
netlist, rusEFI wiki 2002/2003 pages, Haltech NB2. Crank (3Y) and cam (3V) are 3-wire hall sensors.
2003-05: the PCM drives the main relay (3H) and reads IG1 on 4S; 2001-02: key-switched relay, both unused.
"""
import mb_later as L
from mb_later import OUTLINE, CASE_HOLES, W, H, DAUGHTER

NAME = 'miata_mb_0105'
TITLE = 'Miata ECU motherboard 2001-2005 (NB2, VVT)'
BUS = False                     # three irregular rows: the general router wires the header
HDR_1A = (40.95, 16.6)          # terminal 2A (inner row, first column); outer row 8 mm further out
CASE_NOTE = L.CASE_NOTE_PROVISIONAL
HEADER_DESC = ('TE **353830-5** (alt. 1123038-2), 72 positions in three rows: OEM plug 2 = 2A-2R without 2L (17), '
               'plug 3 = 3A-3Z without 3G/3R (24), plug 4 = 4A-4AH without 4G/4Q/4Y (31). There is no plug 1. Fitted by hand.')
CHANGES = ['Rev 0.4: freewheel diode D1 on the idle valve and D2 on the VVT valve to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.',
           'Rev 0.3: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.1: first release (design complete, case geometry provisional).']
VERIFY = ['**The case outline, mounting holes and header position (provisional here).**',
          'Mazdaspeed (turbo) cars: 4R is the second IAT sensor input there, not the VVT valve: do not fit this board unmodified.',
          '2P (idle valve +) and 4D (VVT valve +) are fed +12 V through F2 / F3 (2 A resettable each).',
          '3H drives the main relay on 2003-05 (unused on 2001-02); 4S reads the ignition switch on 2003-05.',
          'Left open: 3Q (K-line), 3S (immobilizer), 4E (DLC TEN), 4Z/4AC (A/T), 4AD (fuel gauge), 4AG (battery backup), '
          '4T (generator voltage), the EGR stepper (2E/2F/2H/2I), purge (3C), 3D, 3E, 3K, VTCS (2N, 4J), O2 heaters (3J, 3P), '
          'generator lamp (3U), brake / power-steering / neutral switches, EGR boost sensor (4AE), 4AB, 4AH.']

HARNESS = {
    '2A': 'OUT_INJ1',    # injector No.1
    '2B': 'OUT_FAN',     # cooling fan relay
    '2C': 'OUT_LS7',     # condenser fan relay
    '2D': 'OUT_INJ2',    # injector No.2
    '2E': '', '2F': '',  # EGR stepper (not driven)
    '2G': 'OUT_INJ3',    # injector No.3
    '2H': '', '2I': '',  # EGR stepper (not driven)
    '2J': 'OUT_INJ4',    # injector No.4
    '2K': 'OUT_AC',      # A/C relay
    '2M': 'OUT_FP',      # fuel pump relay
    '2N': '',            # VTCS solenoid (not driven)
    '2O': '',
    '2P': 'IAC_12V',     # idle valve +12 V supply (fused, F2)
    '2Q': 'OUT_IACV',    # idle valve (low side)
    '2R': 'OUT_CEL',     # MIL
    '3A': 'GND',         # injector (power) ground
    '3B': 'GND',         # PCM ground
    '3C': '', '3D': '', '3E': '',
    '3F': 'OUT_IGN1',    # igniter cylinders 1 & 4
    '3H': 'OUT_MAINRLY', # main relay control (2003-05; unused on 2001-02)
    '3I': 'OUT_IGN2',    # igniter cylinders 2 & 3
    '3J': '', '3K': '', '3L': '',
    '3M': 'OUT_ALT',     # generator field coil control
    '3N': '',
    '3O': 'OUT_TACH',    # tachometer (shared with the A/T TCM)
    '3P': '', '3Q': '', '3S': '',   # 3Q: K-line, 3S: immobilizer - never drive
    '3T': 'IN_SW1',      # vehicle speed
    '3U': '',            # generator warning lamp (not driven)
    '3V': 'IN_HALL2',    # cam position sensor (hall)
    '3W': '', '3X': '',
    '3Y': 'IN_HALL1',    # crank position sensor (hall)
    '3Z': '',
    '4A': 'GND',         # device ground (CKP return)
    '4B': '', '4C': '',  # brake / power-steering switches (not read)
    '4D': 'OCV_12V',     # VVT oil control valve +12 V supply (fused, F3)
    '4E': '',            # DLC TEN - never drive
    '4F': 'IN_SW2',      # A/C refrigerant pressure switch
    '4H': '',            # neutral switch (not read)
    '4I': 'IN_SW3',      # clutch switch
    '4J': '', '4K': '',
    '4L': 'V5_SENS',     # +5 V reference
    '4M': 'IN_KNOCK',    # knock sensor
    '4N': 'HARN_IAT',    # intake air temperature (IAT jumper JP1 on STOCK to use it)
    '4O': 'GND',         # analogue sensor ground
    '4P': 'IN_CLT',      # coolant temperature
    '4R': 'OUT_VVT',     # VVT oil control valve (low side, PWM)
    '4S': 'VIGN_IN',     # IG1 ignition switch sense (2003-05)
    '4T': '', '4U': '',
    '4V': 'IN_TPS',      # throttle position sensor
    '4W': 'IN_AUX2',     # front HO2S
    '4X': 'IN_AUX3',     # MAF signal
    '4Z': '',            # A/T - never drive
    '4AA': 'IN_AUX1',    # rear HO2S
    '4AB': '', '4AC': '', '4AD': '', '4AE': '',
    '4AF': 'VBAT_IN',    # ECU +12 V from the main relay
    '4AG': '',           # battery backup - never drive
    '4AH': '',
}
# 3B (GND) ends up boxed in by bus lanes on both layers, so the pour can't reach it: tie it to 3A on B.Cu
GND_TIES = [('J1', '3B', '3A', 'B')]
FUSES = [('F2', 'IAC_12V', 'idle valve +12 V feed (2P)'), ('F3', 'OCV_12V', 'VVT valve +12 V feed (4D)')]


def build_parts():
    parts = L.build('ecu_mb:TE_353830-5_72P', 'TE 353830-5', 'Stock harness header, 72 positions (3 rows). Hand-solder; '
                    'salvage from a stock ECU or use a clone', HARNESS, FUSES)
    L.C.protection_parts('IAC_12V', 'OCV_12V')
    return parts


def placement():
    return L.C.protection_place(L.place(HDR_1A, [f[0] for f in FUSES]), vvt=True)
