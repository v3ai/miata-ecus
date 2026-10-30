"""1996-1997 Miata (NA8 OBD-II, BP-ZE 1.8) motherboard.

Header: TE 178780-1, 76 positions, OEM plugs 1 (22) | 2 (12, no harness plug) | 3 (16) | 4 (26).
Pin map: rusEFI wiki 1996 page, Hellen NA8-96 connector map and board netlist, DIY MSPNP Pro MM9697,
AMP and Haltech docs, Mazda TSB 006/98 (research notes: pinouts_9605.md in this release).
Crank and cam come from the cam-driven CAS (hall / open collector, 12 V fed) on 4F / 4G.
"""
import mb_later as L
from mb_later import OUTLINE, W, H, DAUGHTER
# the wide header covers where the NA case has its two top bosses: provisional board keeps the four side holes
CASE_HOLES = {k: v for k, v in L.CASE_HOLES.items() if k not in ('H1', 'H2')}

NAME = 'miata_mb_9697'
TITLE = 'Miata ECU motherboard 1996-1997 (NA8 OBD2)'
HDR_1A = (16.0, 18.13)
CASE_NOTE = L.CASE_NOTE_PROVISIONAL
HEADER_DESC = ('TE **178780-1**, 76 positions (alternates 174915-6, 3-178780-6): OEM plug 1 = 1A-1V (22), plug 2 = '
               '2A-2L (12, no harness plug: left open), plug 3 = 3A-3P (16), plug 4 = 4A-4Z (26). Hellen\'s board names '
               'the same cavities 1 / 4 / 2 / 3. Fitted by hand.')
CHANGES = ['Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.1: first release (design complete, case geometry provisional).']
VERIFY = ['**The case outline, mounting holes and header position (provisional here).**',
          'The 76-position header housing is 130 mm wide and reaches into the top-corner notches of the provisional (NA) outline; the real 1996-97 case must clear it.',
          '4E / 4H: the separate OBD-II crank-pulley sensor (VR) is left unconnected, as on every PnP board found; '
          'rusEFI uses the CAS signals on 4F / 4G.',
          '1O and 4A are tied to ground (sources agree they are grounds; power vs signal role unconfirmed).',
          '4I (possible battery backup), 4K, 1D, 1H, 1I, 1P, 3H, 3J, 3N, 3P and the other unidentified cavities are left open.',
          'Brake switch (1Q) is not read: the spare inputs are 0-5 V analog, not 12 V switch inputs.']

HARNESS = {
    '1A': 'OUT_FAN',     # cooling (radiator) fan relay
    '1B': 'OUT_LS7',     # fan No.2 / A/C condenser fan relay
    '1C': '', '1D': '',  # 1D: possibly diagnostic link - never drive
    '1E': 'OUT_CEL',     # MIL
    '1F': '',
    '1G': 'OUT_AC',      # A/C relay
    '1H': '', '1I': '', '1J': '',
    '1K': 'IN_SW2',      # A/C switch / refrigerant pressure switch
    '1L': 'IN_SW3',      # clutch switch
    '1M': 'IN_SW1',      # vehicle speed sensor
    '1N': '',
    '1O': 'GND',         # ground
    '1P': '', '1Q': '',  # 1Q: brake switch (12 V; not read)
    '1R': '',            # A/T only - never drive
    '1S': '', '1T': '',  # 1T: A/T only - never drive
    '1U': 'OUT_FP',      # fuel pump relay
    '1V': '',
    '3A': '',
    '3B': 'IN_AUX3',     # MAF signal
    '3C': 'IN_AUX2',     # front HO2S (narrowband)
    '3D': 'IN_AUX1',     # rear HO2S
    '3E': '',
    '3F': 'IN_TPS',      # throttle position sensor
    '3G': 'IN_CLT',      # coolant temperature sensor
    '3H': '',
    '3I': 'V5_SENS',     # +5 V sensor reference (TPS, MAF)
    '3J': '',
    '3K': 'HARN_IAT',    # intake air temperature sensor (fit R5 instead of R4 to use it)
    '3L': '',            # ground per one source only: left open
    '3M': 'OUT_VVT',     # front HO2S heater (PWM low side; no VVT on this engine)
    '3N': '',
    '3O': 'GND',         # sensor ground (BLK/BLU)
    '3P': '',
    '4A': 'GND',         # ground
    '4B': 'VBAT_IN',     # ECU +12 V from the main relay (WHT/RED)
    '4C': 'GND', '4D': 'GND',
    '4E': '',            # crank-pulley OBD-II sensor lead - not used
    '4F': 'IN_HALL1',    # CAS 4-pulse crank angle (SGT), hall / open collector
    '4G': 'IN_HALL2',    # CAS 2-pulse cam (SGC), hall / open collector
    '4H': '',            # crank-pulley OBD-II sensor lead - not used
    '4I': '',            # possibly battery backup - never drive
    '4J': '', '4K': '',
    '4L': 'OUT_TACH',    # tachometer
    '4M': '',
    '4N': 'OUT_IGN1',    # igniter cylinders 1 & 4
    '4O': '', '4P': '',
    '4Q': 'OUT_IACV',    # idle air control valve (low side)
    '4R': 'OUT_IGN2',    # igniter cylinders 2 & 3
    '4S': '', '4T': '',
    '4U': 'OUT_INJ1', '4V': 'OUT_INJ2', '4W': 'OUT_INJ3', '4X': 'OUT_INJ4',
    '4Y': '',
    '4Z': '',            # rear HO2S heater (not driven)
}
for k in 'ABCDEFGHIJKL':
    HARNESS.setdefault('2' + k, '')


def build_parts():
    return L.build('ecu_mb:TE_178780-1_76P', 'TE 178780-1', 'Stock harness header, 76 positions (OEM plugs 1/3/4 used). '
                   'Hand-solder; salvage from a stock ECU or use a clone', HARNESS, holes=CASE_HOLES)


def placement():
    return L.place(HDR_1A)
