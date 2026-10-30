"""1994-1995 Miata (NA8, BP 1.8) motherboard.

Same stock case and the same 48-pin TE 174917-6 header as 1990-93 (the microRusEFI NA PnP
board fits both), so outline, holes and placement are shared with mb_na6. Only the
harness pin functions differ (rusEFI "Mazda Miata 1994" pinout; its plug 2 = 2A-2Z).
"""
import mb_na6 as base
from mb_na6 import OUTLINE, CASE_HOLES, HDR_1A, DAUGHTER, W, H, placement

NAME = 'miata_mb_9495'
TITLE = 'Miata ECU motherboard 1994-1995 (NA8)'

BASES = ['mb_na6']
CASE_NOTE = base.CASE_NOTE
HEADER_DESC = base.HEADER_DESC
CHANGES = ['Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.3: first release, from the 89-93 rev 0.3 template: same case, outline, holes and 48-pin header; 94-95 pin map '
           '(rusEFI "Mazda Miata 1994" page and the Hellen NA6/94 connector map).']
VERIFY = ['The case geometry, as for 89-93: one stock case with calipers.',
          '1C (VIO): ignition-switch sense on the 1990 diagram, unlabelled on the 1994 page; it is only an input here (diode-isolated on the daughterboard).',
          'LCSC stock for the extended parts (C124412, C127367, C587650, C3020560, C410772, C46641168, C3406).']
HARNESS = dict(base.HARNESS)
HARNESS.update({
    '1N': '',            # 94-95: to the AT control unit - never drive the 5 V reference here
    '1R': '',            # 94-95: not the fan any more (fan relay is 1L)
    '1C': 'VIGN_IN',     # VIO: ignition switch (input only)
    '2N': 'IN_AUX2',     # heated O2 sensor (narrowband)
    '2O': 'IN_AUX3',     # MAF signal (94-95 have a MAF, not the flap meter)
    '2P': 'HARN_IAT',    # intake air thermosensor in the AFM (IAT jumper JP1 on STOCK to use it)
    '1D': '',            # data link connector
    '1F': '',            # spare analog in the stock ECU
    '1I': '',            # AT control unit
    '1K': '',            # MT only (unclear on the stock diagram)
    '1L': 'OUT_FAN',     # radiator fan relay
    '1M': 'IN_SW1',      # vehicle speed sensor
    '1N': '',            # AT control unit
    '1Q': 'IN_SW2',      # A/C pressure switch
    '1V': 'IN_SW3',      # clutch switch (MT) / AT control unit
    '2H': '',            # data link connector
    '2J': '',            # EGR function sensor
    '2L': 'IN_AUX1',     # electrical load (rear defroster) -> idle up
    '2R': 'OUT_ALT',     # pressure regulator control solenoid (generic low side)
    '2S': 'OUT_LS7',     # condenser fan relay
})


def build_parts():
    return base.build_parts(HARNESS)
